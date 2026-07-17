# 🔍 RCA Analyzer — Root Cause Analysis Tool

A professional Python desktop application for AI-powered Root Cause Analysis of source code across **40+ programming languages and technologies**.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Multi-Language Support** | Python, Java, JS/TS, C#, C/C++, Go, Rust, Ruby, PHP, Swift, Kotlin, SQL, YAML, Terraform, and 30+ more |
| **10 Analysis Modes** | Full RCA, Bug Detection, Security Scan, Performance, Code Quality, Dependency Analysis, Complexity, Test Coverage, Code Review, Migration Assessment |
| **5 AI Providers** | OpenAI (GPT-4o), Anthropic Claude, Google Gemini, Azure OpenAI, Ollama (local) |
| **Professional UI** | Dark-mode CustomTkinter desktop app with real-time results |
| **Rich Reports** | Export as HTML (interactive), JSON, or Markdown |
| **Project-Level Insights** | Holistic project summary + severity distribution across all files |
| **Code Snippets** | Annotated problematic code with line numbers and fix suggestions |

---

## 🖥️ UI Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│  🔍 RCA Analyzer  v1.0.0        🤖 OpenAI · gpt-4o    ⚙️ 📂 ❓     │
├───────────────┬─────────────────────────────────────────────────────┤
│  SOURCE INPUT │  Analysis Mode: [🔍 Full Root Cause Analysis ▼]     │
│               │  ▶ Run Analysis   ⏹ Stop         Export as: HTML   │
│  📁 Add Folder│  ─────────────────────────────────────────────────  │
│  📄 Add Files │  RESULTS           │  DETAIL VIEW                   │
│  🗑️ Clear     │                    │                                 │
│               │  [●] main.py High  │  📄 main.py                    │
│  FILES        │  [●] utils.py Med  │  Root Causes:                  │
│  ─────────    │  [●] db.py  Low    │   • Unhandled exception ...     │
│  📄 main.py   │                    │  Recommendations:              │
│  📄 utils.py  │                    │   • Add try/except ...          │
│  📄 db.py     │                    │  Code Snippets: ...             │
└───────────────┴────────────────────┴────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Install Python (3.10+)

Download from [python.org](https://python.org)

### 2. Clone or download this repo

```bash
git clone https://github.com/JalalKazi/AOCCL2UC.git
cd AOCCL2UC/RCA_Analyzer
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

---

## ⚙️ Configuration

On first launch, click **⚙️ Settings** and configure:

| Setting | Description |
|---|---|
| **AI Provider** | Choose from OpenAI, Anthropic, Gemini, Azure, or Ollama |
| **Model** | Select specific model version |
| **API Key** | Your provider API key (stored locally in `settings.json`) |
| **Max Tokens** | Response length (default: 4096) |
| **Temperature** | Creativity (0.1–0.3 recommended for analysis) |
| **Report Format** | Default export format (HTML / JSON / Markdown) |

### Environment Variables (optional)

Create a `.env` file in the `RCA_Analyzer` directory:

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
AZURE_OPENAI_API_KEY=...
```

---

## 📊 Analysis Modes

| Mode | What It Does |
|---|---|
| 🔍 Full Root Cause Analysis | Comprehensive deep-dive into all issues |
| 🐛 Bug & Error Detection | Find logical bugs, null refs, exception risks |
| 🔒 Security Vulnerability Scan | OWASP Top-10, injection, auth flaws |
| ⚡ Performance Bottleneck Analysis | Inefficiencies, N+1, memory leaks |
| 🏗️ Code Quality & Maintainability | Clean code, SOLID, readability |
| 🔗 Dependency & Coupling Analysis | Tight coupling, circular dependencies |
| 📊 Complexity & Metrics Report | Cyclomatic complexity, cognitive complexity |
| 🧪 Test Coverage Gap Analysis | Untested paths, missing assertions |
| 📋 Code Review & Best Practices | Language-specific best practices |
| 🚀 Migration & Upgrade Assessment | Deprecated APIs, upgrade risks |

---

## 📁 Project Structure

```
RCA_Analyzer/
├── app.py                  # Main UI application (CustomTkinter)
├── rca_engine.py           # AI analysis engine (all LLM providers)
├── file_utils.py           # File/folder ingestion helpers
├── report_generator.py     # HTML / JSON / Markdown report generation
├── config.py               # Settings, language map, provider config
├── requirements.txt        # Python dependencies
├── settings.json           # User settings (auto-generated)
├── reports/                # Generated reports (auto-created)
├── assets/                 # Icons and assets
└── themes/                 # Custom UI themes
```

---

## 🤖 Supported AI Providers

| Provider | Models | Notes |
|---|---|---|
| **OpenAI** | gpt-4o, gpt-4-turbo, gpt-4, gpt-3.5-turbo | Best overall quality |
| **Anthropic Claude** | claude-opus-4-5, claude-sonnet-4-5, claude-3.5-sonnet | Excellent for complex RCA |
| **Google Gemini** | gemini-1.5-pro, gemini-1.5-flash | Fast and cost-effective |
| **Azure OpenAI** | gpt-4o, gpt-4-turbo (via deployment) | Enterprise/on-prem |
| **Ollama (Local)** | llama3, codellama, mistral, phi3, gemma2 | 100% offline/private |

---

## 📄 Report Output Example

HTML reports include:
- Executive summary with overall severity rating
- Severity distribution bar chart
- Per-file deep analysis cards
- Annotated code snippets with line numbers
- Root causes and actionable recommendations
- Code metrics (complexity, security risk, maintainability)

---

## 🔒 Security & Privacy

- API keys are stored locally in `settings.json` (never uploaded)
- Use **Ollama** for fully offline, private analysis
- Source code is sent only to the configured AI provider

---

## 📦 Requirements

- Python 3.10+
- See `requirements.txt` for full list
- Internet connection (unless using Ollama)

---

## 📝 License

MIT License — see [LICENSE](../LICENSE) for details.

---

*Built for the AOCCL2UC project · Powered by IBM Bob Agent*
