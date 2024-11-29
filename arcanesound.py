import streamlit as st
import os
import random
import cv2
import pygame
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
    # Initialize state variables
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
    if 'audio_enabled' not in st.session_state:
        st.session_state.audio_enabled = True

    # Try initializing pygame audio
    try:
        pygame.init()
        pygame.mixer.init()
    except (pygame.error, Exception) as e:
        st.session_state.audio_enabled = False
        st.warning("Audio playback is disabled due to system limitations.")

    # [Rest of the interface code remains the same until update_display()]

    def update_display():
        nonlocal already_selected

        if not st.session_state.playing:
            time.sleep(0.1)
            return

        already_selected.clear()

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
            sound_path = os.path.join(folder, folder_sounds[folder][img_idx])

            # Display image with fade transition
            prev_img = cv2.imread(img_path) if st.session_state.current_images[i] is None else \
                      cv2.cvtColor(np.array(st.session_state.current_images[i]), cv2.COLOR_RGB2BGR)
            
            img = cv2.imread(img_path)
            for faded_img in fade_transition(prev_img, img, int(74 / st.session_state.speed)):
                pil_image = Image.fromarray(cv2.cvtColor(faded_img.astype(np.uint8), cv2.COLOR_BGR2RGB))
                image_placeholders[i].image(pil_image, caption=None, use_container_width=True)
                st.session_state.current_images[i] = pil_image

            # Play sound only if audio is enabled
            if st.session_state.playing and st.session_state.audio_enabled:
                try:
                    sound = pygame.mixer.Sound(sound_path)
                    sound.set_volume(st.session_state.volume)
                    sound.play()
                    time.sleep(sound.get_length() / st.session_state.speed)
                except (pygame.error, FileNotFoundError) as e:
                    pass  # Silently continue if sound file can't be played

        if st.session_state.playing:
            time.sleep((st.session_state.pause_duration / 1300) / st.session_state.speed)

    # Automatic loop
    while True:
        update_display()

if __name__ == "__main__":
    main()
