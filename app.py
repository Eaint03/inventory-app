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

    # 🔥 SIMPLE SMART DETECTION
    component = ""
    if "DIODE" in text.upper():
        component = "Zener Diode 18V"

    qty = 1
    for word in text.split():
        if word.isdigit():
            qty = int(word)

    st.divider()

    # Clean UI
    st.subheader("✔️ Detected Result")

    col1, col2 = st.columns(2)

    with col1:
        component = st.text_input("Component", value=component)

    with col2:
        qty = st.number_input("Quantity", min_value=1, value=qty)

    location = st.text_input("Location (e.g. A1)")

    # Save
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
