import streamlit as st
import os
import random
import cv2
import numpy as np
from itertools import cycle
from PIL import Image
import time
import sounddevice as sd
import soundfile as sf

def init_session_state():
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
    if 'last_update' not in st.session_state:
        st.session_state.last_update = time.time()

def load_all_matching_files(folder):
    image_files = [f for f in os.listdir(folder) if f.endswith(".png")]
    sound_files = set(f for f in os.listdir(folder) if f.endswith((".mp3", ".wav")))
    matching_files = []
    for image in image_files:
        base_name = os.path.splitext(image)[0]
        sound = next((s for s in sound_files if s.startswith(base_name)), None)
        if sound:
            matching_files.append((image, sound))
    random.shuffle(matching_files)
    return matching_files

def play_sound(sound_path, volume):
    try:
        data, samplerate = sf.read(sound_path)
        # Ajustar el volumen
        data = data * volume
        # Reproducir el sonido
        sd.play(data, samplerate)
        sd.wait()  # Esperar a que termine la reproducción
    except Exception as e:
        st.error(f"Error playing sound: {str(e)}")

def main():
    st.set_page_config(layout="wide")
    
    # Initialize session state
    init_session_state()
    
    # Apply styles
    st.markdown("""
        <style>
            header {visibility: hidden;}
            .stDeployButton {display: none;}
            footer {visibility: hidden;}
            #MainMenu {visibility: hidden;}
            
            .footer-controls {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background-color: rgba(0, 0, 0, 0.7);
                padding: 20px;
                z-index: 1000;
            }
            
            .stSlider {
                background-color: rgba(255, 255, 255, 0.1);
                padding: 10px;
                border-radius: 10px;
            }
            
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
        </style>
    """, unsafe_allow_html=True)
    
    # Main layout
    main_container = st.container()
    with main_container:
        cols = st.columns(len(folders))
        image_placeholders = [col.empty() for col in cols]
    
    # Controls
    footer = st.container()
    with footer:
        st.markdown('<div class="footer-controls">', unsafe_allow_html=True)
        control_cols = st.columns([1,1,1])
        
        with control_cols[0]:
            if st.button("⏯️ Play/Pause"):
                st.session_state.playing = not st.session_state.playing
                if not st.session_state.playing:
                    sd.stop()
        
        with control_cols[1]:
            st.session_state.speed = st.slider(
                "Velocidad",
                0.5, 2.0, st.session_state.speed,
                step=0.1
            )
        
        with control_cols[2]:
            st.session_state.volume = st.slider(
                "Volumen",
                0.0, 1.0, st.session_state.volume,
                step=0.1
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # Load content
    folder_content = {}
    for folder in folders:
        pairs = load_all_matching_files(folder)
        folder_content[folder] = {
            'images': [p[0] for p in pairs],
            'sounds': [p[1] for p in pairs],
            'index': cycle(range(len(pairs)))
        }

    # Update function
    def update_display():
        if not st.session_state.playing:
            return

        current_time = time.time()
        if current_time - st.session_state.last_update < (st.session_state.pause_duration / 1000) / st.session_state.speed:
            return

        for i, folder in enumerate(folders):
            content = folder_content[folder]
            idx = next(content['index'])
            
            img_path = os.path.join(folder, content['images'][idx])
            sound_path = os.path.join(folder, content['sounds'][idx])
            
            # Load and display image
            img = cv2.imread(img_path)
            if img is not None:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                image_placeholders[i].image(img_rgb, use_container_width=True)
            
            # Play sound
            if st.session_state.playing:
                play_sound(sound_path, st.session_state.volume)

        st.session_state.last_update = current_time

    # Main loop using rerun
    update_display()
    time.sleep(0.1)
    st.experimental_rerun()

if __name__ == "__main__":
    folders = ["1", "2", "3"]  # Define your folders here
    main()
