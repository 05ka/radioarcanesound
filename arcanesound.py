import streamlit as st
import os
import random
from itertools import cycle
from PIL import Image
import time
import base64

st.set_page_config(layout="wide")

# Estilos
st.markdown("""
    <style>
        header {visibility: hidden;}
        [data-testid="stStatusWidget"] {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {visibility: hidden;}
        .css-k1ih3n { margin-top: 1px; }
        
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
        
        .main-content {
            margin-bottom: 100px;
        }
    </style>
""", unsafe_allow_html=True)

# Video de fondo
st.markdown("""
    <video autoplay muted loop id="myVideo" style="position: fixed; right: 0; bottom: 0; min-width: 100%; min-height: 100%;">
        <source src="https://static.streamlit.io/examples/star.mp4" type="video/mp4">
    </video>
""", unsafe_allow_html=True)

folders = ["1", "2", "3"]

def get_base64_audio(file_path):
    with open(file_path, "rb") as audio_file:
        audio_bytes = audio_file.read()
        b64 = base64.b64encode(audio_bytes).decode()
        return b64

def create_audio_player(audio_b64, volume=0.5):
    audio_html = f"""
        <audio autoplay style="width:100%; display:none">
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>
        <script>
            var audio = document.querySelector('audio');
            audio.volume = {volume};
        </script>
    """
    return audio_html

def load_all_matching_files(folder):
    image_files = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    sound_files = set(f for f in os.listdir(folder) if f.endswith('.mp3'))
    matching_files = []
    for image in image_files:
        sound = os.path.splitext(image)[0] + '.mp3'
        if sound in sound_files:
            matching_files.append((image, sound))
    random.shuffle(matching_files)
    return matching_files

# Initialize session state
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
if 'update_counter' not in st.session_state:
    st.session_state.update_counter = 0

# Main container
main_container = st.container()
with main_container:
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    cols = st.columns(len(folders))
    image_placeholders = [col.empty() for col in cols]
    audio_placeholders = [col.empty() for col in cols]

# Footer controls
footer = st.container()
with footer:
    st.markdown('<div class="footer-controls">', unsafe_allow_html=True)
    control_cols = st.columns([1,1,1])
    
    with control_cols[0]:
        if st.button("⏯️ Play/Pause"):
            st.session_state.playing = not st.session_state.playing
    
    with control_cols[1]:
        st.session_state.speed = st.slider(
            "Velocidad",
            0.5, 2.0, st.session_state.speed,
            step=0.1,
            format="%.1fx"
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

# Update display
if st.session_state.playing:
    for i, folder in enumerate(folders):
        content = folder_content[folder]
        idx = next(content['index'])
        
        img_path = os.path.join(folder, content['images'][idx])
        sound_path = os.path.join(folder, content['sounds'][idx])

        try:
            img = Image.open(img_path)
            image_placeholders[i].image(img, use_column_width=True)
            st.session_state.current_images[i] = img
            
            audio_b64 = get_base64_audio(sound_path)
            audio_html = create_audio_player(audio_b64, st.session_state.volume)
            audio_placeholders[i].markdown(audio_html, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {str(e)}")

    st.session_state.update_counter += 1
    time.sleep((st.session_state.pause_duration / 1300) / st.session_state.speed)
    st.rerun()
