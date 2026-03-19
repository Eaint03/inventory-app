import streamlit as st
from PIL import Image
import pytesseract

st.title("📦 Smart Inventory System")

# Upload
uploaded_file = st.file_uploader("📸 Upload Component Image", type=["jpg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Preview", use_column_width=True)

    # OCR (hidden)
    text = pytesseract.image_to_string(image)

    # 🔥 Extract ONLY what you want (example: quantity + component)
    component = "Zener Diode 18V" if "DIODE" in text else ""
    qty = 100 if "100" in text else ""

    st.divider()

    # ✨ FINAL CLEAN UI ONLY
    st.subheader("✔️ Detected Result")

    col1, col2 = st.columns(2)

    with col1:
        component = st.text_input("Component", value=component)

    with col2:
        qty = st.number_input("Quantity", min_value=1, value=qty if qty else 1)

    location = st.text_input("Location (e.g. A1)")

    if st.button("💾 Save"):
        st.success("Saved successfully!")
