import gspread, json

with open("service_account.json", "r", encoding="utf-8") as f:
    print("Using service account:", json.load(f).get("client_email"))

gc = gspread.service_account(filename="service_account.json")
files = gc.list_spreadsheet_files()
print("Visible spreadsheets:", len(files))
print(files[:5])
