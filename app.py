import streamlit as st
import requests
from PIL import Image
import io
import re

# =========================
# GOOGLE SHEETS
# =========================
def save_to_sheet(component, qty, location):
    url = "https://script.google.com/macros/s/AKfycbzsX55cEf1cHBXWPgBz-ypLiLz8rZ06IgKZp7edJBsyvwpAzY0riHamRz-ay8S1whV15w/exec"

    data = {
        "component": component,
        "quantity": qty,
        "location": location
    }

    requests.post(url, json=data)


# =========================
# OCR FUNCTION (STABLE)
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
# EXTRACTION LOGIC
# =========================
def extract_info(text):

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    component = ""
    part_number = ""
    quantity = ""

    # ===== COMPONENT =====
    for line in lines:
        upper = line.upper()
        if any(x in upper for x in ["DIODE", "EEPROM", "RESISTOR", "CAPACITOR", "IC"]):
            component = line
            break

    if not component:
        component = lines[0]

    # ===== PART NUMBER =====
    for i in range(len(lines)):
        line = lines[i].upper()

        if "MFG" in line or "P/N" in line or "PN" in line:

            match = re.search(r"[A-Z0-9\-,]{6,}", lines[i])
            if match:
                part_number = match.group()
                break

            if i + 1 < len(lines):
                match = re.search(r"[A-Z0-9\-,]{6,}", lines[i+1])
                if match:
                    part_number = match.group()
                    break

    # fallback
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

    # fallback
    if not quantity:
        nums = re.findall(r"\b\d{1,4}\b", text)
        if nums:
            quantity = max(nums, key=int)

    return component, part_number, quantity


# =========================
# UI
# =========================
st.set_page_config(page_title="Smart Inventory", layout="centered")

st.title("📦 Smart Inventory System")

st.subheader("📷 Take Photo")

image_file = st.camera_input("Take a picture")

if image_file:

    image = Image.open(image_file)
    st.image(image, caption="Captured Image", use_column_width=True)

    if st.button("🔍 Scan & Extract"):

        with st.spinner("Reading label..."):
            text = run_ocr(image)

        if not text:
            st.error("❌ OCR failed. Try clearer image.")
        else:
            st.success("✅ Text detected")

            st.text_area("Detected Text", text, height=200)

            component, part, qty = extract_info(text)

            st.subheader("📌 Extracted Data")
            st.write("Component:", component)
            st.write("Part Number:", part)
            st.write("Quantity:", qty)

            if st.button("💾 Save to Inventory"):
                save_to_sheet(component, qty, "")
                st.success("Saved to Google Sheets!")
