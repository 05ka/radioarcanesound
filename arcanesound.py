import streamlit as st
import os
import random
import cv2
import numpy as np
from itertools import cycle
from PIL import Image
import time

st.set_page_config(layout="wide")

# Ocultar elementos específicos y agregar estilos
st.markdown("""
    <style>
        header {visibility: hidden;}
        [data-testid="stStatusWidget"] {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {visibility: hidden;}
        .css-k1ih3n { margin-top: 1px; }
        
        /* Estilos para los controles en el footer */
        .footer-controls {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: rgba(0, 0, 0, 0.7);
            padding: 20px;
            z-index: 1000;
        }
        
        /* Estilo para los controles */
        .stSlider {
            background-color: rgba(255, 255, 255, 0.1);
            padding: 10px;
            border-radius: 10px;
        }
        
        /* Estilo para los botones */
        .stButton>button {
            border-radius: 20px;
            padding: 10px 20px;
            background-color: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            background-color: rgba(255, 255, 255, 0.3);
            border-color: rgba(255, 255, 255, 0.5);
        }
        
        /* Ajuste para dejar espacio para los controles */
        .main-content {
            margin-bottom: 100px;
        }
    </style>
""", unsafe_allow_html=True)

# Configurar el video de fondo
st.markdown("""
    <style>
        #myVideo {
            position: fixed;
            right: 0;
            bottom: 0;
            min-width: 100%;
            min-height: 100%;
        }
    </style>
    <video autoplay muted loop id="myVideo">
        <source src="https://static.streamlit.io/examples/star.mp4" type="video/mp4">
        Tu navegador no admite video HTML5.
    </video>
""", unsafe_allow_html=True)

# Define folders, pause duration, and loading logic
folders = ["1", "2", "3"]

def load_all_matching_files(folder):
    image_files = [f for f in os.listdir(folder) if f.endswith(".png")]
    sound_files = set(f for f in os.listdir(folder) if f.endswith(".mp3"))
    matching_files = []
    for image in image_files:
        sound = os.path.splitext(image)[0] + '.mp3'
        if sound in sound_files:
            matching_files.append((image, sound))
    random.shuffle(matching_files)
    return matching_files

def fade_transition(img1, img2, duration):
    for i in np.linspace(0, 1, duration):
        dst = cv2.addWeighted(img1, 1 - i, img2, i, 0)
        yield dst

def main():
    # Inicializar variables de estado
    if 'playing' not in st.session_state:
        st.session_state.playing = True
    if 'speed' not in st.session_state:
        st.session_state.speed = 1.0
    if 'volume' not in st.session_state:
        st.session_state.volume = 0.5
    if 'pause_duration' not in st.session_state:
        st.session_state.pause_duration = 8000
    if 'current_images' not in st.session_state:
        st.session_state.current_images = [None] * len(folders)
    if 'audio_key' not in st.session_state:
        st.session_state.audio_key = 0
    if 'folder_sounds_binary' not in st.session_state:
        st.session_state.folder_sounds_binary = {}
    
    # Contenedor principal para las imágenes
    main_container = st.container()
    with main_container:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        cols = st.columns(len(folders))
        image_placeholders = [col.empty() for col in cols]
        
        # Mostrar las imágenes actuales si existen
        for i, img in enumerate(st.session_state.current_images):
            if img is not None:
                image_placeholders[i].image(img, caption=None, use_container_width=True)
    
    # Panel de control en el footer
    footer = st.container()
    with footer:
        st.markdown('<div class="footer-controls">', unsafe_allow_html=True)
        control_cols = st.columns([1,1,1])
        
        with control_cols[0]:
            if st.button("⏯️ Play/Pause"):
                st.session_state.playing = not st.session_state.playing
        
        with control_cols[1]:
            st.session_state.speed = st.slider(
                "Velocidad de reproducción",
                min_value=0.5,
                max_value=2.0,
                value=st.session_state.speed,
                step=0.1,
                format="%.1fx"
            )
        
        with control_cols[2]:
            st.session_state.volume = st.slider(
                "Volumen",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.volume,
                step=0.1,
                format="%.1f"
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # Load images and sounds
    folder_images = {}
    folder_sounds = {}
    for folder in folders:
        pairs = load_all_matching_files(folder)
        folder_images[folder] = [p[0] for p in pairs]
        folder_sounds[folder] = [p[1] for p in pairs]

    # Load audio files and save into session_state.folder_sounds_binary
    if not st.session_state.folder_sounds_binary:
        for folder in folders:
            st.session_state.folder_sounds_binary[folder] = []
            for sound_file in folder_sounds[folder]:
                sound_path = os.path.join(folder, sound_file)
                with open(sound_path, "rb") as f:
                    st.session_state.folder_sounds_binary[folder].append(f.read())
    
    # Initialize indexes
    indexes = {folder: cycle(range(len(folder_images[folder]))) for folder in folders}
    already_selected = set()

    # Placeholder for audio player
    audio_placeholder = st.empty()

    def update_display():
        nonlocal already_selected

        if not st.session_state.playing:
            time.sleep(0.1)
            return

        already_selected.clear()
        
        audio_binaries = []

        for i, folder in enumerate(folders):
            img_idx = next(indexes[folder])

            # Prevent duplicates
            original_img_idx = img_idx
            while folder_images[folder][img_idx] in already_selected:
                img_idx = next(indexes[folder])
                if img_idx == original_img_idx:
                    break

            already_selected.add(folder_images[folder][img_idx])

            img_path = os.path.join(folder, folder_images[folder][img_idx])
            audio_binaries.append(st.session_state.folder_sounds_binary[folder][img_idx])


            # Display image with fade transition
            prev_img = cv2.imread(img_path) if st.session_state.current_images[i] is None else \
                      cv2.cvtColor(np.array(st.session_state.current_images[i]), cv2.COLOR_RGB2BGR)
            
            img = cv2.imread(img_path)
            for faded_img in fade_transition(prev_img, img, int(74 / st.session_state.speed)):
                pil_image = Image.fromarray(cv2.cvtColor(faded_img.astype(np.uint8), cv2.COLOR_BGR2RGB))
                image_placeholders[i].image(pil_image, caption=None, use_container_width=True)
                st.session_state.current_images[i] = pil_image

        #Reproducir audio usando un reproductor HTML5 y Javascript
        if st.session_state.playing:
            audio_data = audio_binaries[st.session_state.audio_key % len(audio_binaries)]
            audio_placeholder.audio(audio_data) #The magic happens here
            st.session_state.audio_key += 1


        if st.session_state.playing:
            time.sleep((st.session_state.pause_duration / 1300) / st.session_state.speed)

        
    # Javascript for auto playing the audio
    st.markdown(
        """
            <script>
            var audio = document.querySelectorAll('audio');
            if (audio.length > 0){
                audio[audio.length -1].play();
            }
        
            </script>
        """, unsafe_allow_html=True
    )

    # Automatic loop
    while True:
        update_display()
        st.experimental_rerun()

if __name__ == "__main__":
    main()
