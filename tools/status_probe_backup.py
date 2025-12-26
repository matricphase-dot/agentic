from __future__ import annotations

import os
import sys
import json
import importlib
from pathlib import Path
from datetime import datetime

# ---- CONFIG YOU MAY NEED TO EDIT ----
# If your Flask app file is not "app.py" or your Flask variable isn't named "app",
# edit these:
DEFAULT_APP_MODULE = "app"          # app.py -> "app"
DEFAULT_APP_OBJECT = "app"          # Flask(...) assigned to variable named "app"
# -------------------------------------


def _safe_bool(v: str | None) -> bool:
    return bool(v and str(v).strip())


def _mask_email(v: str | None) -> str | None:
    if not v:
        return None
    v = v.strip()
    if "@" not in v:
        return "***"
    name, domain = v.split("@", 1)
    if len(name) <= 2:
        return f"{name[0]}***@{domain}"
    return f"{name[:2]}***@{domain}"


def _collect_env_summary() -> dict:
    return {
        "SMTP_HOST_set": _safe_bool(os.environ.get("SMTP_HOST")),
        "SMTP_PORT_set": _safe_bool(os.environ.get("SMTP_PORT")),
        "SMTP_USER_set": _safe_bool(os.environ.get("SMTP_USER")),
        "SMTP_PASS_set": _safe_bool(os.environ.get("SMTP_PASS")),
        "ALERT_TO_EMAIL_set": _safe_bool(os.environ.get("ALERT_TO_EMAIL")),
        "SMTP_USER_masked": _mask_email(os.environ.get("SMTP_USER")),
        "ALERT_TO_EMAIL_masked": _mask_email(os.environ.get("ALERT_TO_EMAIL")),
    }


def _pip_freeze_snippet(max_lines: int = 80) -> list[str]:
    try:
        import subprocess
        out = subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True)
        lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
        return lines[:max_lines]
    except Exception as e:
        return [f"ERROR: pip freeze failed: {e!r}"]


def _tree_snapshot(root: Path, max_files: int = 250) -> dict:
    skip_dirs = {".venv", "venv", "__pycache__", ".git", ".pytest_cache", "node_modules"}
    files = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        parts = set(part.lower() for part in p.parts)
        if any(d in parts for d in skip_dirs):
            continue
        # keep it lightweight: only names + size + modified time
        try:
            stat = p.stat()
            files.append(
                {
                    "path": str(p.relative_to(root)).replace("\\", "/"),
                    "bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
                }
            )
        except Exception:
            continue

        if len(files) >= max_files:
            break

    files.sort(key=lambda x: x["path"])
    return {
        "root": str(root),
        "file_count_listed": len(files),
        "files": files,
        "note": f"Limited to {max_files} files; excludes common env/cache folders.",
    }


def _load_flask_app(app_module: str, app_object: str):
    mod = importlib.import_module(app_module)
    app = getattr(mod, app_object)
    return app


def _routes_from_flask(app) -> list[dict]:
    routes = []
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        methods = sorted(m for m in rule.methods if m not in {"HEAD", "OPTIONS"})
        routes.append(
            {
                "rule": str(rule),
                "endpoint": rule.endpoint,
                "methods": methods,
            }
        )
    return routes


def _guess_automation_registry(root: Path) -> dict:
    """
    Heuristic search for 'automation type' registries without executing the whole app.
    Looks for common keywords in .py files: AUTOMATION, registry, types, leads_sheet, etc.
    """
    keywords = [
        "AUTOMATION",
        "automation_types",
        "AUTOMATION_TYPES",
        "registry",
        "leads_sheet",
        "scheduler",
        "add_job",
        "apscheduler",
        "BackgroundScheduler",
        "run_now",
    ]
    hits = []
    skip_dirs = {".venv", "venv", "__pycache__", ".git", ".pytest_cache", "node_modules"}
    for p in root.rglob("*.py"):
        parts = set(part.lower() for part in p.parts)
        if any(d in parts for d in skip_dirs):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        score = 0
        for kw in keywords:
            if kw in text:
                score += 1

        if score >= 2:
            # store only a small preview for safety
            preview_lines = []
            for i, line in enumerate(text.splitlines()[:220], start=1):
                if any(kw.lower() in line.lower() for kw in ["automation", "registry", "leads_sheet", "apscheduler", "add_job"]):
                    preview_lines.append(f"{i:04d}: {line[:180]}")
                if len(preview_lines) >= 25:
                    break

            hits.append(
                {
                    "path": str(p.relative_to(root)).replace("\\", "/"),
                    "keyword_score": score,
                    "preview": preview_lines,
                }
            )

    hits.sort(key=lambda x: (-x["keyword_score"], x["path"]))
    return {
        "hits": hits[:12],
        "note": "Heuristic scan: shows likely files that define automation types/registry/scheduler.",
    }


def main():
    root = Path(os.getcwd()).resolve()

    # Allow overrides:
    app_module = os.environ.get("STATUS_APP_MODULE", DEFAULT_APP_MODULE)
    app_object = os.environ.get("STATUS_APP_OBJECT", DEFAULT_APP_OBJECT)

    report = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "cwd": str(root),
        "python": {
            "executable": sys.executable,
            "version": sys.version,
        },
        "env_summary": _collect_env_summary(),
        "project_tree": _tree_snapshot(root),
        "automation_registry_guess": _guess_automation_registry(root),
        "pip_freeze_head": _pip_freeze_snippet(),
    }

    # Flask introspection (best signal)
    try:
        app = _load_flask_app(app_module, app_object)
        report["flask"] = {
            "app_module": app_module,
            "app_object": app_object,
            "routes": _routes_from_flask(app),
        }
    except Exception as e:
        report["flask"] = {
            "app_module": app_module,
            "app_object": app_object,
            "error": repr(e),
            "how_to_fix": (
                "Set STATUS_APP_MODULE and STATUS_APP_OBJECT env vars, e.g.\n"
                "set STATUS_APP_MODULE=web.app\n"
                "set STATUS_APP_OBJECT=app\n"
                "then rerun."
            ),
        }

    out_path = root / "status_report.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote: {out_path}")
    print("Paste the contents of status_report.json here (or the top ~200 lines).")


if __name__ == "__main__":
    main()
