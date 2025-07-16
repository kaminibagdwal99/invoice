import json, os, gspread
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

def _build_credentials():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    if "google" in st.secrets:
        creds_dict = dict(st.secrets["google"])
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    elif os.path.exists("credentials.json"):
        return ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    else:
        raise FileNotFoundError("Google credentials not found.")

def append_invoice(row_data, sheet_name: str):
    creds = _build_credentials()
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    sheet.append_row([
        row_data["invoice_no"],
        row_data["date"],
        row_data["customer_name"],
        row_data["customer_email"],
        row_data["customer_phone"],
        row_data["customer_address"],
        row_data["total"],
        row_data["payment_option"],
        row_data["duration"],
        row_data["items"],
    ])
    return True
