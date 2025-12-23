import streamlit as st
import whisper
from pathlib import Path
import os
import time

# --------------------
# CONFIG & DESIGN (Noir & Vert OneTwo)
# --------------------
st.set_page_config(page_title="OneTwo - Le Transcripteur", layout="wide")

st.markdown(
    """
    <style>
    html, body, [data-testid="stApp"] { 
        background-color: #000000 !important; 
        color: #61F885 !important; 
    }
    section.main { background-color: #000000 !important; }
    
    div, p, span, label, h1, h2, h3, h4, h5, h6 { 
        color: #61F885 !important; 
        background-color: transparent !important; 
    }

    .stButton > button { 
        background-color: #000000 !important; 
        color: #61F885 !important; 
        border: 2px solid #61F885 !important; 
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
        height: 3em;
    }
    .stButton > button:hover { 
        background-color: #61F885 !important; 
        color: #000000 !important; 
    }

    [data-testid="stFileUploader"] { 
        background-color: #000000 !important; 
        border: 2px dashed #61F885 !important; 
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------
# CHARGEMENT DU MODÈLE
# --------------------
@st.cache_resource
def load_model():
    return whisper.load_model("small")

model = load_model()

def format_timestamp(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")

# --------------------
# INTERFACE PRINCIPALE
# --------------------
col_left, col_center, col_right = st.columns([1, 2, 1])

with col_center:
    if Path("img_83hf92z_01.png").exists():
        st.image("img_83hf92z_01.png", use_container_width=True)
    
    st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>OneTwo OneTwo</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; margin-top: 0;'>Le Transcripteur</h2>", unsafe_allow_html=True)
    st.markdown("---")

    uploaded_file = st.file_uploader(
        "Déposez votre fichier (MP3, WAV, M4A)",
        type=["mp3", "wav", "m4a"]
    )

    if uploaded_file:
        if st.button("LANCER LE TRANSCRIPTEUR"):
            audio_path = f"/tmp/{uploaded_file.name}"
            with open(audio_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                status_text.markdown("✨ *Initialisation du moteur IA...*")
                progress_bar.progress(20)
                
                status_text.markdown("🎙️ *Transcription en cours...*")
                progress_bar.progress(50)
                
                result = model.transcribe(
                    audio_path,
                    language="fr",
                    condition_on_previous_text=False
                )
                
                progress_bar.progress(90)
                status_text.markdown("📝 *Mise en forme des fichiers...*")
                
                segments = result.get("segments", [])
                title = Path(audio_path).stem.upper()
                
                txt_output = f"{title}\n{'='*len(title)}\n\n"
                srt_output = ""
                
                for i, seg in enumerate(segments, 1):
                    time_block = f"{format_timestamp(seg['start'])} --> {format_timestamp(seg['end'])}"
                    txt_output += f"{time_block}\n{seg['text'].strip()}\n\n"
                    srt_output += f"{i}\n{time_block}\n{seg['text'].strip()}\n\n"

                progress_bar.progress(100)
                status_text.empty()
                st.success("✅ Transcription terminée !")

                dl_col1, dl_col2 = st.columns(2)
                dl_col1.download_button("📥 Télécharger TXT", txt_output, file_name=f"{title}.txt")
                dl_col2.download_button("📥 Télécharger SRT", srt_output, file_name=f"{title}.srt")
                
                with st.expander("👁️ Voir l'aperçu du texte"):
                    st.text(txt_output)

            except Exception as e:
                st.error(f"❌ Erreur : {e}")
            finally:
                if os.path.exists(audio_path):
                    os.remove(audio_path)

# --------------------
# PIED DE PAGE
# --------------------
st.markdown("---")
st.markdown("<p style='text-align: center; color: #61F885;'>OneTwo<br>Usage Interne</p>", unsafe_allow_html=True)
