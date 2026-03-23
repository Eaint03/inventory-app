import streamlit as st
import requests
from PIL import Image, ImageEnhance, ImageFilter
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
        "component": part,
        "quantity": qty,
        "location": ""
    }

    response = requests.post(url, json=data)
    return response.text


# =========================
# IMAGE PREPROCESSING
# =========================
def preprocess_image(image):
    image = image.convert("L")  # grayscale
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    image = image.filter(ImageFilter.SHARPEN)
    return image


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
# CLEAN OCR TEXT
# =========================
def clean_text(text):
    text = text.upper()
    text = text.replace("O", "0")
    text = text.replace("I", "1")
    text = text.replace("S", "5")
    return text


# =========================
# EXTRACT DATA
# =========================
def extract_info(text):

    part = ""
    qty = ""

    # PART NUMBER
    part_match = re.search(r"(P/N|PN|MFG)[^\n]*", text)
    if part_match:
        line = part_match.group()
        match = re.search(r"[A-Z0-9\-]{6,}", line)
        if match:
            part = match.group()

    if not part:
        matches = re.findall(r"[A-Z0-9\-]{8,}", text)
        if matches:
            part = sorted(matches, key=len, reverse=True)[0]

    # QUANTITY
    qty_match = re.search(r"(QTY|QUANTITY)[^\d]*(\d+)", text)
    if qty_match:
        qty = qty_match.group(2)

    if not qty:
        nums = re.findall(r"\b\d{1,3}\b", text)
        if nums:
            qty = max(nums, key=int)

    return part, qty


# =========================
# VALIDATION
# =========================
def validate(part, qty):

    if not part or len(part) < 6:
        return False

    if not re.match(r"[A-Z0-9\-]+$", part):
        return False

    if not qty.isdigit():
        return False

    if int(qty) <= 0 or int(qty) > 10000:
        return False

    return True


# =========================
# HOME PAGE
# =========================
if st.session_state.page == "home":

    st.title("Smart Inventory System")

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
        st.image(image, caption="Captured")

        if st.button("Scan"):

            # PREPROCESS
            processed = preprocess_image(image)

            # OCR
            text = run_ocr(processed)

            if not text:
                st.error("❌ OCR failed — retake photo")
            else:

                text = clean_text(text)

                part, qty = extract_info(text)

                if validate(part, qty):

                    st.success("✅ Valid Result")
                    st.write("Part Number:", part)
                    st.write("Quantity:", qty)

                    response = save_to_sheet(part, qty)
                    st.write("Saved:", response)

                else:
                    st.error("❌ Invalid detection — please retake photo")


# =========================
# TAKE PAGE
# =========================
elif st.session_state.page == "take":

    if st.button("Back"):
        st.session_state.page = "home"
        st.rerun()

    st.title("📤 Take Inventory (Coming Soon)")
