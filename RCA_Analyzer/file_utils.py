"""
file_utils.py — file and folder ingestion helpers for RCA Analyzer
"""
import os
import chardet
from pathlib import Path
from typing import List, Tuple, Optional
from config import LANGUAGE_EXTENSIONS

# Directories to always skip
SKIP_DIRS = {
    ".git", ".svn", "__pycache__", "node_modules", ".venv", "venv",
    "env", ".env", "dist", "build", ".next", ".nuxt", "target",
    "bin", "obj", ".idea", ".vscode", "coverage", ".pytest_cache",
    ".mypy_cache", "vendor", "bower_components", ".terraform",
}

MAX_FILE_SIZE_BYTES = 500 * 1024  # 500 KB per file


def detect_encoding(path: str) -> str:
    """Detect file encoding using chardet."""
    with open(path, "rb") as f:
        raw = f.read(4096)
    result = chardet.detect(raw)
    return result.get("encoding") or "utf-8"


def read_file_safe(path: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Read a file safely. Returns (content, error_message).
    Returns (None, error) if the file cannot be read.
    """
    p = Path(path)
    if p.stat().st_size > MAX_FILE_SIZE_BYTES:
        return None, f"File too large (>{MAX_FILE_SIZE_BYTES // 1024} KB), skipped."
    encoding = detect_encoding(path)
    try:
        with open(path, "r", encoding=encoding, errors="replace") as f:
            return f.read(), None
    except Exception as e:
        return None, str(e)


def get_language(path: str) -> str:
    """Return the programming language name based on file extension."""
    ext = Path(path).suffix.lower()
    return LANGUAGE_EXTENSIONS.get(ext, "Unknown")


def is_supported_file(path: str) -> bool:
    ext = Path(path).suffix.lower()
    return ext in LANGUAGE_EXTENSIONS


def collect_files_from_folder(
    folder: str,
    selected_extensions: Optional[List[str]] = None,
) -> List[dict]:
    """
    Recursively collect all supported source files from a folder.
    Returns a list of dicts: {path, language, size, content, error}
    """
    collected = []
    folder_path = Path(folder)

    for root, dirs, files in os.walk(folder_path):
        # Prune skipped directories in-place
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for fname in files:
            fpath = Path(root) / fname
            ext = fpath.suffix.lower()

            if selected_extensions:
                if ext not in selected_extensions:
                    continue
            elif not is_supported_file(str(fpath)):
                continue

            language = get_language(str(fpath))
            size = fpath.stat().st_size
            rel_path = str(fpath.relative_to(folder_path))

            content, error = read_file_safe(str(fpath))
            collected.append(
                {
                    "path": rel_path,
                    "abs_path": str(fpath),
                    "language": language,
                    "size": size,
                    "content": content,
                    "error": error,
                }
            )

    return collected


def collect_files_from_paths(paths: List[str]) -> List[dict]:
    """
    Collect content from a list of file paths (multi-file selection).
    """
    collected = []
    for p in paths:
        if not os.path.isfile(p):
            continue
        language = get_language(p)
        size = Path(p).stat().st_size
        content, error = read_file_safe(p)
        collected.append(
            {
                "path": os.path.basename(p),
                "abs_path": p,
                "language": language,
                "size": size,
                "content": content,
                "error": error,
            }
        )
    return collected


def summarise_files(files: List[dict]) -> dict:
    """Return a stats summary of collected files."""
    total = len(files)
    errored = sum(1 for f in files if f["error"])
    total_lines = 0
    lang_counts: dict = {}

    for f in files:
        if f["content"]:
            total_lines += f["content"].count("\n") + 1
        lang = f["language"]
        lang_counts[lang] = lang_counts.get(lang, 0) + 1

    return {
        "total_files": total,
        "errored_files": errored,
        "total_lines": total_lines,
        "languages": lang_counts,
    }


def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / 1024 ** 2:.1f} MB"
