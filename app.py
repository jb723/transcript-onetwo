import streamlit as st
import whisper
from pathlib import Path
import os
import time

# --------------------
# CONFIG & DESIGN (Noir & Vert OneTwo)
# --------------------
st.set_page_config(page_title="OneTwo Transcript", layout="wide")

st.markdown(
    """
    <style>
    /* Fond noir et texte vert fluo */
    html, body, [data-testid="stApp"] { 
        background-color: #000000 !important; 
        color: #61F885 !important; 
    }
    section.main { background-color: #000000 !important; }
    
    /* Couleurs des textes et titres */
    div, p, span, label, h1, h2, h3, h4, h5, h6 { 
        color: #61F885 !important; 
        background-color: transparent !important; 
    }

    /* Personnalisation des boutons */
    .stButton > button { 
        background-color: #000000 !important; 
        color: #61F885 !important; 
        border: 2px solid #61F885 !important; 
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
    }
    .stButton > button:hover { 
        background-color: #61F885 !important; 
        color: #000000 !important; 
    }

    /* Zone de dépôt de fichier */
    [data-testid="stFileUploader"] { 
        background-color: #000000 !important; 
        border: 2px dashed #61F885 !important; 
    }

    /* Masquer le menu Streamlit pour faire plus "App" */
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
    # Affichage du logo centré
    if Path("logo_onetwo.png").exists():
        st.image("logo_onetwo.png", use_container_width=True)
    
    st.markdown("<h1 style='text-align: center;'>ONETWO TRANSCRIPT</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Outil interne de transcription audio & vidéo</p>", unsafe_allow_html=True)
    st.markdown("---")

    uploaded_file = st.file_uploader(
        "Déposez votre fichier (MP3, WAV, M4A)",
        type=["mp3", "wav", "m4a"]
    )

    if uploaded_file:
        if st.button("LANCER LA TRANSCRIPTION"):
            # Sauvegarde temporaire sur le serveur cloud
            audio_path = f"/tmp/{uploaded_file.name}"
            with open(audio_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # --- BARRE DE PROGRESSION ---
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Étape 1 : Analyse
                status_text.markdown("✨ *Initialisation du moteur IA...*")
                progress_bar.progress(20)
                time.sleep(1) # Petit délai visuel
                
                # Étape 2 : Transcription (C'est ici que l'IA travaille)
                status_text.markdown("🎙️ *Transcription en cours... cela peut prendre quelques minutes.*")
                progress_bar.progress(50)
                
                result = model.transcribe(
                    audio_path,
                    language="fr",
                    condition_on_previous_text=False
                )
                
                # Étape 3 : Mise en forme
                progress_bar.progress(90)
                status_text.markdown("📝 *Mise en forme des fichiers TXT et SRT...*")
                
                segments = result.get("
