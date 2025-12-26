import json
import gspread

SPREADSHEET_ID = "1CmNDVr2t4JWwmnZkRymxMw-ybgZ7gNiICIiR3yuMX1I"

with open("service_account.json", "r", encoding="utf-8") as f:
    creds = json.load(f)
print("Using service account:", creds.get("client_email"))

gc = gspread.service_account(filename="service_account.json")
sh = gc.open_by_key(SPREADSHEET_ID)
ws = sh.worksheet("Sheet1")
ws.append_row(["hello", "from", "python"], value_input_option="RAW")
print("OK")
