import streamlit as st
from datetime import datetime
from xhtml2pdf import pisa
from jinja2 import Environment, FileSystemLoader
import uuid
import os
from google_sheets_helper import append_invoice
import json


st.set_page_config(page_title="Invoice Generator", page_icon="📄")
st.title("📄 Webplause Invoice Generator")

# Function to get and increment invoice number
def get_next_invoice_number():
    counter_file = "invoice_counter.txt"
    if not os.path.exists(counter_file):
        with open(counter_file, "w") as f:
            f.write("1001")
    with open(counter_file, "r") as f:
        current = int(f.read().strip())
    with open(counter_file, "w") as f:
        f.write(str(current + 1))
    return f"INV-{current}"

# Customer Information
st.header("Customer Details")
customer_name = st.text_input("Customer Name")
customer_address = st.text_area("Customer Address")
customer_phone = st.text_input("Customer Phone")
customer_email = st.text_input("Customer Email")

# Invoice Items
st.header("Invoice Items")
items = []
num_items = st.number_input("Number of items", min_value=1, max_value=10, value=1)
for i in range(num_items):
    st.subheader(f"Item {i+1}")
    service = st.text_input(f"Service {i+1}", key=f"service_{i}")
    project = st.text_input(f"Project {i+1}", key=f"project_{i}")
    cost = st.text_input(f"Cost {i+1} (USD)", key=f"cost_{i}")
    items.append({"service": service, "project": project, "cost": cost})

# Summary
st.header("Invoice Summary")
user_invoice_no = st.text_input("Invoice Number (leave blank to auto-generate)")
user_date = st.text_input("Invoice Date (leave blank for today)")
total = st.text_input("Total Cost (USD)")
payment_link = st.text_input("Payment Link")

if st.button("Generate Invoice"):
    invoice_no = user_invoice_no.strip() if user_invoice_no.strip() else get_next_invoice_number()
    date = user_date.strip() if user_date.strip() else datetime.now().strftime("%d/%m/%Y")

    # Prepare data
    data = {
        "customer": {
            "name": customer_name,
            "address": customer_address,
            "phone": customer_phone,
            "email": customer_email
        },
        "invoice_no": invoice_no,
        "date": date,
        "items": items,
        "total": total,
        "payment_link": payment_link
    }

    # Render HTML using Jinja2
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("invoice_template.html")
    html_out = template.render(**data)

    # Create PDF
    output_path = f"invoice_{invoice_no}.pdf"
    with open(output_path, "w+b") as f:
        pisa.CreatePDF(html_out, dest=f)

    # Serve download
    with open(output_path, "rb") as f:
        st.success("✅ Invoice generated!")
        st.download_button(
            label="⬇️ Download Invoice PDF",
            data=f.read(),
            file_name=output_path,
            mime="application/pdf"
        )

    # Save invoice details to Google Sheet
    row = {
        "invoice_no": invoice_no,
        "date": date,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "customer_phone": customer_phone,
        "customer_address": customer_address,
        "total": total,
        "payment_link": payment_link,
        "items": json.dumps(items)
    }

    try:
        append_invoice(row, "InvoiceData")  # change this to your actual sheet name
        st.success("✅ Invoice data saved to Google Sheet.")
    except Exception as e:
        st.warning(f"⚠️ Failed to save invoice to Google Sheets: {e}")


    os.remove(output_path)
