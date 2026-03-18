import streamlit as st
import pandas as pd
from PIL import Image
file = "inventory.xlsx"

# Load Excel
try:
    df = pd.read_excel(file)
except:
    df = pd.DataFrame(columns=["Component", "Quantity", "Location"])

# Title
st.title("📦 Smart Inventory System")

# 📸 IMAGE PART (PUT HERE)
st.subheader("📸 Upload Component Image")

uploaded_file = st.file_uploader("Choose an image", type=["jpg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

# 🟦 INPUT PART (comes after image)
component = st.text_input("Component Name")
qty = st.number_input("Quantity", min_value=1)
location = st.text_input("Location (e.g. A1)")

# Button
if st.button("Update Inventory"):
    new_row = pd.DataFrame([{
        "Component": component,
        "Quantity": qty,
        "Location": location
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(file, index=False)

    st.success("Saved to Excel ✅")

# Show data
st.subheader("Inventory Data")
st.dataframe(df)
