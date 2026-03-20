import streamlit as st
from PIL import Image
import requests
import io
import re
import numpy as np

# =========================
# FUNCTION
# =========================
def save_to_sheet(component, qty, location):
    url = "https://script.google.com/macros/s/AKfycbzsX55cEf1cHBXWPgBz-ypLiLz8rZ06IgKZp7edJBsyvwpAzY0riHamRz-ay8S1whV15w/exec"

    data = {
        "component": component,
        "quantity": qty,
        "location": location
    }

    response = requests.post(url, json=data)
    return response.text

# =========================
# PAGE CONTROL
# =========================
if "page" not in st.session_state:
    st.session_state.page = "home"


# =========================
# HOME Screen
# =========================
if st.session_state.page == "home":
    st.title("Welcome to smart Inventory System")

    st.write("")  # spacing
    st.write("")

    # Create 3 columns → middle one is center
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### Choose Action")

        if st.button("➕ Add Inventory", use_container_width=True):
            st.session_state.page = "add"

        st.write("")  # space between buttons

        if st.button("📤 Take Inventory", use_container_width=True):
            st.session_state.page = "take"
# =========================
# ADD PAGE
# =========================
elif st.session_state.page == "add":

    if st.button(" Back"):
        st.session_state.page = "home"

    st.title("Adding Inventory")

    # 📸 UPLOAD (MISSING BEFORE)
    uploaded_file = st.file_uploader("Upload image", type=["jpg", "png", "jpeg"])

    # DEFAULT VALUES (MISSING BEFORE)
    component_auto = ""
    qty_auto = 1
    location_auto = ""

    # 🔍 OCR
    if uploaded_file:
        image = Image.open(uploaded_file)

        image = image.convert("L")

        img_array = np.array(image)
        img_array = np.clip(img_array * 1.5, 0, 255).astype(np.uint8)
        image = Image.fromarray(img_array)

        image.thumbnail((800, 800))

        st.image(image, caption="Processed Image", use_column_width=True)

        img_bytes_io = io.BytesIO()
        image.save(img_bytes_io, format="JPEG", quality=70)
        img_bytes = img_bytes_io.getvalue()

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

        if detected_text:
            st.success("✔️ Details detected automatically")
        else:
            st.warning("⚠️ Unable to detect clearly")

        if detected_text:
            qty_match = re.search(r'Quantity\s*(\d+)', detected_text, re.IGNORECASE)
            if qty_match:
                qty_auto = int(qty_match.group(1))

            for line in detected_text.split("\n"):
                if any(word in line.upper() for word in ["DIODE", "RESISTOR", "CAPACITOR", "IC"]):
                    component_auto = line.strip()
                    break

            loc_match = re.search(r'[A-Z]{1,3}\d{1,3}[-]?\d*', detected_text)
            if loc_match:
                location_auto = loc_match.group()

    # ✍️ INPUT
    st.subheader("✍️ Confirm / Edit Details")

    component = st.text_input("Component Name", component_auto)
    qty = st.number_input("Quantity", min_value=1, value=qty_auto)
    location = st.text_input("Location", location_auto)

    # 💾 SAVE
    if st.button("Add to Inventory"):
        response = save_to_sheet(component, qty, location)

        if "Success" in response:
            st.success("✅ Saved to Google Sheet!")
        else:
            st.error("❌ Failed to save.")
