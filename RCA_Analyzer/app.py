"""
app.py — Root Cause Analyzer  ·  Professional Desktop UI
Built with CustomTkinter · Supports OpenAI / Claude / Gemini / Azure / Ollama
"""
from __future__ import annotations

import os
import sys
import threading
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox
import tkinter as tk

import customtkinter as ctk
from PIL import Image, ImageTk

from config import (
    ANALYSIS_MODES,
    LANGUAGE_EXTENSIONS,
    LLM_PROVIDERS,
    REPORTS_DIR,
    load_settings,
    save_settings,
)
from file_utils import (
    collect_files_from_folder,
    collect_files_from_paths,
    format_size,
    summarise_files,
)
from rca_engine import AnalysisResult, ProjectAnalysis, run_analysis_async
from report_generator import generate_report

# ── App-wide appearance ──────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_VERSION = "1.0.0"
APP_NAME = "RCA Analyzer"

# ── Severity colours ─────────────────────────────────────────────────────────────
SEV_COLORS = {
    "Low": "#22c55e",
    "Medium": "#f59e0b",
    "High": "#f97316",
    "Critical": "#ef4444",
    "Error": "#ef4444",
}


# ═══════════════════════════════════════════════════════════════════════════════
#  Settings Dialog
# ═══════════════════════════════════════════════════════════════════════════════

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent: "App", settings: dict):
        super().__init__(parent)
        self.parent_app = parent
        self.settings = settings.copy()

        self.title("⚙️  Settings — RCA Analyzer")
        self.geometry("580x640")
        self.resizable(False, False)
        self.grab_set()
        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 20, "pady": 8}

        # Title
        ctk.CTkLabel(self, text="⚙️  Configuration", font=ctk.CTkFont(size=20, weight="bold")).pack(**pad, anchor="w", pady=(20, 4))
        ctk.CTkLabel(self, text="Configure AI provider, model, and output preferences.", text_color="#94a3b8").pack(**pad, anchor="w", pady=(0, 10))

        # ── Provider ─────────────────────────────────────────────────────────────
        ctk.CTkLabel(self, text="AI Provider", font=ctk.CTkFont(weight="bold")).pack(**pad, anchor="w", pady=(10, 0))
        self.provider_var = ctk.StringVar(value=self.settings.get("provider", "OpenAI"))
        self.provider_menu = ctk.CTkOptionMenu(
            self,
            variable=self.provider_var,
            values=list(LLM_PROVIDERS.keys()),
            width=380,
            command=self._on_provider_change,
        )
        self.provider_menu.pack(**pad, anchor="w")

        # ── Model ─────────────────────────────────────────────────────────────────
        ctk.CTkLabel(self, text="Model", font=ctk.CTkFont(weight="bold")).pack(**pad, anchor="w", pady=(10, 0))
        provider_key = self.settings.get("provider", "OpenAI")
        models = LLM_PROVIDERS.get(provider_key, {}).get("models", ["gpt-4o"])
        self.model_var = ctk.StringVar(value=self.settings.get("model", models[0]))
        self.model_menu = ctk.CTkOptionMenu(self, variable=self.model_var, values=models, width=380)
        self.model_menu.pack(**pad, anchor="w")

        # ── API Key ───────────────────────────────────────────────────────────────
        ctk.CTkLabel(self, text="API Key", font=ctk.CTkFont(weight="bold")).pack(**pad, anchor="w", pady=(10, 0))
        self.api_key_entry = ctk.CTkEntry(self, width=380, show="•", placeholder_text="sk-...")
        self.api_key_entry.pack(**pad, anchor="w")
        if self.settings.get("api_key"):
            self.api_key_entry.insert(0, self.settings["api_key"])

        # ── Azure endpoint (conditional) ──────────────────────────────────────────
        self.azure_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctk.CTkLabel(self.azure_frame, text="Azure Endpoint", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.azure_entry = ctk.CTkEntry(self.azure_frame, width=380, placeholder_text="https://<your-resource>.openai.azure.com/")
        self.azure_entry.pack()
        if self.settings.get("azure_endpoint"):
            self.azure_entry.insert(0, self.settings["azure_endpoint"])

        # ── Ollama URL (conditional) ──────────────────────────────────────────────
        self.ollama_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctk.CTkLabel(self.ollama_frame, text="Ollama URL", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.ollama_entry = ctk.CTkEntry(self.ollama_frame, width=380, placeholder_text="http://localhost:11434")
        self.ollama_entry.pack()
        if self.settings.get("ollama_url"):
            self.ollama_entry.insert(0, self.settings["ollama_url"])

        self._on_provider_change(provider_key)

        # ── Max tokens ────────────────────────────────────────────────────────────
        ctk.CTkLabel(self, text="Max Tokens", font=ctk.CTkFont(weight="bold")).pack(**pad, anchor="w", pady=(10, 0))
        self.tokens_var = ctk.StringVar(value=str(self.settings.get("max_tokens", 4096)))
        ctk.CTkEntry(self, textvariable=self.tokens_var, width=160).pack(**pad, anchor="w")

        # ── Temperature ───────────────────────────────────────────────────────────
        ctk.CTkLabel(self, text=f"Temperature: {self.settings.get('temperature', 0.2)}", font=ctk.CTkFont(weight="bold")).pack(**pad, anchor="w", pady=(10, 0))
        self.temp_label = self.winfo_children()[-1]
        self.temp_slider = ctk.CTkSlider(self, from_=0, to=1.0, number_of_steps=20, width=380,
                                          command=lambda v: self.temp_label.configure(text=f"Temperature: {v:.2f}"))
        self.temp_slider.set(float(self.settings.get("temperature", 0.2)))
        self.temp_slider.pack(**pad, anchor="w")

        # ── Report format ─────────────────────────────────────────────────────────
        ctk.CTkLabel(self, text="Default Report Format", font=ctk.CTkFont(weight="bold")).pack(**pad, anchor="w", pady=(10, 0))
        self.fmt_var = ctk.StringVar(value=self.settings.get("report_format", "HTML"))
        ctk.CTkOptionMenu(self, variable=self.fmt_var, values=["HTML", "JSON", "Markdown"], width=200).pack(**pad, anchor="w")

        # ── Buttons ───────────────────────────────────────────────────────────────
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)
        ctk.CTkButton(btn_frame, text="💾 Save Settings", command=self._save, width=180).pack(side="right", padx=4)
        ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy, fg_color="transparent",
                      border_width=1, width=100).pack(side="right", padx=4)

    def _on_provider_change(self, provider: str):
        models = LLM_PROVIDERS.get(provider, {}).get("models", [])
        self.model_menu.configure(values=models)
        if models:
            self.model_var.set(models[0])

        if provider == "Azure OpenAI":
            self.azure_frame.pack(padx=20, pady=8, anchor="w")
        else:
            self.azure_frame.pack_forget()

        if provider == "Ollama (Local)":
            self.ollama_frame.pack(padx=20, pady=8, anchor="w")
        else:
            self.ollama_frame.pack_forget()

    def _save(self):
        self.settings["provider"] = self.provider_var.get()
        self.settings["model"] = self.model_var.get()
        self.settings["api_key"] = self.api_key_entry.get()
        self.settings["azure_endpoint"] = self.azure_entry.get()
        self.settings["ollama_url"] = self.ollama_entry.get()
        self.settings["max_tokens"] = int(self.tokens_var.get() or 4096)
        self.settings["temperature"] = round(self.temp_slider.get(), 2)
        self.settings["report_format"] = self.fmt_var.get()
        save_settings(self.settings)
        self.parent_app.settings = self.settings
        self.parent_app.update_provider_label()
        self.destroy()


