# web/templates_data.py

GALLERY_TEMPLATES = [
    {
        "id": "leads_to_sheet_alert",
        "name": "Lead capture → Google Sheet (+ email alert)",
        "type": "leads_sheet",
        "minutes_saved_per_run": 10,
        "description": "Collect leads reliably, store them in Sheets, and notify instantly.",
    },
    {
        "id": "daily_health_check",
        "name": "Daily health check (email summary)",
        "type": "generic",
        "minutes_saved_per_run": 5,
        "description": "Runs daily and logs status (v1 simulated).",
    },
]
