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
    page_icon="logo.png",  # Favicon logo
    layout="centered"
)

# 🖼️ Afficher le logo en haut
st.image("logo.png", width=120)

# 🏷️ Titre principal
st.title("MedPredict - Maintenance Prédictive")
st.write("Bienvenue sur votre application de maintenance prédictive.")

# 📋 Champs d'informations
equipment_name = st.text_input("Equipment Name", placeholder="Surgical Microscope")
company = st.text_input("Company", placeholder="Leica")
model = st.text_input("Model", placeholder="Provido")

# 📂 Upload fichiers
log_file = st.file_uploader("Upload Logs (Excel .xlsx)", type=["xlsx"])
manual_file = st.file_uploader("Upload Technical Manual (PDF)", type=["pdf"])

# 📦 Charger modèle et scaler
try:
    model_pfe = joblib.load("modele_pfe.pkl")
    scaler_pfe = joblib.load("scaler_pfe.pkl")
except Exception as e:
    st.error("❌ Impossible de charger le modèle. Vérifiez les fichiers modele_pfe.pkl et scaler_pfe.pkl.")
    st.stop()

# 📑 Extraire actions recommandées du PDF
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

# 📥 Fonction pour télécharger Excel
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Results')
        writer.save()
    processed_data = output.getvalue()
    return processed_data

# 🔔 Jouer son d'alarme
def play_alert():
    audio_file = open('alert.mp3', 'rb')
    audio_bytes = audio_file.read()
    b64 = base64.b64encode(audio_bytes).decode()
    md = f"""
    <audio autoplay="true">
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)

# 🚀 Bouton Submit
if st.button("Submit"):
    if equipment_name and company and model and log_file and manual_file:
        st.success("✅ Informations et fichiers chargés avec succès.")

        try:
            # 📊 Lire fichier Excel
            data = pd.read_excel(log_file)
            st.write("✅ Données chargées :")
            st.dataframe(data.head())

            # 🔄 Prétraitement
            numeric_data = data.select_dtypes(include=['float64', 'int64'])
            data_scaled = scaler_pfe.transform(numeric_data)

            # 🤖 Prédictions
            predictions = model_pfe.predict(data_scaled)
            data['Prediction'] = predictions

            # 📑 Actions recommandées
            actions = extract_actions_from_pdf(manual_file)
            data['Recommended Action'] = data['Prediction'].map(actions)

            # 📊 Afficher résultat
            st.write("### 🔥 Résultat avec Actions Recommandées :")
            st.dataframe(data)

            # 📥 Bouton téléchargement Excel
            excel_data = to_excel(data)
            st.download_button(
                label="📥 Download Results as Excel",
                data=excel_data,
                file_name="medpredict_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # 🚨 POP-UP et Alarme
            if "Failure" in predictions:
                st.error("⚠️ Panne détectée ! Une alarme sonnera 30 minutes avant l'événement.")
                
                # Simuler l'attente de 30 minutes (pour test : réduire à 5 secondes)
                # time.sleep(1800)  # 30 min réelles
                time.sleep(5)  # ⏱️ pour test rapide
                
                play_alert()

        except Exception as e:
            st.error(f"❌ Erreur lors du traitement : {e}")

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
