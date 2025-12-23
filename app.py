import streamlit as st
import whisper
from pathlib import Path
import os

# --------------------
# CONFIG & THEME
# --------------------
st.set_page_config(page_title="OneTwo Transcript", layout="wide")

st.markdown(
    """
    <style>
    html, body, [data-testid="stApp"] { background-color: #000000 !important; color: #61F885 !important; }
    section.main { background-color: #000000 !important; }
    div, p, span, label, h1, h2, h3, h4, h5, h6 { color: #61F885 !important; background-color: transparent !important; }
    .stButton > button { background-color: #000000 !important; color: #61F885 !important; border: 2px solid #61F885 !important; width: 100%; }
    .stButton > button:hover { background-color: #61F885 !important; color: #000000 !important; }
    [data-testid="stFileUploader"] { background-color: #000000 !important; border: 2px dashed #61F885 !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------
# WHISPER (SMALL)
# --------------------
@st.cache_resource
def load_model():
    # Sur le cloud, le modèle sera téléchargé au premier lancement
    return whisper.load_model("small")

model = load_model()

def ts(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")

# --------------------
# LAYOUT
# --------------------
col_center, col_right = st.columns([3, 1])

with col_right:
    if Path("logo_onetwo.png").exists():
        st.image("logo_onetwo.png", width=200)
    st.markdown("### ONETWO ONETWO")
    st.markdown("Le transcripteur officiel")
    st.info("Les fichiers sont traités sur les serveurs Streamlit.")

with col_center:
    st.markdown("## 🎙️ Nouvelle Transcription")
    
    uploaded_file = st.file_uploader(
        "Déposez votre fichier audio (MP3, WAV, M4A)",
        type=["mp3", "wav", "m4a"]
    )

    if uploaded_file:
        if st.button("LANCER LA TRANSCRIPTION"):
            # Utilisation de /tmp pour le cloud
            audio_path = f"/tmp/{uploaded_file.name}"
            with open(audio_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with st.status("⚡ Transcription en cours...", expanded=True) as status:
                try:
                    result = model.transcribe(
                        audio_path,
                        language="fr",
                        condition_on_previous_text=False
                    )
                    
                    segments = result.get("segments", [])
                    title = Path(audio_path).stem.upper()
                    
                    # Préparation des textes
                    txt_output = f"{title}\n{'='*len(title)}\n\n"
                    srt_output = ""
                    
                    for i, seg in enumerate(segments, 1):
                        time_block = f"{ts(seg['start'])} --> {ts(seg['end'])}"
                        txt_output += f"{time_block}\n{seg['text'].strip()}\n\n"
                        
                        srt_output += f"{i}\n{time_block}\n{seg['text'].strip()}\n\n"

                    status.update(label="✅ Terminé !", state="complete", expanded=False)
                    st.success("Fichier prêt !")

                    # Boutons de téléchargement
                    c1, c2 = st.columns(2)
                    c1.download_button("📥 Télécharger TXT", txt_output, file_name=f"{title}.txt")
                    c2.download_button("📥 Télécharger SRT", srt_output, file_name=f"{title}.srt")
                    
                    # Aperçu
                    with st.expander("Voir l'aperçu du texte"):
                        st.text(txt_output)

                except Exception as e:
                    st.error(f"Erreur : {e}")
                finally:
                    # Nettoyage du fichier temporaire
                    if os.path.exists(audio_path):
                        os.remove(audio_path)