import streamlit as st
import pandas as pd
from PIL import Image
import requests
import io
import re

# Title
st.title("📦 Smart Inventory System")

# Upload (Phone can take photo)
st.subheader("📸 Take or Upload Component Image")
uploaded_file = st.file_uploader("Upload image", type=["jpg", "png"])

detected_text = ""
component_auto = ""
qty_auto = 1
location_auto = ""

if uploaded_file:
    image = Image.open(uploaded_file)

    # 🔥 Improve OCR accuracy (IMPORTANT)
    image = image.convert("L")  # grayscale

    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Convert image to bytes
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes = img_bytes.getvalue()

    # 🔥 OCR API with better engine
    response = requests.post(
        "https://api.ocr.space/parse/image",
        files={"file": img_bytes},
        data={
            "apikey": "helloworld",
            "language": "eng",
            "OCREngine": 2
        }
    )

    result = response.json()

    # 🔥 Safe extraction
    try:
        parsed = result.get("ParsedResults")
        if parsed:
            detected_text = parsed[0].get("ParsedText", "")
        else:
            detected_text = "No text detected"
    except:
        detected_text = "OCR failed"

    # Show OCR result
    st.subheader("🔍 OCR Detected Text")
    st.text(detected_text)

    # 🔥 SMART EXTRACTION (simple rules)

    # Extract Quantity (look for "Quantity 100")
    qty_match = re.search(r'Quantity\s*(\d+)', detected_text, re.IGNORECASE)
    if qty_match:
        qty_auto = int(qty_match.group(1))
    else:
        # fallback: first number found
        num_match = re.search(r'\b\d+\b', detected_text)
        if num_match:
            qty_auto = int(num_match.group())

    # Extract Component (look for DIODE / RESISTOR etc.)
    for line in detected_text.split("\n"):
        if "DIODE" in line.upper() or "RESISTOR" in line.upper():
            component_auto = line.strip()
            break

    # Extract Location (pattern like PB51-09 or A1)
    loc_match = re.search(r'[A-Z]{1,3}\d{1,3}[-]?\d*', detected_text)
    if loc_match:
        location_auto = loc_match.group()

# Input fields (auto-filled)
st.subheader("✍️ Confirm / Edit Details")

component = st.text_input("Component Name", component_auto)
qty = st.number_input("Quantity", min_value=1, value=qty_auto)
location = st.text_input("Location (e.g. A1)", location_auto)

# Save button
if st.button("Add to Inventory"):
    data = pd.DataFrame({
        "Component": [component],
        "Quantity": [qty],
        "Location": [location]
    })

    try:
        existing = pd.read_excel("inventory.xlsx")
        updated = pd.concat([existing, data], ignore_index=True)
    except:
        updated = data

    updated.to_excel("inventory.xlsx", index=False)

    st.success("✅ Saved to Inventory!")

    st.dataframe(updated)
