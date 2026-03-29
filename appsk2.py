import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

# ================= 1. XỬ LÝ PDF & FONT TIẾNG VIỆT =================
def create_pdf_final(name, res, diet, tips):
    try:
        # Sử dụng FPDF bản chuẩn, fix lỗi tràn khung
        pdf = FPDF()
        pdf.add_page()
        
        # Đường dẫn font Roboto từ thư mục của bạn
        font_path = "Roboto-VariableFont_wdth,wght.ttf"
        if os.path.exists(font_path):
            pdf.add_font("Roboto", "", font_path)
            pdf.set_font("Roboto", size=12)
            f_name = "Roboto"
        else:
            pdf.set_font("Arial", size=12)
            f_name = "Arial"

        # Tiêu đề (Bỏ Emoji để tránh lỗi Unicode)
        pdf.set_font(f_name, 'B', 16)
        pdf.cell(0, 10, txt="BAO CAO SUC KHOE CHUYEN SAU AI 2026", ln=True, align='C')
        pdf.ln(5)

        # Thông tin khách hàng
        pdf.set_font(f_name, size=12)
        pdf.cell(0, 10, txt=f"Khach hang: {name}", ln=True)
        pdf.cell(0, 10, txt=f"Tuoi tho du bao: {res['Lifespan']} tuoi", ln=True)
        pdf.cell(0, 10, txt=f"Chi so BMI: {res['BMI']}", ln=True)
        pdf.ln(5)

        # Nguy cơ & Thực đơn (Dùng multi_cell để tự động xuống dòng)
        pdf.set_font(f_name, 'B', 12)
        pdf.cell(0, 10, txt="Phan tich nguy co benh ly:", ln=True)
        pdf.set_font(f_name, size=11)
        
        # Làm sạch văn bản (Xóa icon để tránh lỗi latin-1)
        risk_txt = ", ".join(res['Risks']).replace('🔴','').replace('🟠','').replace('🟡','')
        pdf.multi_cell(0, 8, txt=risk_txt)
        
        pdf.ln(5)
        pdf.set_font(f_name, 'B', 12)
        pdf.cell(0, 10, txt="Che do dinh duong goi y:", ln=True)
        pdf.set_font(f_name, size=11)
        pdf.multi_cell(0, 8, txt=diet)

        return pdf.output()
    except Exception as e:
        st.error(f"Lỗi PDF: {e}")
        return None

# ================= 2. ENGINE DỰ BÁO THỰC TẾ =================
def run_ai_analysis(age, w, h, sleep, exer, stress, water):
    bmi = round(w / ((h/100)**2), 1)
    
    # 1. Dự báo tuổi thọ (Công thức cân bằng hơn)
    # Tuổi thọ trung bình Việt Nam là ~75.3 tuổi
    life_score = 75
