import streamlit as st
import pandas as pd
from PIL import Image
import requests
import io
import re
import numpy as np

# Title
st.title("📦 Smart Inventory System")

# Upload section
st.subheader("📸 Take or Upload Component Image")
uploaded_file = st.file_uploader("Upload image", type=["jpg", "png"])

detected_text = ""
component_auto = ""
qty_auto = 1
location_auto = ""

if uploaded_file:
    image = Image.open(uploaded_file)

    # 🔥 STEP 1: Convert to grayscale
    image = image.convert("L")

    # 🔥 STEP 2: Improve contrast
    img_array = np.array(image)
    img_array = np.clip(img_array * 1.5, 0, 255).astype(np.uint8)
    image = Image.fromarray(img_array)

    # 🔥 STEP 3: Resize (FIX for file size)
    max_size = (800, 800)
    image.thumbnail(max_size)

    st.image(image, caption="Processed Image", use_column_width=True)

    # 🔥 STEP 4: Convert to compressed JPEG
    img_bytes_io = io.BytesIO()
    image.save(img_bytes_io, format="JPEG", quality=70)
    img_bytes = img_bytes_io.getvalue()

    # 🔥 STEP 5: OCR API (FIXED FILE FORMAT)
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

    # 🔥 DEBUG
    st.write("🔧 OCR Raw Result:", result)

    # 🔥 STEP 6: Extract text safely
    parsed = result.get("ParsedResults")

    if parsed and parsed[0].get("ParsedText"):
        detected_text = parsed[0]["ParsedText"]
    else:
        detected_text = ""

    # Show OCR result
    st.subheader("🔍 OCR Detected Text")

    if detected_text:
        st.text(detected_text)
    else:
        st.warning("⚠️ OCR could not detect text clearly. Please enter manually.")

    # 🔥 STEP 7: SMART EXTRACTION
    if detected_text:
        # Quantity
        qty_match = re.search(r'Quantity\s*(\d+)', detected_text, re.IGNORECASE)
        if qty_match:
            qty_auto = int(qty_match.group(1))
        else:
            num_match = re.search(r'\b\d+\b', detected_text)
            if num_match:
                qty_auto = int(num_match.group())

        # Component
        for line in detected_text.split("\n"):
            if any(word in line.upper() for word in ["DIODE", "RESISTOR", "CAPACITOR"]):
                component_auto = line.strip()
                break

        # Location
        loc_match = re.search(r'[A-Z]{1,3}\d{1,3}[-]?\d*', detected_text)
        if loc_match:
            location_auto = loc_match.group()

# Input section
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
