import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from fpdf import FPDF
import base64

# ================= 1. CẤU HÌNH & CSS =================
st.set_page_config(page_title="AI Health Pro Ultra 2026", page_icon="🧬", layout="wide")

# Hàm tạo file PDF
def create_pdf(name, score, status, bmi, tips):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="BAO CAO SUC KHOE AI 2026", ln=True, align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Ho ten: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Diem suc khoe: {score:.1f}/100", ln=True)
    pdf.cell(200, 10, txt=f"Trang thai: {status}", ln=True)
    pdf.cell(200, 10, txt=f"Chi so BMI: {bmi}", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Loi khuyen tu AI:", ln=True)
    pdf.set_font("Arial", size=10)
    for tip in tips:
        pdf.multi_cell(0, 10, txt=f"- {tip}")
        
    return pdf.output(dest='S').encode('latin-1')

# ================= 2. MODEL AI =================
@st.cache_resource
def load_model():
    np.random.seed(42)
    data = pd.DataFrame({
        "Sleep": np.random.uniform(4, 10, 500),
        "Exercise": np.random.uniform(0, 3, 500),
        "Water": np.random.uniform(1, 4, 500),
        "Stress": np.random.uniform(1, 10, 500),
        "BMI": np.random.uniform(17, 30, 500)
    })
    data["Score"] = (data["Sleep"]*5 + data["Exercise"]*15 + data["Water"]*4 - data["Stress"]*3 - abs(data["BMI"]-22)*3 + 40)
    model = RandomForestRegressor(n_estimators=100)
    model.fit(data[["Sleep", "Exercise", "Water", "Stress", "BMI"]], data["Score"].clip(0,100))
    return model

model = load_model()

# ================= 3. GIAO DIỆN NHẬP LIỆU =================
with st.sidebar:
    st.header("👤 Thông tin cá nhân")
    name = st.text_input("Tên của bạn", "User Pro")
    weight = st.number_input("Cân nặng (kg)", 40, 150, 65)
    height = st.number_input("Chiều cao (cm)", 100, 220, 170)
    bmi = round(weight / ((height/100)**2), 1)
    
    st.divider()
    sleep = st.slider("Giờ ngủ", 0.0, 12.0, 7.0)
    exercise = st.slider("Vận động", 0.0, 4.0, 1.0)
    water = st.slider("Nước (L)", 0.0, 5.0, 2.0)
    stress = st.slider("Stress", 1, 10, 4)
    
    run = st.button("🔥 PHÂN TÍCH NGAY", use_container_width=True, type="primary")

# ================= 4. HIỂN THỊ KẾT QUẢ =================
if run or 'analyzed' in st.session_state:
    st.session_state.analyzed = True
    score = model.predict([[sleep, exercise, water, stress, bmi]])[0]
    status = "Tốt" if score > 75 else "Cần chú ý" if score > 50 else "Nguy cơ cao"
    
    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Score", f"{score:.1f}")
    c2.metric("BMI", bmi)
    c3.metric("Status", status)

    # Lời khuyên
    tips = []
    if sleep < 7: tips.append("Ban nen ngu them de phuc hoi co the.")
    if exercise < 1: tips.append("Tang cuong van dong it nhat 30 phut moi ngay.")
    if water < 2: tips.append("Uong du 2L nuoc de thanh loc co the.")
    if stress > 6: tips.append("Hay tap thien hoac nghe nhac de giam stress.")
    if not tips: tips.append("Moi chi so deu tuyet voi, hay duy tri nhe!")

    st.write("### 🤖 Lời khuyên từ AI")
    for t in tips:
        st.info(t)

    # NÚT XUẤT PDF
    st.divider()
    pdf_bytes = create_pdf(name, score, status, bmi, tips)
    st.download_button(
        label="📥 Tải Báo Cáo Sức Khỏe (PDF)",
        data=pdf_bytes,
        file_name=f"Health_Report_{name}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

    # Phần Chat AI bên dưới
    st.write("### 💬 Chat với chuyên gia AI")
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    if prompt := st.chat_input("Bạn muốn hỏi thêm gì không?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        # Phản hồi giả lập nhanh
        res = f"Chào {name}, với chỉ số BMI {bmi}, tôi khuyên bạn nên tập trung vào {tips[0].lower()}"
        st.session_state.messages.append({"role": "assistant", "content": res})
        with st.chat_message("assistant"): st.markdown(res)
