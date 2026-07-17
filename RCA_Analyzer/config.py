"""
config.py — centralised settings for RCA Analyzer
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
REPORTS_DIR = BASE_DIR / "reports"
THEMES_DIR = BASE_DIR / "themes"
SETTINGS_FILE = BASE_DIR / "settings.json"
REPORTS_DIR.mkdir(exist_ok=True)

# ── LLM providers ──────────────────────────────────────────────────────────────
LLM_PROVIDERS = {
    "OpenAI": {
        "models": ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
        "env_key": "OPENAI_API_KEY",
    },
    "Anthropic (Claude)": {
        "models": [
            "claude-opus-4-5",
            "claude-sonnet-4-5",
            "claude-3-5-sonnet-20241022",
            "claude-3-haiku-20240307",
        ],
        "env_key": "ANTHROPIC_API_KEY",
    },
    "Google Gemini": {
        "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
        "env_key": "GOOGLE_API_KEY",
    },
    "Azure OpenAI": {
        "models": ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-35-turbo"],
        "env_key": "AZURE_OPENAI_API_KEY",
    },
    "Ollama (Local)": {
        "models": ["llama3", "codellama", "mistral", "phi3", "gemma2"],
        "env_key": None,
    },
}

# ── Supported file extensions (language map) ───────────────────────────────────
LANGUAGE_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".jsx": "React JSX",
    ".tsx": "React TSX",
    ".java": "Java",
    ".cs": "C#",
    ".cpp": "C++",
    ".c": "C",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".php": "PHP",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".scala": "Scala",
    ".r": "R",
    ".m": "MATLAB/Objective-C",
    ".sh": "Shell/Bash",
    ".ps1": "PowerShell",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".json": "JSON",
    ".xml": "XML",
    ".html": "HTML",
    ".css": "CSS",
    ".sql": "SQL",
    ".tf": "Terraform",
    ".groovy": "Groovy",
    ".lua": "Lua",
    ".dart": "Dart",
    ".vue": "Vue",
    ".svelte": "Svelte",
    ".ex": "Elixir",
    ".exs": "Elixir",
    ".pl": "Perl",
    ".hs": "Haskell",
    ".fs": "F#",
    ".vb": "Visual Basic",
    ".abap": "ABAP",
    ".cob": "COBOL",
    ".f90": "Fortran",
    ".asm": "Assembly",
    ".xaml": "XAML",
    ".config": "Config",
    ".toml": "TOML",
    ".ini": "INI",
}

# ── Analysis modes ──────────────────────────────────────────────────────────────
ANALYSIS_MODES = [
    "🔍 Full Root Cause Analysis",
    "🐛 Bug & Error Detection",
    "🔒 Security Vulnerability Scan",
    "⚡ Performance Bottleneck Analysis",
    "🏗️ Code Quality & Maintainability",
    "🔗 Dependency & Coupling Analysis",
    "📊 Complexity & Metrics Report",
    "🧪 Test Coverage Gap Analysis",
    "📋 Code Review & Best Practices",
    "🚀 Migration & Upgrade Assessment",
]

# ── Default settings ────────────────────────────────────────────────────────────
DEFAULT_SETTINGS = {
    "provider": "OpenAI",
    "model": "gpt-4o",
    "api_key": "",
    "azure_endpoint": "",
    "ollama_url": "http://localhost:11434",
    "theme": "dark",
    "max_tokens": 4096,
    "temperature": 0.2,
    "report_format": "HTML",
    "auto_save_reports": True,
}


def load_settings() -> dict:
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                return {**DEFAULT_SETTINGS, **data}
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> None:
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)
