import streamlit as st
import pandas as pd
from PIL import Image
import requests
import io

# Title
st.title("📦 Smart Inventory System")

# Upload (Phone can take photo here)
st.subheader("📸 Upload Component Image")
uploaded_file = st.file_uploader("Take or upload a photo", type=["jpg", "png"])

detected_text = ""

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Convert image to bytes
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes = img_bytes.getvalue()

    # OCR API
    response = requests.post(
        "https://api.ocr.space/parse/image",
        files={"file": img_bytes},
        data={"apikey": "helloworld"}  # free demo key
    )

    result = response.json()

    try:
        detected_text = result["ParsedResults"][0]["ParsedText"]
    except:
        detected_text = "OCR failed"

    st.subheader("🔍 OCR Detected Text")
    st.write(detected_text)

# Input fields
component = st.text_input("Component Name")
qty = st.number_input("Quantity", min_value=1, value=1)
location = st.text_input("Location (e.g. A1)")

# Save button
if st.button("Add to Inventory"):
    st.success(f"Saved: {component}, Qty: {qty}, Location: {location}")
