import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from fpdf import FPDF
import os

# ================= 1. CẤU HÌNH TRANG =================
st.set_page_config(page_title="AI Health Pro MAX", layout="wide", page_icon="💪")

# Hàm tạo PDF an toàn (Không dấu để tránh lỗi crash nếu thiếu font)
def create_pdf(name, score, status, bmi, tips):
    try:
        pdf = FPDF()
        pdf.add_page()
        # Thử dùng font Roboto nếu bạn đã up lên GitHub, nếu không dùng Arial
        font_path = "Roboto-Regular.ttf"
        if os.path.exists(font_path):
            pdf.add_font("Roboto", "", font_path)
            pdf.set_font("Roboto", size=12)
            f_name = "Roboto"
        else:
            pdf.set_font("Arial", size=12)
            f_name = "Arial"

        pdf.set_font(f_name, 'B', 16)
        pdf.cell(0, 10, txt="BAO CAO SUC KHOE AI 2026", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font(f_name, size=12)
        pdf.cell(0, 10, txt=f"Ho ten: {name}", ln=True)
        pdf.cell(0, 10, txt=f"Diem so: {score:.1f}/100", ln=True)
        pdf.cell(0, 10, txt=f"BMI: {bmi}", ln=True)
        pdf.ln(5)
        pdf.cell(0, 10, txt="LOI KHUYEN TU AI:", ln=True)
        for t in tips:
            pdf.multi_cell(0, 10, txt=f"- {t}")
        return pdf.output()
    except:
        return None

# ================= 2. MODEL AI & DATA =================
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

# ================= 3. SIDEBAR NHẬP LIỆU =================
with st.sidebar:
    st.header("🧬 Chỉ số cá nhân")
    name = st.text_input("Họ tên", "Người dùng")
    weight = st.number_input("Cân nặng (kg)", 40, 150, 65)
    height = st.number_input("Chiều cao (cm)", 100, 220, 170)
    bmi = round(weight / ((height/100)**2), 1)
    
    st.divider()
    sleep = st.slider("🛌 Giờ ngủ", 0.0, 12.0, 7.0)
    exercise = st.slider("🏃 Vận động (h)", 0.0, 4.0, 1.0)
    water = st.slider("💧 Nước (L)", 0.0, 5.0, 2.0)
    stress = st.slider("😰 Stress", 1, 10, 4)
    analyze_btn = st.button("🚀 PHÂN TÍCH TỔNG THỂ", type="primary", use_container_width=True)

# ================= 4. GIAO DIỆN CHÍNH =================
if analyze_btn or 'analyzed' in st.session_state:
    st.session_state.analyzed = True
    
    score = model.predict([[sleep, exercise, water, stress, bmi]])[0]
    
    # KPI Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("💯 Score", f"{score:.1f}")
    c2.metric("⚖️ BMI", bmi)
    c3.metric("🏆 Rank", f"{98 - (100-score)//2:.0f}%")

    # --- BIỂU ĐỒ ---
    tab1, tab2 = st.tabs(["📊 Biểu đồ Radar & Impact", "📈 Dự báo xu hướng"])
    
    with tab1:
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("### Health Radar")
            labels = ['Ngủ', 'Vận động', 'Nước', 'Tâm lý', 'Cân đối']
            stats = [sleep*10, exercise*25, water*20, (11-stress)*10, (100-abs(bmi-22)*5)]
            angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
            stats += stats[:1]; angles += angles[:1]
            fig, ax = plt.subplots(figsize=(4,4), subplot_kw=dict(polar=True))
            ax.fill(angles, stats, color='red', alpha=0.25)
            ax.plot(angles, stats, color='red', linewidth=2)
            ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels)
            st.pyplot(fig)
        with col_b:
            st.write("### Impact Factors")
            contributions = {"Sleep": sleep*4, "Exercise": exercise*12, "Water": water*3, "Stress": -stress*2, "BMI": -abs(bmi-22)*2}
            st.bar_chart(pd.Series(contributions))

    with tab2:
        st.write("### 30-Day Trend Prediction")
        days = list(range(30))
        trend = [score + i*(exercise*0.5 - stress*0.1) for i in days]
        st.line_chart(pd.DataFrame({"Day": days, "Score": trend}).set_index("Day"))

    # --- AI COACH & CHAT ---
    st.divider()
    col_chat, col_advice = st.columns([2, 1])
    
    with col_advice:
        st.write("### 🤖 AI Coach")
        tips = []
        if sleep < 7: tips.append("Cần ngủ thêm để phục hồi.")
        if exercise < 1: tips.append("Tăng vận động hàng ngày.")
        if water < 2: tips.append("Uống thêm nước.")
        for t in tips: st.info(t)
        
        # Nút PDF nằm ở đây
        pdf_data = create_pdf(name, score, "On định", bmi, tips)
        if pdf_data:
            st.download_button("📥 Tải Báo Cáo PDF", data=bytes(pdf_data), file_name="Health_Report.pdf", use_container_width=True)

    with col_chat:
        st.write("### 💬 Hỏi đáp AI")
        if "messages" not in st.session_state: st.session_state.messages = []
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        
        if prompt := st.chat_input("Hỏi AI về sức khỏe..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            response = f"Dựa trên chỉ số BMI {bmi} và điểm {score:.1f}, bạn nên tập trung cải thiện thói quen hàng ngày."
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"): st.markdown(response)
