import streamlit as st
from PIL import Image

# 🎨 Config
st.set_page_config(
    page_title="MedPredict Test",
    page_icon="logo.png",
    layout="centered"
)

# 🖼️ Afficher logo
try:
    st.image("logo.png", width=120)
except:
    st.warning("Logo non trouvé.")

# 🏷️ Titre
st.title("🧪 MedPredict - Version Test Interface")

# 📋 Champs texte
st.text_input("Equipment Name", placeholder="Surgical Microscope")
st.text_input("Company", placeholder="Leica")
st.text_input("Model", placeholder="Provido")

# 📂 Upload (fictif)
st.file_uploader("Upload Logs (Excel .xlsx)", type=["xlsx"])
st.file_uploader("Upload Technical Manual (PDF)", type=["pdf"])

# ✅ Bouton test
if st.button("Tester le bouton"):
    st.success("🎉 Le front-end fonctionne correctement !")

# 📌 Footer
st.markdown(
    """
    <hr style="border:1px solid #f0f0f0">
    <div style="text-align: center; color: #888888; font-size: 14px;">
        © MedPredict 2025 - Interface test
    </div>
    """,
    unsafe_allow_html=True
)
