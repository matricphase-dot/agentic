from __future__ import annotations

import os
import sys
import importlib
from pathlib import Path

def main():
    # Ensure project root is on sys.path so "import web.app" works even when run as a script.
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))

    mod = importlib.import_module("web.app")
    app = getattr(mod, "app")

    print("Loaded module:", mod.__name__)
    print("Flask app type:", type(app))
    print("Routes count:", len(list(app.url_map.iter_rules())))

    for name in ["db", "scheduler"]:
        print(f"{name} present:", hasattr(mod, name))

    keys = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS", "ALERT_TO_EMAIL"]
    for k in keys:
        print(k, "set" if os.environ.get(k) else "NOT set")

if __name__ == "__main__":
    main()
