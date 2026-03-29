import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

# --- CẤU HÌNH HỆ THỐNG ---
st.set_page_config(page_title="AI Health Prognosis Pro", layout="wide")

def create_pdf_final(name, res, diet):
    try:
        # Sử dụng fpdf2 để fix lỗi Unicode và tràn khung
        pdf = FPDF()
        pdf.add_page()
        
        # Sử dụng file font bạn đã upload
        font_path = "Roboto-VariableFont_wdth,wght.ttf"
        if os.path.exists(font_path):
            pdf.add_font("Roboto", "", font_path)
            pdf.set_font("Roboto", size=12)
            f_name = "Roboto"
        else:
            pdf.set_font("Arial", size=12)
            f_name = "Arial"

        pdf.set_font(f_name, 'B', 16)
        pdf.cell(0, 10, txt="BAO CAO SUC KHOE CHUYEN SAU 2026", ln=True, align='C')
        pdf.ln(5)

        pdf.set_font(f_name, size=12)
        pdf.cell(0, 10, txt=f"Khach hang: {name}", ln=True)
        pdf.cell(0, 10, txt=f"Tuoi tho du bao: {res['Lifespan']} tuoi", ln=True)
        pdf.ln(5)

        # Fix lỗi UnicodeEncodeError bằng cách làm sạch text
        risk_txt = "Nguy co: " + ", ".join(res['Risks'])
        # Fix lỗi FPDFException bằng multi_cell
        pdf.multi_cell(0, 8, txt=risk_txt) 
        pdf.ln(5)
        pdf.multi_cell(0, 8, txt=f"Thuc don goi y: {diet}")

        return pdf.output()
    except Exception as e:
        st.error(f"Loi PDF: {e}")
        return None

# --- LOGIC DỰ BÁO THỰC TẾ ---
def run_analysis(age, w, h, sleep, exer, stress, water):
    bmi = round(w / ((h/100)**2), 1)
    
    # Thuật toán dự báo tuổi thọ thực tế (Dựa trên mức nền 75 tuổi)
    life = 75.0 + (sleep - 7.5)*0.8 + (exer*1.5) - (stress - 4)*0.7 - abs(bmi - 22.5)*0.5
    final_life = np.clip(life, 62.0, 95.0) # Đảm bảo con số thực tế

    # Suy luận chỉ số ẩn
    bp_sys = int(110 + (age * 0.2) + (bmi - 22)*1.2 + (stress * 0.5))
    
    risks = []
    if bp_sys > 135: risks.append("Cao huyet ap")
    if bmi > 25: risks.append("Roi loan chuyen hoa")
    if stress > 7: risks.append("Cang thang man tinh")
    if not risks: risks.append("Suc khoe on dinh")

    return {"BMI": bmi, "Lifespan": round(final_life, 1), "BP": f"{bp_sys}/85", "Risks": risks}

# --- GIAO DIỆN ---
st.title("🏥 AI Health Intelligence Pro")

with st.sidebar:
    name = st.text_input("Ho ten", "User")
    age = st.number_input("Tuoi", 18, 100, 30)
    w = st.number_input("Can nang (kg)", 40.0, 150.0, 68.0)
    h = st.number_input("Chieu cao (cm)", 140, 210, 170)
    st.divider()
    sl = st.slider("Gio ngu", 0.0, 12.0, 7.5)
    ex = st.slider("Van dong (h)", 0.0, 5.0, 1.0)
    st_val = st.slider("Stress", 1, 10, 5)
    btn = st.button("PHAN TICH", type="primary")

if btn:
    res = run_analysis(age, w, h, sl, ex, st_val, 2.0)
    
    c1, c2 = st.columns(2)
    c1.metric("Tuoi tho dự báo", f"{res['Lifespan']} tuổi")
    c2.metric("Huyết áp ước tính", f"{res['BP']} mmHg")

    st.write("### ⚠️ Cảnh báo:")
    for r in res['Risks']: st.warning(r)

    # Xuất PDF sạch lỗi
    pdf_data = create_pdf_final(name, res, "Tang cuong rau xanh, giam tinh bot")
    if pdf_data:
        st.download_button("📥 Tải báo cáo PDF", data=bytes(pdf_data), file_name="Health_AI.pdf")
