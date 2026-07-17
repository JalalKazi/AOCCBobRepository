"""
rca_engine.py — AI-powered Root Cause Analysis engine for RCA Analyzer
Supports: OpenAI, Anthropic (Claude), Google Gemini, Azure OpenAI, Ollama (Local)
"""
from __future__ import annotations

import json
import re
import textwrap
import threading
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from config import LLM_PROVIDERS, ANALYSIS_MODES


# ── Data models ─────────────────────────────────────────────────────────────────

@dataclass
class AnalysisResult:
    file_path: str
    language: str
    mode: str
    summary: str = ""
    root_causes: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    severity: str = "Medium"       # Low / Medium / High / Critical
    confidence: str = "Moderate"   # Low / Moderate / High
    code_snippets: List[dict] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    raw_response: str = ""
    error: Optional[str] = None


@dataclass
class ProjectAnalysis:
    mode: str
    provider: str
    model: str
    file_results: List[AnalysisResult] = field(default_factory=list)
    project_summary: str = ""
    overall_severity: str = "Medium"
    top_issues: List[str] = field(default_factory=list)
    total_files: int = 0
    analysed_files: int = 0


# ── Prompt builder ───────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert senior software engineer and root cause analyst with deep
knowledge across all programming languages, frameworks, and architectures. Your task is to
perform a detailed, structured analysis of the provided source code.

