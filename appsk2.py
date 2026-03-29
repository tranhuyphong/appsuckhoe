import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from fpdf import FPDF
import os

# ================= 1. HÀM TẠO PDF CHỐNG LỖI =================
def create_pdf(name, score, status, bmi, tips):
    # Sử dụng fpdf2 để xử lý Unicode tốt hơn
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    
    # Đường dẫn font
    font_path = "Roboto-Regular.ttf"
    if os.path.exists(font_path):
        pdf.add_font("Roboto", "", font_path)
        pdf.set_font("Roboto", size=12)
        f_family = "Roboto"
    else:
        pdf.set_font("Helvetica", size=12)
        f_family = "Helvetica"
        st.warning("⚠️ Đang dùng font dự phòng (không dấu).")

    # Tiêu đề
    pdf.set_font(f_family, size=16)
    pdf.cell(0, 10, txt="BÁO CÁO SỨC KHỎE AI", ln=True, align='C')
    pdf.ln(10)
    
    # Nội dung chính
    pdf.set_font(f_family, size=12)
    pdf.cell(0, 10, txt=f"Họ tên: {name}", ln=True)
    pdf.cell(0, 10, txt=f"Điểm số: {score:.1f}/100", ln=True)
    pdf.cell(0, 10, txt=f"Trạng thái: {status}", ln=True)
    pdf.cell(0, 10, txt=f"BMI: {bmi}", ln=True)
    
    pdf.ln(5)
    pdf.cell(0, 10, txt="Lời khuyên từ chuyên gia AI:", ln=True)
    
    # multi_cell với chiều rộng tự động (w=0) để tránh lỗi không gian
    pdf.set_font(f_family, size=10)
    for t in tips:
        pdf.multi_cell(0, 8, txt=f"- {t}", border=0)
        
    return pdf.output()

# ================= 2. LOGIC ỨNG DỤNG =================
@st.cache_resource
def load_ai():
    np.random.seed(42)
    X = np.random.rand(100, 5) * 10
    y = X.sum(axis=1)
    model = RandomForestRegressor(n_estimators=10).fit(X, y)
    return model

model = load_ai()

# Giao diện nhập liệu
st.title("💪 AI Health Checker")
with st.sidebar:
    name = st.text_input("Tên", "Khách hàng")
    w = st.number_input("Cân nặng", 40, 120, 60)
    h = st.number_input("Chiều cao (cm)", 100, 200, 165)
    bmi = round(w / ((h/100)**2), 1)
    slp = st.slider("Ngủ", 0, 12, 7)
    ex = st.slider("Vận động", 0, 5, 1)
    wat = st.slider("Nước", 0, 5, 2)
    strss = st.slider("Stress", 1, 10, 5)

if st.button("🚀 Phân tích & Xuất PDF"):
    score = (slp*5 + ex*10 + wat*5 - strss*2 + 40)
    score = min(max(score, 0), 100)
    status = "Tốt" if score > 70 else "Cần cố gắng"
    
    st.success(f"Điểm của bạn: {score:.1f}")
    
    tips = [
        "Hãy duy trì thói quen uống nước đều đặn.",
        "Ngủ đủ giấc là chìa khóa của sự phục hồi.",
        "Cân nhắc tập thể dục nhẹ nhàng 30 phút mỗi ngày."
    ]
    
    # Xuất PDF
    try:
        pdf_data = create_pdf(name, score, status, bmi, tips)
        st.download_button(
            "📥 Tải Báo Cáo PDF",
            data=bytes(pdf_data),
            file_name=f"Health_Report_{name}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Lỗi tạo PDF: {e}")
