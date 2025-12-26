from __future__ import annotations

import os
import sys
import json
import importlib
from pathlib import Path
from datetime import datetime

# Permanent: make project root importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_APP_MODULE = "web.app"
DEFAULT_APP_OBJECT = "app"

def routes_from_flask(app):
    routes = []
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        methods = sorted(m for m in rule.methods if m not in {"HEAD", "OPTIONS"})
        routes.append({"rule": str(rule), "endpoint": rule.endpoint, "methods": methods})
    return routes

def main():
    app_module = os.environ.get("STATUS_APP_MODULE", DEFAULT_APP_MODULE)
    app_object = os.environ.get("STATUS_APP_OBJECT", DEFAULT_APP_OBJECT)

    report = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "cwd": os.getcwd(),
        "project_root_added_to_syspath": str(PROJECT_ROOT),
        "python": {"executable": sys.executable, "version": sys.version},
    }

    try:
        mod = importlib.import_module(app_module)
        app = getattr(mod, app_object)
        report["flask"] = {
            "app_module": app_module,
            "app_object": app_object,
            "routes": routes_from_flask(app),
        }
    except Exception as e:
        report["flask"] = {
            "app_module": app_module,
            "app_object": app_object,
            "error": repr(e),
        }

    out_path = PROJECT_ROOT / "status_report_routes.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote: {out_path}")
    print("Paste flask.routes from status_report_routes.json")

if __name__ == "__main__":
    main()
