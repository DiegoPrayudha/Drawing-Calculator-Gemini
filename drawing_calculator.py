import pandas as pd
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas
import cv2
import numpy as np
from dotenv import load_dotenv
import os
import google.generativeai as genai
import base64
import io

# Load environment variables
load_dotenv()

# Konfigurasi Gemini API
genai.configure(api_key=os.getenv('API_KEY'))

# Fungsi untuk mengkonversi gambar ke base64
def image_to_base64(image):
    # Konversi gambar OpenCV ke PIL Image
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    # Simpan ke buffer
    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG")
    
    # Encode ke base64
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

# Fungsi untuk memproses gambar dengan Gemini
def process_image_with_gemini(image):
    # Konfigurasi model
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Konversi gambar ke base64
    base64_image = image_to_base64(image)
    
    # Kirim prompt ke Gemini
    response = model.generate_content([
        "Tolong baca dan hitung ekspresi matematika yang ada di gambar ini. " + 
        "Hanya berikan jawaban numeriknya saja, tanpa penjelasan tambahan. " +
        "Jika tidak bisa membaca atau menghitung, kembalikan pesan 'Tidak Bisa Dibaca'." + 
        "Tambahkan penjelasan dibawahnya dalam bentuk langkah langkah",  
        {
            "mime_type": "image/png",
            "data": base64_image
        }
    ])
    
    return response.text

# Konfigurasi Streamlit
st.title("Drawing Calculator")

drawing_mode = st.sidebar.selectbox(
    "Drawing tool:", ("freedraw", "line", "rect", "circle")
)

stroke_width = st.sidebar.slider("Stroke width: ", 1, 25, 3)
stroke_color = st.sidebar.color_picker("Stroke color hex: ")
bg_color = st.sidebar.color_picker("Background color hex: ", "#ffffff")

# Canvas
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=500,
    drawing_mode=drawing_mode,
    key="canvas",
)

# Tombol hitung
if st.button("Hitung"):
    if canvas_result.image_data is not None:
        # Konversi dari RGBA ke BGR
        img = cv2.cvtColor(canvas_result.image_data, cv2.COLOR_RGBA2BGR)
        
        try:
            # Proses gambar dengan Gemini
            result = process_image_with_gemini(img)
            
            # Tampilkan hasil
            st.write(f"Hasil: {result}")
            
        except Exception as e:
            st.error(f"Error dalam pemrosesan: {e}")
    else:
        st.error("Silakan gambar sesuatu terlebih dahulu")