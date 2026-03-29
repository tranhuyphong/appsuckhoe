import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from fpdf import FPDF
import os

# 1. CẤU HÌNH & XỬ LÝ FONT
st.set_page_config(page_title="AI Health Infinity Pro", layout="wide")

def create_pdf_pro(name, res, diet):
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Kiểm tra file font bạn đã up lên (Dựa theo ảnh image_c74895.png)
        font_path = "Roboto-VariableFont_wdth,wght.ttf"
        if os.path.exists(font_path):
            pdf.add_font("Roboto", "", font_path)
            pdf.set_font("Roboto", size=12)
            f = "Roboto"
        else:
            pdf.set_font("Arial", size=12)
            f = "Arial"

        pdf.cell(0, 10, txt=f"BAO CAO SUC KHOE: {name.upper()}", ln=True, align='C')
        pdf.ln(5)
        pdf.cell(0, 10, txt=f"- Tuoi tho du kien: {res['Lifespan']} tuoi", ln=True)
        pdf.multi_cell(0, 10, txt=f"- Nguy co: {', '.join(res['Risks'])}".encode('utf-8').decode('latin-1', 'ignore'))
        pdf.multi_cell(0, 10, txt=f"- Thuc don: {diet}".encode('utf-8').decode('latin-1', 'ignore'))
        
        return pdf.output()
    except Exception as e:
        return None

# 2. ENGINE AI
def analyze_health(age, w, h, sleep, exer, stress):
    bmi = round(w / ((h/100)**2), 1)
    hr = int(72 + (stress * 1.5) - (exer * 3))
    lifespan = 75 + (sleep-7) + (exer*2) - (stress*0.5)
    risks = ["On dinh"]
    if bmi > 25: risks = ["Tim mach", "Tieu duong"]
    return {"BMI": bmi, "HR": hr, "Lifespan": lifespan, "Risks": risks}

# 3. GIAO DIEN
with st.sidebar:
    st.header("Nhap chi so")
    name = st.text_input("Ten", "User")
    age = st.number_input("Tuoi", 18, 100, 25)
    w = st.number_input("Can nang", 40, 120, 65)
    h = st.number_input("Chieu cao", 140, 200, 170)
    sleep = st.slider("Gio ngu", 4, 12, 7)
    exer = st.slider("Van dong", 0, 5, 1)
    stress = st.slider("Stress", 1, 10, 5)
    btn = st.button("PHAN TICH NGAY")

if btn:
    res = analyze_health(age, w, h, sleep, exer, stress)
    st.title(f"Ket qua cho {name}")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Tuoi tho", f"{res['Lifespan']} nam")
    c2.metric("BMI", res['BMI'])
    c3.metric("Nhip tim", f"{res['HR']} bpm")
    
    st.write("### Nguy co benh ly:", ", ".join(res['Risks']))
    
    # Xuat PDF
    pdf_bytes = create_pdf_pro(name, res, "An nhieu rau xanh, giam tinh bot")
    if pdf_bytes:
        st.download_button("Tai bao cao PDF", data=bytes(pdf_bytes), file_name="Health_Report.pdf")