Always respond in valid JSON using this exact schema:
{
  "summary": "2-3 sentence executive summary",
  "severity": "Low|Medium|High|Critical",
  "confidence": "Low|Moderate|High",
  "root_causes": ["cause 1", "cause 2", ...],
  "recommendations": ["fix 1", "fix 2", ...],
  "code_snippets": [
    {"line": <int or null>, "snippet": "...", "issue": "...", "fix": "..."}
  ],
  "metrics": {
    "complexity": "Low|Medium|High",
    "maintainability": "Low|Medium|High",
    "security_risk": "Low|Medium|High",
    "test_coverage_estimate": "None|Poor|Moderate|Good"
  }
}
Provide only the JSON object — no markdown fences, no additional text."""


def _build_user_prompt(mode: str, language: str, filename: str, code: str) -> str:
    mode_label = mode.split(" ", 1)[-1]  # strip emoji

    # Truncate very large files to ~12 000 chars
    if len(code) > 12000:
        code = code[:12000] + "\n\n... [truncated for analysis] ..."

    return textwrap.dedent(f"""\
        Analysis Mode : {mode_label}
        Language      : {language}
        File          : {filename}

        === SOURCE CODE ===
        {code}
        ==================

        Perform a comprehensive {mode_label} on the code above.
        Identify root causes, list concrete actionable recommendations,
        and annotate relevant code snippets with line numbers where possible.
    """)


def _build_project_summary_prompt(results: List[AnalysisResult], mode: str) -> str:
    issues_text = "\n".join(
        f"- [{r.severity}] {r.file_path}: {r.summary}" for r in results if not r.error
    )
    return textwrap.dedent(f"""\
        You have just analysed {len(results)} source files for mode: {mode}.
        Here are the per-file summaries:

        {issues_text}

        Now provide a project-level root cause analysis summary in JSON:
        {{
          "project_summary": "3-4 sentence holistic summary",
          "overall_severity": "Low|Medium|High|Critical",
          "top_issues": ["issue 1", "issue 2", "issue 3", ...]
        }}
        Return only the JSON object.
    """)


# ── LLM client factory ───────────────────────────────────────────────────────────

def _call_openai(api_key: str, model: str, system: str, user: str, max_tokens: int, temperature: float) -> str:
    import openai
    client = openai.OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message.content


def _call_azure_openai(api_key: str, endpoint: str, model: str, system: str, user: str, max_tokens: int, temperature: float) -> str:
    import openai
    client = openai.AzureOpenAI(
        api_key=api_key,
        azure_endpoint=endpoint,
        api_version="2024-02-01",
    )
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message.content


def _call_anthropic(api_key: str, model: str, system: str, user: str, max_tokens: int, temperature: float) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return msg.content[0].text


def _call_gemini(api_key: str, model: str, system: str, user: str, max_tokens: int, temperature: float) -> str:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    gmodel = genai.GenerativeModel(
        model_name=model,
        system_instruction=system,
        generation_config=genai.GenerationConfig(
            max_output_tokens=max_tokens, temperature=temperature
        ),
    )
    resp = gmodel.generate_content(user)
    return resp.text


def _call_ollama(url: str, model: str, system: str, user: str, max_tokens: int, temperature: float) -> str:
    import requests
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "options": {"num_predict": max_tokens, "temperature": temperature},
    }
    resp = requests.post(f"{url}/api/chat", json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["message"]["content"]


def _dispatch_llm(settings: dict, system: str, user: str) -> str:
    provider = settings.get("provider", "OpenAI")
    model = settings.get("model", "gpt-4o")
    api_key = settings.get("api_key", "")
    max_tokens = int(settings.get("max_tokens", 4096))
    temperature = float(settings.get("temperature", 0.2))

    if provider == "OpenAI":
        return _call_openai(api_key, model, system, user, max_tokens, temperature)
    elif provider == "Anthropic (Claude)":
        return _call_anthropic(api_key, model, system, user, max_tokens, temperature)
    elif provider == "Google Gemini":
        return _call_gemini(api_key, model, system, user, max_tokens, temperature)
    elif provider == "Azure OpenAI":
        endpoint = settings.get("azure_endpoint", "")
        return _call_azure_openai(api_key, endpoint, model, system, user, max_tokens, temperature)
    elif provider == "Ollama (Local)":
        url = settings.get("ollama_url", "http://localhost:11434")
        return _call_ollama(url, model, system, user, max_tokens, temperature)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def _parse_json_response(raw: str) -> dict:
    """Extract and parse a JSON object from the LLM response."""
    # Strip markdown fences if present
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip(), flags=re.MULTILINE)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to find JSON object within the text
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            return json.loads(match.group())
        raise ValueError(f"Could not parse JSON from response:\n{raw[:500]}")


# ── Main analysis function ───────────────────────────────────────────────────────

def analyse_file(
    file_info: dict,
    mode: str,
    settings: dict,
    on_progress: Optional[Callable[[str], None]] = None,
) -> AnalysisResult:
    """Analyse a single file and return an AnalysisResult."""
    path = file_info.get("path", "unknown")
    language = file_info.get("language", "Unknown")
    content = file_info.get("content")

    result = AnalysisResult(file_path=path, language=language, mode=mode)

    if not content:
        result.error = file_info.get("error", "No content available.")
        return result

    if on_progress:
        on_progress(f"Analysing: {path}")

    try:
        user_prompt = _build_user_prompt(mode, language, path, content)
        raw = _dispatch_llm(settings, SYSTEM_PROMPT, user_prompt)
        result.raw_response = raw

        parsed = _parse_json_response(raw)
        result.summary = parsed.get("summary", "")
        result.severity = parsed.get("severity", "Medium")
        result.confidence = parsed.get("confidence", "Moderate")
        result.root_causes = parsed.get("root_causes", [])
        result.recommendations = parsed.get("recommendations", [])
        result.code_snippets = parsed.get("code_snippets", [])
        result.metrics = parsed.get("metrics", {})

    except Exception as e:
        result.error = str(e)

    return result


def analyse_project(
    files: list,
    mode: str,
    settings: dict,
    on_progress: Optional[Callable[[str], None]] = None,
    on_file_done: Optional[Callable[[AnalysisResult, int, int], None]] = None,
) -> ProjectAnalysis:
    """
    Analyse multiple files and produce a project-level report.
    Designed to run in a background thread.
    """
    project = ProjectAnalysis(
        mode=mode,
        provider=settings.get("provider", ""),
        model=settings.get("model", ""),
        total_files=len(files),
    )

    for idx, file_info in enumerate(files):
        result = analyse_file(file_info, mode, settings, on_progress)
        project.file_results.append(result)
        project.analysed_files += 1

        if on_file_done:
            on_file_done(result, idx + 1, len(files))

    # Project-level summary (if more than 1 file)
    if len(project.file_results) > 1:
        if on_progress:
            on_progress("Generating project-level summary…")
        try:
            summary_prompt = _build_project_summary_prompt(project.file_results, mode)
            raw = _dispatch_llm(settings, SYSTEM_PROMPT, summary_prompt)
            parsed = _parse_json_response(raw)
            project.project_summary = parsed.get("project_summary", "")
            project.overall_severity = parsed.get("overall_severity", "Medium")
            project.top_issues = parsed.get("top_issues", [])
        except Exception as e:
            project.project_summary = f"Project summary failed: {e}"

    elif project.file_results:
        single = project.file_results[0]
        project.project_summary = single.summary
        project.overall_severity = single.severity
        project.top_issues = single.root_causes[:5]

    return project


def run_analysis_async(
    files: list,
    mode: str,
    settings: dict,
    on_progress: Callable[[str], None],
    on_file_done: Callable[[AnalysisResult, int, int], None],
    on_complete: Callable[[ProjectAnalysis], None],
    on_error: Callable[[str], None],
) -> threading.Thread:
    """Launch analysis in a background thread and return the thread handle."""

    def _worker():
        try:
            result = analyse_project(files, mode, settings, on_progress, on_file_done)
            on_complete(result)
        except Exception as e:
            on_error(str(e))

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    return t
