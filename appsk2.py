import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from fpdf import FPDF
import os

# ================= 1. CẤU HÌNH & FONT =================
st.set_page_config(page_title="AI Health Pro 2026", layout="wide")

def create_pdf(name, score, status, bmi, tips):
    pdf = FPDF()
    pdf.add_page()
    
    # Kiểm tra font để hỗ trợ Tiếng Việt
    font_path = "Roboto-Regular.ttf"
    if os.path.exists(font_path):
        pdf.add_font("Roboto", "", font_path)
        pdf.set_font("Roboto", size=12)
        f_name = "Roboto"
    else:
        pdf.set_font("Arial", size=12)
        f_name = "Arial"
        st.warning("⚠️ Không tìm thấy file Roboto-Regular.ttf. PDF sẽ dùng font mặc định (không dấu).")

    pdf.set_font(f_name, size=16)
    pdf.cell(200, 10, txt="BÁO CÁO SỨC KHỎE AI", ln=True, align='C')
    
    pdf.set_font(f_name, size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Họ tên: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Điểm số: {score:.1f}/100", ln=True)
    pdf.cell(200, 10, txt=f"Trạng thái: {status}", ln=True)
    pdf.cell(200, 10, txt=f"BMI: {bmi}", ln=True)
    
    pdf.ln(10)
    pdf.cell(200, 10, txt="Lời khuyên từ AI:", ln=True)
    for t in tips:
        pdf.multi_cell(0, 10, txt=f"- {t}")
        
    # fpdf2 không cần .encode('latin-1'), gọi .output() là đủ
    return pdf.output()

# ================= 2. MODEL AI =================
@st.cache_resource
def train_model():
    np.random.seed(42)
    data = pd.DataFrame({
        "Sleep": np.random.uniform(4, 10, 500),
        "Exercise": np.random.uniform(0, 3, 500),
        "Water": np.random.uniform(1, 4, 500),
        "Stress": np.random.uniform(1, 10, 500),
        "BMI": np.random.uniform(17, 30, 500)
    })
    data["Score"] = (data["Sleep"]*5 + data["Exercise"]*15 + data["Water"]*4 - data["Stress"]*3 - abs(data["BMI"]-22)*3 + 40)
    model = RandomForestRegressor(n_estimators=50)
    model.fit(data[["Sleep", "Exercise", "Water", "Stress", "BMI"]], data["Score"].clip(0,100))
    return model

model = train_model()

# ================= 3. GIAO DIỆN =================
with st.sidebar:
    st.header("⚙️ Nhập thông số")
    name = st.text_input("Họ tên", "Người dùng")
    weight = st.number_input("Cân nặng (kg)", 40, 150, 65)
    height = st.number_input("Chiều cao (cm)", 100, 220, 170)
    bmi = round(weight / ((height/100)**2), 1)
    
    sleep = st.slider("Giờ ngủ", 0.0, 12.0, 7.0)
    exer = st.slider("Vận động", 0.0, 5.0, 1.0)
    water = st.slider("Nước (L)", 0.0, 5.0, 2.0)
    stress = st.slider("Căng thẳng", 1, 10, 5)
    
    run_btn = st.button("🚀 PHÂN TÍCH", type="primary", use_container_width=True)

if run_btn or 'analyzed' in st.session_state:
    st.session_state.analyzed = True
    
    score = model.predict([[sleep, exer, water, stress, bmi]])[0]
    status = "Khỏe mạnh" if score > 75 else "Cần cải thiện"
    
    st.title(f"Kết quả của {name}")
    st.metric("Điểm Sức Khỏe AI", f"{score:.1f}")
    
    tips = ["Duy trì uống đủ nước mỗi ngày.", "Nên vận động nhẹ nhàng sau giờ làm việc."]
    
    # Nút tải PDF
    pdf_bytes = create_pdf(name, score, status, bmi, tips)
    st.download_button(
        label="📥 Tải Báo Cáo PDF (Tiếng Việt)",
        data=bytes(pdf_bytes),
        file_name=f"Bao_cao_{name}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
