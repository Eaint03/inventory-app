import streamlit as st
import pandas as pd
from PIL import Image
import requests
import os
import re

# =========================
# 📁 Excel setup
# =========================
file = "inventory.xlsx"

if os.path.exists(file):
    df = pd.read_excel(file)
else:
    df = pd.DataFrame(columns=["Component", "Quantity", "Location"])

# =========================
# 🔍 OCR FUNCTION
# =========================
def extract_text(image_file):
    url = "https://api.ocr.space/parse/image"
    
    payload = {
        "apikey": "helloworld",
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

# =========================
# 🎯 UI TITLE
# =========================
st.title("📦 Smart Inventory System")

# =========================
# 📸 UPLOAD
# =========================
uploaded_file = st.file_uploader("📸 Upload Component Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Preview", use_column_width=True)

    # =========================
    # 🔍 OCR WITH LOADING
    # =========================
    with st.spinner("🔍 Detecting from image..."):
        text = extract_text(uploaded_file)

    text_upper = text.upper()

    # =========================
    # 🔍 COMPONENT DETECTION
    # =========================
    component = ""

    # Detect Zener diode (DigiKey label specific)
    if "ZENER" in text_upper or "DIODE" in text_upper:
        voltage_match = re.search(r'(\d{1,3})\s?V', text_upper)
        
        if voltage_match:
            component = f"Zener Diode {voltage_match.group(1)}V"
        else:
            component = "Zener Diode"

    # Detect IC
    elif "IC" in text_upper:
        component = "IC Chip"

    # Detect resistor
    elif "RESISTOR" in text_upper:
        component = "Resistor"

    # Detect capacitor
    elif "CAPACITOR" in text_upper:
        component = "Capacitor"

    # Fallback (leave empty for user edit)
    if component == "":
        component = ""

    # =========================
    # 🔢 QUANTITY DETECTION
    # =========================
    qty = 1

    # Case 1: "Quantity 100"
    match = re.search(r'QUANTITY\s*(\d+)', text_upper)
    if match:
        qty = int(match.group(1))

    # Case 2: number below "Quantity"
    if qty == 1:
        lines = text_upper.split("\n")
        for i, line in enumerate(lines):
            if "QUANTITY" in line:
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line.isdigit():
                        qty = int(next_line)
                        break

    # Case 3: smart fallback
    if qty == 1:
        numbers = re.findall(r'\b\d{2,4}\b', text_upper)
        
        for num in numbers:
            num_int = int(num)
            if 10 <= num_int <= 1000:
                qty = num_int
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

    # =========================
    # 💾 SAVE
    # =========================
    if st.button("💾 Save"):
        new_data = pd.DataFrame([[component, qty, location]],
                                columns=["Component", "Quantity", "Location"])
        
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_excel(file, index=False)

        st.success("Saved successfully!")
        st.rerun()

# =========================
# 📋 INVENTORY TABLE
# =========================
st.divider()
st.subheader("📋 Inventory List")
st.dataframe(df)
