import streamlit as st
import pandas as pd
from PIL import Image
import requests
import io
import re
import numpy as np

# =========================
# 🔗 GOOGLE SHEETS FUNCTION
# =========================
def save_to_sheet(component, qty, location):
    url = "https://script.google.com/a/macros/nexwah.com/s/AKfycbwHdeF4x2zDhiRbxAORM2HIrkZxODV8ByVO-mL14OPD3SKDKHOCaSJSE6OnC04duUwMhA/exec"

    data = {
        "component": component,
        "quantity": qty,
        "location": location
    }

    requests.post(url, json=data)

# =========================
# 🎯 TITLE
# =========================
st.title("📦 Smart Inventory System")

# =========================
# 📸 UPLOAD
# =========================
st.subheader("📸 Take or Upload Component Image")
uploaded_file = st.file_uploader("Upload image", type=["jpg", "png", "jpeg"])

component_auto = ""
qty_auto = 1
location_auto = ""

# =========================
# 🔍 PROCESS IMAGE + OCR
# =========================
if uploaded_file:
    image = Image.open(uploaded_file)

    # Convert to grayscale
    image = image.convert("L")

    # Improve contrast
    img_array = np.array(image)
    img_array = np.clip(img_array * 1.5, 0, 255).astype(np.uint8)
    image = Image.fromarray(img_array)

    # Resize
    image.thumbnail((800, 800))

    st.image(image, caption="Processed Image", use_column_width=True)

    # Convert to JPEG
    img_bytes_io = io.BytesIO()
    image.save(img_bytes_io, format="JPEG", quality=70)
    img_bytes = img_bytes_io.getvalue()

    # OCR API
    with st.spinner("🔍 Detecting from image..."):
    response = requests.post(
        "https://api.ocr.space/parse/image",
        files={"file": ("image.jpg", img_bytes, "image/jpeg")},
        data={
            "apikey": "helloworld",
            "language": "eng",
            "OCREngine": 2,
            "scale": True,
            "detectOrientation": True
        }
    )
    result = response.json()
    parsed = result.get("ParsedResults")

    detected_text = ""
    if parsed and parsed[0].get("ParsedText"):
        detected_text = parsed[0]["ParsedText"]

    # Clean feedback (NO raw text)
    if detected_text:
        st.success("✔️ Details detected automatically")
    else:
        st.warning("⚠️ Unable to detect clearly, please enter manually")

    # =========================
    # 🔍 SMART EXTRACTION
    # =========================
    if detected_text:
        # Quantity
        qty_match = re.search(r'Quantity\s*(\d+)', detected_text, re.IGNORECASE)
        if qty_match:
            qty_auto = int(qty_match.group(1))
        else:
            numbers = re.findall(r'\b\d{2,4}\b', detected_text)
            for num in numbers:
                num_int = int(num)
                if 10 <= num_int <= 1000:
                    qty_auto = num_int
                    break

        # Component
        for line in detected_text.split("\n"):
            if any(word in line.upper() for word in ["DIODE", "RESISTOR", "CAPACITOR", "IC"]):
                component_auto = line.strip()
                break

        # Location (optional)
        loc_match = re.search(r'[A-Z]{1,3}\d{1,3}[-]?\d*', detected_text)
        if loc_match:
            location_auto = loc_match.group()

# =========================
# ✍️ INPUT SECTION
# =========================
st.subheader("✍️ Confirm / Edit Details")

component = st.text_input("Component Name", component_auto, placeholder="Auto-detected")
qty = st.number_input("Quantity", min_value=1, value=qty_auto)
location = st.text_input("Location (e.g. A1)", location_auto)

# =========================
# 💾 SAVE TO GOOGLE SHEET
# =========================
if st.button("Add to Inventory"):
    save_to_sheet(component, qty, location)
    st.success("✅ Saved to Google Sheet!")
