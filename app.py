import streamlit as st
from PIL import Image
import pandas as pd
import joblib
import pypdf
import base64
from io import BytesIO
import time

# 🎨 Config de la page avec logo
st.set_page_config(
    page_title="MedPredict",
    page_icon="logo.png",
    layout="centered"
)

# 🖼️ Afficher le logo en haut
try:
    st.image("logo.png", width=120)
except Exception:
    st.warning("Logo non trouvé.")

st.title("MedPredict - Maintenance Prédictive")
st.write("Bienvenue sur votre application de maintenance prédictive.")

# 📋 Champs
equipment_name = st.text_input("Equipment Name", placeholder="Surgical Microscope")
company = st.text_input("Company", placeholder="Leica")
model = st.text_input("Model", placeholder="Provido")

# 📂 Upload
log_file = st.file_uploader("Upload Logs (Excel .xlsx)", type=["xlsx"])
manual_file = st.file_uploader("Upload Technical Manual (PDF)", type=["pdf"])

# 📦 Charger modèle
try:
    model_pfe = joblib.load("modele_pfe.pkl")
    scaler_pfe = joblib.load("scaler_pfe.pkl")
except Exception as e:
    st.error("❌ Impossible de charger le modèle. Vérifiez les fichiers modele_pfe.pkl et scaler_pfe.pkl.")
    st.stop()

# 📑 Lecture PDF
def extract_actions_from_pdf(pdf_file):
    actions = {}
    reader = pypdf.PdfReader(pdf_file)
    for page in reader.pages:
        text = page.extract_text()
        if text:
            for line in text.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    actions[key.strip()] = value.strip()
    return actions

# 📥 Export Excel
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Results')
    return output.getvalue()

# 🔔 Alarme
def play_alert():
    try:
        with open("alert.mp3", "rb") as audio_file:
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format="audio/mp3", start_time=0)
    except:
        st.warning("Fichier audio d'alerte introuvable.")

# 🚀 Lancer analyse
if st.button("Submit"):
    if equipment_name and company and model and log_file and manual_file:
        st.success("✅ Informations et fichiers chargés.")

        try:
            data = pd.read_excel(log_file)
            st.write("✅ Données chargées :")
            st.dataframe(data.head())

            numeric_data = data.select_dtypes(include=['float64', 'int64'])
            data_scaled = scaler_pfe.transform(numeric_data)

            predictions = model_pfe.predict(data_scaled)
            data['Prediction'] = predictions

            actions = extract_actions_from_pdf(manual_file)
            data['Recommended Action'] = data['Prediction'].map(lambda x: actions.get(str(x), "❗ Non défini"))

            st.write("### 🔥 Résultat avec Actions Recommandées :")
            st.dataframe(data)

            excel_data = to_excel(data)
            st.download_button(
                label="📥 Download Results as Excel",
                data=excel_data,
                file_name="medpredict_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            if any("Failure" in str(p) for p in predictions):
                st.error("⚠️ Panne détectée ! Alarme dans 3 secondes.")
                time.sleep(3)
                play_alert()

        except Exception as e:
            st.error(f"❌ Erreur : {e}")
    else:
        st.error("❌ Veuillez remplir tous les champs et uploader les deux fichiers.")

# 📌 Footer
st.markdown(
    """
    <hr style="border:1px solid #f0f0f0">
    <div style="text-align: center; color: #888888; font-size: 14px;">
        © MedPredict 2025 - Tous droits réservés
    </div>
    """,
    unsafe_allow_html=True
)

print("✅ L'application a bien démarré")

