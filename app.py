import streamlit as st
import pandas as pd
from PIL import Image
import requests
import os

# Excel file
file = "inventory.xlsx"

# Load or create Excel
if os.path.exists(file):
    df = pd.read_excel(file)
else:
    df = pd.DataFrame(columns=["Component", "Quantity", "Location"])

# OCR FUNCTION (API)
def extract_text(image_file):
    url = "https://api.ocr.space/parse/image"
    
    payload = {
        "apikey": "helloworld",  # free demo key
        "language": "eng"
    }

    files = {
        "file": image_file.getvalue()
    }

    response = requests.post(url, files=files, data=payload)
    result = response.json()

    try:
        return result["ParsedResults"][0]["ParsedText"]
    except:
        return ""

# Title
st.title("📦 Smart Inventory System")

# Upload
uploaded_file = st.file_uploader("📸 Upload Component Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Preview", use_column_width=True)

    # OCR (hidden)
    text = extract_text(uploaded_file)
    text_upper = text.upper()

    # =========================
    # 🔍 COMPONENT DETECTION
    # =========================
    import re

    component = ""

    if "ZENER" in text_upper:
        voltage_match = re.search(r'\d+\s?V', text_upper)
        
        if voltage_match:
            component = f"Zener Diode {voltage_match.group().replace(' ', '')}"
        else:
            component = "Zener Diode"

    elif "RESISTOR" in text_upper:
        component = "Resistor"

    elif "CAPACITOR" in text_upper:
        component = "Capacitor"

    if component == "":
        component = "Electronic Component"

    # =========================
    # 🔢 QUANTITY DETECTION
    # =========================
    qty = 1

    lines = text.split("\n")

    for i, line in enumerate(lines):
        if "QUANTITY" in line.upper():
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line.isdigit():
                    qty = int(next_line)
                    break

    # Fallback
    if qty == 1:
        for line in lines:
            line = line.strip()
            if line.isdigit():
                num = int(line)
                if 1 <= num <= 1000:
                    qty = num
                    break

    # =========================
    # 🎯 CLEAN UI
    # =========================
    st.subheader("✔️ Detected Result")

    col1, col2 = st.columns(2)

    with col1:
        component = st.text_input("Component", value=component)

    with col2:
        qty = st.number_input("Quantity", min_value=1, value=qty)

    location = st.text_input("Location (e.g. A1)")

    if st.button("💾 Save"):
        new_data = pd.DataFrame([[component, qty, location]],
                                columns=["Component", "Quantity", "Location"])
        
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_excel(file, index=False)

        st.success("Saved successfully!")
# Show inventory
st.divider()
st.subheader("📋 Inventory List")
st.dataframe(df)
