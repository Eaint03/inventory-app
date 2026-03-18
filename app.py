import streamlit as st
import pandas as pd
from PIL import Image
import numpy as np
import easyocr

# Initialize OCR (put near top)
reader = easyocr.Reader(['en'])

# Title
st.title("📦 Smart Inventory System")

# Upload Image
st.subheader("📸 Upload Component Image")
uploaded_file = st.file_uploader("Choose an image", type=["jpg", "png"])

detected_text = ""

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Convert image to array
    img_array = np.array(image)

    # Run OCR
    result = reader.readtext(img_array)

    # Combine detected text
    detected_text = " ".join([text[1] for text in result])

    st.subheader("🔍 OCR Detected Text")
    st.write(detected_text)

# Input fields (auto-fill using OCR)
component = st.text_input("Component Name", detected_text)
qty = st.number_input("Quantity", min_value=1, value=1)
location = st.text_input("Location (e.g. A1)")

# Save button
if st.button("Add to Inventory"):
    st.success(f"Saved: {component}, Qty: {qty}, Location: {location}")
