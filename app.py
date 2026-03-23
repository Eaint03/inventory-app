import streamlit as st
import requests
from PIL import Image
import io
import re

# =========================
# PAGE STATE
# =========================
if "page" not in st.session_state:
    st.session_state.page = "home"

# =========================
# GOOGLE SHEET
# =========================
def save_to_sheet(part, qty):
    url = "https://script.google.com/macros/s/AKfycbzsX55cEf1cHBXWPgBz-ypLiLz8rZ06IgKZp7edJBsyvwpAzY0riHamRz-ay8S1whV15w/exec"

    data = {
        "component": part,  # using part as main key
        "quantity": qty,
        "location": ""
    }

    requests.post(url, json=data)

# =========================
# OCR
# =========================
def run_ocr(image):

    url = "https://api.ocr.space/parse/image"

    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_bytes = buffered.getvalue()

    files = {'file': ('image.jpg', img_bytes, 'image/jpeg')}
    data = {'apikey': 'helloworld'}

    response = requests.post(url, files=files, data=data)
    result = response.json()

    if result.get("IsErroredOnProcessing"):
        return None

    parsed = result.get("ParsedResults")
    if parsed:
        return parsed[0].get("ParsedText")

    return None

# =========================
# STRONG EXTRACTION (ONLY P/N + QTY)
# =========================
def extract_info(text):

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    part_number = ""
    quantity = ""

    # ===== PART NUMBER =====
    for i in range(len(lines)):
        line = lines[i].upper()

        if "MFG" in line or "P/N" in line or "PN" in line:

            # same line
            match = re.search(r"[A-Z0-9\-,]{6,}", lines[i])
            if match:
                part_number = match.group()
                break

            # next line
            if i + 1 < len(lines):
                match = re.search(r"[A-Z0-9\-,]{6,}", lines[i+1])
                if match:
                    part_number = match.group()
                    break

    # fallback (longest code-like string)
    if not part_number:
        matches = re.findall(r"[A-Z0-9\-,]{8,}", text)
        if matches:
            part_number = sorted(matches, key=len, reverse=True)[0]

    # ===== QUANTITY =====
    for i in range(len(lines)):
        line = lines[i].upper()

        if "QTY" in line or "QUANTITY" in line:

            match = re.search(r"\d+", lines[i])
            if match:
                quantity = match.group()
                break

            if i + 1 < len(lines):
                match = re.search(r"\d+", lines[i+1])
                if match:
                    quantity = match.group()
                    break

    # fallback (avoid big invoice numbers)
    if not quantity:
        nums = re.findall(r"\b\d{1,3}\b", text)
        if nums:
            quantity = max(nums, key=int)

    return part_number, quantity

# =========================
# HOME PAGE
# =========================
if st.session_state.page == "home":

    st.title("Welcome to Smart Inventory System")

    st.write("")

    if st.button("➕ Add Inventory"):
        st.session_state.page = "add"
        st.rerun()

    if st.button("📤 Take Inventory"):
        st.session_state.page = "take"
        st.rerun()

# =========================
# ADD PAGE
# =========================
elif st.session_state.page == "add":

    if st.button("Back"):
        st.session_state.page = "home"
        st.rerun()

    st.title("➕ Add Inventory")

    image_file = st.camera_input("Take Photo")

    if image_file:

        image = Image.open(image_file)
        st.image(image, use_column_width=True)

        if st.button("Scan"):

            with st.spinner("Reading label..."):
                text = run_ocr(image)

            if not text:
                st.error("❌ OCR failed")
            else:
                st.success("Text detected")

                part, qty = extract_info(text)

                st.subheader("Result")
                st.write("Part Number:", part)
                st.write("Quantity:", qty)

                if st.button("Save"):
                    save_to_sheet(part, qty)
                    st.success("Saved!")

# =========================
# TAKE PAGE
# =========================
elif st.session_state.page == "take":

    if st.button("Back"):
        st.session_state.page = "home"
        st.rerun()

    st.title("📤 Take Inventory")
    st.write("Coming soon")