# ═══════════════════════════════════════════════════════════════════════════════
#  Result Detail Panel (right-side scrollable)
# ═══════════════════════════════════════════════════════════════════════════════

class ResultDetailView(ctk.CTkScrollableFrame):
    """Renders a single AnalysisResult or the project-level summary."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._placeholder()

    def _placeholder(self):
        for w in self.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self,
            text="📋  Select a file from the list\nto view its analysis.",
            font=ctk.CTkFont(size=14),
            text_color="#64748b",
            justify="center",
        ).pack(expand=True, pady=80)

    def show_result(self, result: AnalysisResult):
        for w in self.winfo_children():
            w.destroy()

        # ── File header ──────────────────────────────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color="#1e3a5f", corner_radius=8)
        hdr.pack(fill="x", padx=4, pady=(4, 10))
        ctk.CTkLabel(hdr, text=f"📄  {result.file_path}", font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#93c5fd").pack(anchor="w", padx=14, pady=(10, 2))
        ctk.CTkLabel(hdr, text=f"Language: {result.language}  ·  Severity: {result.severity}  ·  Confidence: {result.confidence}",
                     text_color="#94a3b8", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=14, pady=(0, 10))

        if result.error:
            self._section("❌ Error", [result.error], "#ef4444")
            return

        # ── Summary ──────────────────────────────────────────────────────────────
        self._text_block("📝 Summary", result.summary)

        # ── Root causes ──────────────────────────────────────────────────────────
        if result.root_causes:
            self._section("🔴 Root Causes", result.root_causes, "#f87171")

        # ── Recommendations ──────────────────────────────────────────────────────
        if result.recommendations:
            self._section("✅ Recommendations", result.recommendations, "#4ade80")

        # ── Metrics ──────────────────────────────────────────────────────────────
        if result.metrics:
            self._metrics_grid(result.metrics)

        # ── Code snippets ────────────────────────────────────────────────────────
        if result.code_snippets:
            self._snippet_section(result.code_snippets)

    def show_project_summary(self, project: ProjectAnalysis):
        for w in self.winfo_children():
            w.destroy()

        hdr = ctk.CTkFrame(self, fg_color="#1e3a5f", corner_radius=8)
        hdr.pack(fill="x", padx=4, pady=(4, 10))
        ctk.CTkLabel(hdr, text="🗂️  Project-Level Summary",
                     font=ctk.CTkFont(size=16, weight="bold"), text_color="#93c5fd").pack(anchor="w", padx=14, pady=(10, 2))
        ctk.CTkLabel(hdr, text=f"Mode: {project.mode}  ·  {project.analysed_files} files analysed",
                     text_color="#94a3b8", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=14, pady=(0, 10))

        self._text_block("📊 Executive Summary", project.project_summary)
        if project.top_issues:
            self._section("⚠️ Top Issues", project.top_issues, "#fbbf24")

        # Severity summary
        sev_counts: dict = {}
        for r in project.file_results:
            sev_counts[r.severity] = sev_counts.get(r.severity, 0) + 1
        if sev_counts:
            self._metrics_grid(sev_counts, label_prefix="Severity")

    # ── helpers ──────────────────────────────────────────────────────────────────

    def _text_block(self, title: str, text: str):
        ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#e2e8f0").pack(anchor="w", padx=8, pady=(10, 2))
        box = ctk.CTkTextbox(self, height=80, wrap="word", fg_color="#0f172a",
                              text_color="#94a3b8", font=ctk.CTkFont(size=12))
        box.pack(fill="x", padx=8, pady=(0, 6))
        box.insert("1.0", text or "N/A")
        box.configure(state="disabled")

    def _section(self, title: str, items: list, bullet_color: str = "#60a5fa"):
        ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#e2e8f0").pack(anchor="w", padx=8, pady=(10, 4))
        for item in items:
            row = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=4)
            row.pack(fill="x", padx=8, pady=2)
            ctk.CTkLabel(row, text="●", text_color=bullet_color, width=20).pack(side="left", padx=(8, 4), pady=6)
            ctk.CTkLabel(row, text=str(item), wraplength=420, justify="left",
                         text_color="#cbd5e1", font=ctk.CTkFont(size=12)).pack(side="left", padx=4, pady=6)

    def _metrics_grid(self, metrics: dict, label_prefix: str = ""):
        ctk.CTkLabel(self, text="📊 Metrics", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#e2e8f0").pack(anchor="w", padx=8, pady=(10, 4))
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", padx=8)
        col = 0
        for k, v in metrics.items():
            label = f"{label_prefix} {k}".strip().replace("_", " ").title()
            chip = ctk.CTkFrame(grid, fg_color="#0f172a", corner_radius=6, border_width=1, border_color="#334155")
            chip.grid(row=0, column=col, padx=4, pady=4, sticky="w")
            ctk.CTkLabel(chip, text=label, font=ctk.CTkFont(size=10), text_color="#64748b").pack(padx=10, pady=(6, 0))
            ctk.CTkLabel(chip, text=str(v), font=ctk.CTkFont(size=13, weight="bold"),
                         text_color="#e2e8f0").pack(padx=10, pady=(0, 6))
            col += 1

    def _snippet_section(self, snippets: list):
        ctk.CTkLabel(self, text="🔎 Code Snippets", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#e2e8f0").pack(anchor="w", padx=8, pady=(10, 4))
        for s in snippets:
            frame = ctk.CTkFrame(self, fg_color="#0f172a", corner_radius=6,
                                  border_width=1, border_color="#1d4ed8")
            frame.pack(fill="x", padx=8, pady=4)
            line_info = f"Line {s.get('line')}" if s.get("line") else ""
            meta = f"{line_info}  {s.get('issue', '')}".strip()
            ctk.CTkLabel(frame, text=meta, font=ctk.CTkFont(size=11), text_color="#94a3b8").pack(anchor="w", padx=10, pady=(8, 2))
            tb = ctk.CTkTextbox(frame, height=70, wrap="none", fg_color="#020817",
                                 text_color="#86efac", font=ctk.CTkFont(family="Cascadia Code", size=11))
            tb.pack(fill="x", padx=10, pady=2)
            tb.insert("1.0", s.get("snippet", ""))
            tb.configure(state="disabled")
            if s.get("fix"):
                ctk.CTkLabel(frame, text=f"💡 {s['fix']}", text_color="#fbbf24",
                              font=ctk.CTkFont(size=11), wraplength=420, justify="left").pack(anchor="w", padx=10, pady=(2, 8))


# ═══════════════════════════════════════════════════════════════════════════════
#  Main Application
# ═══════════════════════════════════════════════════════════════════════════════

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self._loaded_files: list = []
        self._analysis_result: ProjectAnalysis | None = None
        self._analysis_thread: threading.Thread | None = None
        self._is_running = False

        self.title(f"🔍  {APP_NAME}  v{APP_VERSION}")
        self.geometry("1280x800")
        self.minsize(1000, 680)

        self._build_layout()
        self.update_provider_label()

    # ── Layout ───────────────────────────────────────────────────────────────────

    def _build_layout(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_topbar()
        self._build_main()
        self._build_statusbar()

    def _build_topbar(self):
        bar = ctk.CTkFrame(self, height=56, corner_radius=0, fg_color="#0f1729")
        bar.grid(row=0, column=0, sticky="ew")
        bar.grid_propagate(False)
        bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(bar, text="🔍  RCA Analyzer",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#60a5fa").grid(row=0, column=0, padx=20, pady=14)

        # Provider info
        self.provider_lbl = ctk.CTkLabel(bar, text="", text_color="#64748b",
                                          font=ctk.CTkFont(size=12))
        self.provider_lbl.grid(row=0, column=1, padx=10, sticky="w")

        btn_frame = ctk.CTkFrame(bar, fg_color="transparent")
        btn_frame.grid(row=0, column=2, padx=16, pady=10)

        ctk.CTkButton(btn_frame, text="⚙️  Settings", width=110, height=32,
                      command=self._open_settings).pack(side="left", padx=4)
        ctk.CTkButton(btn_frame, text="📂  Reports", width=110, height=32,
                      fg_color="#1e3a5f", hover_color="#1e40af",
                      command=self._open_reports_folder).pack(side="left", padx=4)
        ctk.CTkButton(btn_frame, text="❓  Help", width=80, height=32,
                      fg_color="transparent", border_width=1,
                      command=self._show_help).pack(side="left", padx=4)

    def _build_main(self):
        main = ctk.CTkFrame(self, corner_radius=0, fg_color="#0d1117")
        main.grid(row=1, column=0, sticky="nsew")
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=1)

        # ── Left sidebar ──────────────────────────────────────────────────────────
        sidebar = ctk.CTkFrame(main, width=300, fg_color="#161b27", corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(sidebar, text="SOURCE INPUT", font=ctk.CTkFont(size=10, weight="bold"),
                     text_color="#475569").grid(row=0, column=0, padx=16, pady=(16, 4), sticky="w")

        # Input buttons
        btn_cfg = {"width": 268, "height": 38, "corner_radius": 6}
        ctk.CTkButton(sidebar, text="📁  Add Folder", **btn_cfg,
                      command=self._add_folder).grid(row=1, column=0, padx=16, pady=4)
        ctk.CTkButton(sidebar, text="📄  Add Files", **btn_cfg,
                      fg_color="#1e3a5f", hover_color="#1e40af",
                      command=self._add_files).grid(row=2, column=0, padx=16, pady=4)
        ctk.CTkButton(sidebar, text="🗑️  Clear All", **btn_cfg,
                      fg_color="#2d1515", hover_color="#7f1d1d", text_color="#f87171",
                      command=self._clear_files).grid(row=3, column=0, padx=16, pady=4)

        # Stats
        self.stats_lbl = ctk.CTkLabel(sidebar, text="No files loaded.",
                                       text_color="#64748b", font=ctk.CTkFont(size=11),
                                       wraplength=260, justify="left")
        self.stats_lbl.grid(row=4, column=0, padx=16, pady=6, sticky="w")

        # File list
        ctk.CTkLabel(sidebar, text="FILES", font=ctk.CTkFont(size=10, weight="bold"),
                     text_color="#475569").grid(row=5, column=0, padx=16, pady=(8, 2), sticky="sw")

        self.file_listbox = ctk.CTkScrollableFrame(sidebar, fg_color="#0d1117", corner_radius=4)
        self.file_listbox.grid(row=6, column=0, sticky="nsew", padx=8, pady=(0, 8))
        sidebar.grid_rowconfigure(6, weight=1)

        # ── Centre panel (analysis controls + progress) ────────────────────────────
        centre = ctk.CTkFrame(main, fg_color="#0d1117", corner_radius=0)
        centre.grid(row=0, column=1, sticky="nsew", padx=(1, 0))
        centre.grid_rowconfigure(3, weight=1)
        centre.grid_columnconfigure(0, weight=1)

        # Analysis controls strip
        ctrl = ctk.CTkFrame(centre, fg_color="#161b27", corner_radius=8)
        ctrl.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        ctrl.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(ctrl, text="Analysis Mode", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#94a3b8").grid(row=0, column=0, padx=16, pady=(12, 2), sticky="w")

        self.mode_var = ctk.StringVar(value=ANALYSIS_MODES[0])
        mode_menu = ctk.CTkOptionMenu(ctrl, variable=self.mode_var, values=ANALYSIS_MODES,
                                       width=340, height=36, font=ctk.CTkFont(size=13))
        mode_menu.grid(row=1, column=0, padx=16, pady=(0, 12), sticky="w")

        self.run_btn = ctk.CTkButton(
            ctrl,
            text="▶  Run Analysis",
            width=170,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#1d4ed8",
            hover_color="#2563eb",
            command=self._run_analysis,
        )
        self.run_btn.grid(row=0, column=2, rowspan=2, padx=16, pady=12)

        self.stop_btn = ctk.CTkButton(
            ctrl,
            text="⏹  Stop",
            width=100,
            height=40,
            fg_color="#7f1d1d",
            hover_color="#991b1b",
            text_color="#f87171",
            command=self._stop_analysis,
        )
        self.stop_btn.grid(row=0, column=3, rowspan=2, padx=(0, 16), pady=12)
        self.stop_btn.configure(state="disabled")

        # Report format + export
        fmt_frame = ctk.CTkFrame(ctrl, fg_color="transparent")
        fmt_frame.grid(row=0, column=1, rowspan=2, padx=8, pady=12, sticky="e")
        ctk.CTkLabel(fmt_frame, text="Export as:", text_color="#64748b",
                     font=ctk.CTkFont(size=11)).pack(anchor="w")
        self.fmt_var = ctk.StringVar(value=self.settings.get("report_format", "HTML"))
        ctk.CTkOptionMenu(fmt_frame, variable=self.fmt_var,
                          values=["HTML", "JSON", "Markdown"], width=130).pack()

        # Progress
        prog_frame = ctk.CTkFrame(centre, fg_color="transparent")
        prog_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=4)
        self.progress = ctk.CTkProgressBar(prog_frame, mode="indeterminate", height=4)
        self.progress.pack(fill="x")
        self.progress.set(0)
        self.progress.stop()

        self.progress_lbl = ctk.CTkLabel(prog_frame, text="", text_color="#64748b",
                                          font=ctk.CTkFont(size=11))
        self.progress_lbl.pack(anchor="w", pady=2)

        # ── Split: results list + detail view ─────────────────────────────────────
        split = ctk.CTkFrame(centre, fg_color="transparent")
        split.grid(row=3, column=0, sticky="nsew", padx=16, pady=8)
        split.grid_rowconfigure(0, weight=1)
        split.grid_columnconfigure(0, weight=0)
        split.grid_columnconfigure(1, weight=1)

        # Results list (left of split)
        results_panel = ctk.CTkFrame(split, fg_color="#161b27", corner_radius=8, width=260)
        results_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        results_panel.grid_propagate(False)
        results_panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(results_panel, text="RESULTS", font=ctk.CTkFont(size=10, weight="bold"),
                     text_color="#475569").grid(row=0, column=0, padx=12, pady=(10, 4), sticky="w")

        self.result_list = ctk.CTkScrollableFrame(results_panel, fg_color="transparent")
        self.result_list.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
        results_panel.grid_columnconfigure(0, weight=1)

        # Placeholder
        self._result_placeholder = ctk.CTkLabel(
            self.result_list,
            text="Results will appear\nafter analysis.",
            text_color="#475569",
            font=ctk.CTkFont(size=12),
            justify="center",
        )
        self._result_placeholder.pack(pady=40)

        # Detail view (right of split)
        self.detail_view = ResultDetailView(split, fg_color="#161b27", corner_radius=8)
        self.detail_view.grid(row=0, column=1, sticky="nsew")

        # Export button
        export_row = ctk.CTkFrame(centre, fg_color="transparent")
        export_row.grid(row=4, column=0, sticky="ew", padx=16, pady=(0, 12))
        self.export_btn = ctk.CTkButton(
            export_row,
            text="💾  Export Report",
            width=160,
            state="disabled",
            fg_color="#065f46",
            hover_color="#047857",
            command=self._export_report,
        )
        self.export_btn.pack(side="right")

        self.project_summary_btn = ctk.CTkButton(
            export_row,
            text="🗂️  Project Summary",
            width=160,
            state="disabled",
            fg_color="#1e3a5f",
            hover_color="#1e40af",
            command=self._show_project_summary,
        )
        self.project_summary_btn.pack(side="right", padx=8)

    def _build_statusbar(self):
        bar = ctk.CTkFrame(self, height=28, corner_radius=0, fg_color="#0a0f1a")
        bar.grid(row=2, column=0, sticky="ew")
        self.status_lbl = ctk.CTkLabel(bar, text="Ready.", text_color="#475569",
                                        font=ctk.CTkFont(size=11))
        self.status_lbl.pack(side="left", padx=14, pady=4)
        ctk.CTkLabel(bar, text=f"RCA Analyzer v{APP_VERSION}  ·  AOCCL2UC",
                     text_color="#334155", font=ctk.CTkFont(size=10)).pack(side="right", padx=14)

    # ── File loading ─────────────────────────────────────────────────────────────

    def _add_folder(self):
        folder = filedialog.askdirectory(title="Select Source Code Folder")
        if not folder:
            return
        self._set_status("Scanning folder…")
        files = collect_files_from_folder(folder)
        if not files:
            messagebox.showinfo("No Files", "No supported source files found in that folder.")
            self._set_status("Ready.")
            return
        self._loaded_files.extend(files)
        self._refresh_file_list()

    def _add_files(self):
        exts = " ".join(f"*{e}" for e in LANGUAGE_EXTENSIONS.keys())
        paths = filedialog.askopenfilenames(
            title="Select Source Files",
            filetypes=[("Source Files", exts), ("All Files", "*.*")],
        )
        if not paths:
            return
        new_files = collect_files_from_paths(list(paths))
        self._loaded_files.extend(new_files)
        self._refresh_file_list()

    def _clear_files(self):
        self._loaded_files = []
        self._refresh_file_list()
        self.detail_view._placeholder()
        self._clear_result_list()
        self._analysis_result = None
        self.export_btn.configure(state="disabled")
        self.project_summary_btn.configure(state="disabled")
        self._set_status("Cleared.")

    def _refresh_file_list(self):
        for w in self.file_listbox.winfo_children():
            w.destroy()

        stats = summarise_files(self._loaded_files)
        lang_text = ", ".join(f"{l}({c})" for l, c in list(stats["languages"].items())[:4])
        self.stats_lbl.configure(
            text=f"{stats['total_files']} files · {stats['total_lines']:,} lines\n{lang_text}"
        )

        for f in self._loaded_files:
            row = ctk.CTkFrame(self.file_listbox, fg_color="#1e293b", corner_radius=4)
            row.pack(fill="x", padx=2, pady=1)
            icon = "⚠️" if f.get("error") else "📄"
            ctk.CTkLabel(row, text=icon, width=20, font=ctk.CTkFont(size=11)).pack(side="left", padx=(6, 2), pady=4)
            ctk.CTkLabel(row, text=f["path"], font=ctk.CTkFont(size=10),
                         text_color="#94a3b8", anchor="w").pack(side="left", padx=2, pady=4, fill="x", expand=True)
            ctk.CTkLabel(row, text=format_size(f["size"]), font=ctk.CTkFont(size=9),
                         text_color="#475569").pack(side="right", padx=6, pady=4)

        self._set_status(f"{len(self._loaded_files)} file(s) loaded.")

    # ── Analysis ─────────────────────────────────────────────────────────────────

    def _run_analysis(self):
        if not self._loaded_files:
            messagebox.showwarning("No Files", "Please load source files or a folder first.")
            return

        if not self.settings.get("api_key") and self.settings.get("provider") not in ("Ollama (Local)",):
            if not messagebox.askyesno("No API Key", "No API key is configured. Open Settings now?"):
                return
            self._open_settings()
            return

        self._is_running = True
        self.run_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.export_btn.configure(state="disabled")
        self.project_summary_btn.configure(state="disabled")
        self._clear_result_list()
        self.detail_view._placeholder()
        self.progress.start()

        mode = self.mode_var.get()
        self._set_status(f"Running: {mode}…")

        self._analysis_thread = run_analysis_async(
            files=self._loaded_files,
            mode=mode,
            settings=self.settings,
            on_progress=self._on_progress,
            on_file_done=self._on_file_done,
            on_complete=self._on_complete,
            on_error=self._on_error,
        )

    def _stop_analysis(self):
        self._is_running = False
        self._set_status("Stopping… (current file will finish)")

    def _on_progress(self, msg: str):
        self.after(0, lambda: self._set_status(msg))
        self.after(0, lambda: self.progress_lbl.configure(text=msg))

    def _on_file_done(self, result: AnalysisResult, done: int, total: int):
        self.after(0, lambda r=result, d=done, t=total: self._add_result_row(r, d, t))

    def _on_complete(self, project: ProjectAnalysis):
        self._analysis_result = project
        self.after(0, self._analysis_finished)

    def _on_error(self, err: str):
        self.after(0, lambda: messagebox.showerror("Analysis Error", err))
        self.after(0, self._analysis_finished)

    def _analysis_finished(self):
        self._is_running = False
        self.progress.stop()
        self.progress.set(1)
        self.run_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        if self._analysis_result:
            done = self._analysis_result.analysed_files
            total = self._analysis_result.total_files
            self._set_status(f"✅  Analysis complete — {done}/{total} files processed.")
            self.export_btn.configure(state="normal")
            if total > 1:
                self.project_summary_btn.configure(state="normal")
        else:
            self._set_status("Analysis stopped.")

    # ── Result list ──────────────────────────────────────────────────────────────

    def _clear_result_list(self):
        for w in self.result_list.winfo_children():
            w.destroy()

    def _add_result_row(self, result: AnalysisResult, done: int, total: int):
        self._result_placeholder.pack_forget()
        row = ctk.CTkFrame(self.result_list, fg_color="#1e293b", corner_radius=4, cursor="hand2")
        row.pack(fill="x", padx=2, pady=2)

        sev = result.severity if not result.error else "Error"
        color = SEV_COLORS.get(sev, "#94a3b8")

        indicator = ctk.CTkFrame(row, width=4, fg_color=color, corner_radius=0)
        indicator.pack(side="left", fill="y")

        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(side="left", fill="x", expand=True, padx=8, pady=6)

        fname = Path(result.file_path).name
        ctk.CTkLabel(inner, text=fname, font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#e2e8f0", anchor="w").pack(fill="x")
        ctk.CTkLabel(inner, text=f"{result.language}  ·  {sev}", font=ctk.CTkFont(size=10),
                     text_color="#64748b", anchor="w").pack(fill="x")

        # Click to show detail
        def _show(e, r=result):
            self.detail_view.show_result(r)

        row.bind("<Button-1>", _show)
        for child in row.winfo_children():
            child.bind("<Button-1>", _show)
            for grandchild in child.winfo_children():
                grandchild.bind("<Button-1>", _show)

        self.progress_lbl.configure(text=f"Processed {done}/{total}: {result.file_path}")

    def _show_project_summary(self):
        if self._analysis_result:
            self.detail_view.show_project_summary(self._analysis_result)

    # ── Export ────────────────────────────────────────────────────────────────────

    def _export_report(self):
        if not self._analysis_result:
            return
        fmt = self.fmt_var.get()
        self._set_status(f"Generating {fmt} report…")
        try:
            path = generate_report(self._analysis_result, fmt)
            self._set_status(f"✅  Report saved: {path}")
            if messagebox.askyesno("Report Saved", f"Report saved to:\n{path}\n\nOpen it now?"):
                webbrowser.open(path)
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
            self._set_status("Export failed.")

    # ── UI helpers ────────────────────────────────────────────────────────────────

    def update_provider_label(self):
        p = self.settings.get("provider", "—")
        m = self.settings.get("model", "—")
        self.provider_lbl.configure(text=f"🤖  {p}  ·  {m}")

    def _set_status(self, msg: str):
        self.status_lbl.configure(text=msg)

    def _open_settings(self):
        SettingsDialog(self, self.settings)

    def _open_reports_folder(self):
        webbrowser.open(str(REPORTS_DIR))

    def _show_help(self):
        win = ctk.CTkToplevel(self)
        win.title("Help — RCA Analyzer")
        win.geometry("520x480")
        win.grab_set()

        ctk.CTkLabel(win, text="🔍  RCA Analyzer — Quick Guide",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(padx=20, pady=(20, 4))

        help_text = """
1. LOAD SOURCE CODE
   • Click "Add Folder" to load an entire project directory.
   • Click "Add Files" to select individual source files.
   • All 40+ languages are supported automatically.

2. CONFIGURE AI PROVIDER
   • Click "⚙️ Settings" and enter your API key.
   • Supports: OpenAI, Claude (Anthropic), Gemini (Google),
     Azure OpenAI, and local Ollama models.

3. SELECT ANALYSIS MODE
   • Choose from 10 analysis modes including:
     - Full RCA, Bug Detection, Security Scan,
       Performance, Code Quality, and more.

4. RUN ANALYSIS
   • Click "▶ Run Analysis" to begin.
   • Each file is sent to the AI for deep analysis.
   • Results appear in real-time in the results panel.

5. VIEW & EXPORT RESULTS
   • Click any file in the results list for detailed findings.
   • Click "🗂️ Project Summary" for a holistic view.
   • Export as HTML (rich report), JSON, or Markdown.
   • Reports are auto-saved to the /reports folder.

TIPS:
   • For large projects, start with a sub-folder.
   • GPT-4o and Claude Sonnet give the best RCA results.
   • Set temperature to 0.1-0.3 for consistent, precise output.
        """
        tb = ctk.CTkTextbox(win, wrap="word", fg_color="#0f172a", text_color="#94a3b8")
        tb.pack(fill="both", expand=True, padx=20, pady=10)
        tb.insert("1.0", help_text.strip())
        tb.configure(state="disabled")

        ctk.CTkButton(win, text="Close", command=win.destroy, width=100).pack(pady=10)


# ═══════════════════════════════════════════════════════════════════════════════
#  Entry point
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
