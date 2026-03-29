import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from fpdf import FPDF
import os

# ================= 1. CẤU HÌNH TRANG & PDF =================
st.set_page_config(page_title="AI Health Infinity", layout="wide", page_icon="🧬")

def create_pdf(name, diagnosis, metrics, lifespan, risks, diet, tips):
    try:
        pdf = FPDF()
        pdf.add_page()
        font_path = "Roboto-Regular.ttf"
        if os.path.exists(font_path):
            pdf.add_font("Roboto", "", font_path); pdf.set_font("Roboto", size=12); f_name = "Roboto"
        else:
            pdf.set_font("Arial", size=12); f_name = "Arial"

        pdf.set_font(f_name, 'B', 16)
        pdf.cell(0, 10, txt="HO SO SUC KHOE TOAN DIEN AI 2026", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font(f_name, size=12)
        pdf.cell(0, 10, txt=f"Ho ten: {name} | Tuoi tho du kien: {lifespan} tuoi", ln=True)
        pdf.ln(5)
        pdf.multi_cell(0, 10, txt=f"Chan doan AI: {diagnosis}")
        
        pdf.ln(5)
        pdf.set_font(f_name, 'B', 12); pdf.cell(0, 10, txt="Cac nguy co benh ly:", ln=True); pdf.set_font(f_name, size=12)
        for r in risks: pdf.cell(0, 8, txt=f"- {r}", ln=True)
        
        pdf.ln(5)
        pdf.set_font(f_name, 'B', 12); pdf.cell(0, 10, txt="Thuc don goi y:", ln=True); pdf.set_font(f_name, size=12)
        pdf.multi_cell(0, 8, txt=diet)
        
        pdf.ln(5)
        pdf.set_font(f_name, 'B', 12); pdf.cell(0, 10, txt="Loi khuyen:", ln=True); pdf.set_font(f_name, size=12)
        for t in tips: pdf.multi_cell(0, 8, txt=f"- {t}")
        
        return pdf.output()
    except: return None

# ================= 2. CORE AI ENGINE =================
def analyze_infinity(age, w, h, sleep, exer, stress, water):
    bmi = round(w / ((h/100)**2), 1)
    hr = int(np.clip(70 + (stress * 1.5) - (exer * 4), 56, 110))
    bp_sys = int(110 + (bmi-21)*1.5 + (stress*1.2) + (age*0.2))
    spo2 = int(np.clip(95 + (sleep/4) + (exer/3) - (stress/6), 94, 100))
    
    # Tuổi thọ
    lifespan = round(76 + (sleep-7)*1.2 + exer*2.5 - (stress-4)*1.5 - abs(bmi-22)*1.2, 1)
    
    # Nguy cơ bệnh
    risks = []
    if bp_sys > 135: risks.append("🔴 Nguy cơ Cao huyết áp")
    if bmi > 26: risks.append("🟠 Nguy cơ Tiểu đường & Gan nhiễm mỡ")
    if stress > 7: risks.append("🟡 Nguy cơ Rối loạn lo âu & Mất ngủ")
    if not risks: risks.append("🟢 Hệ thống chưa ghi nhận bất thường")
    
    # Thực đơn AI
    if bmi > 25:
        diet = "Ưu tiên: Ức gà, Cá hồi, Rau xanh đậm, Khoai lang. Hạn chế: Tinh bột trắng, Đường."
    else:
        diet = "Ưu tiên: Chế độ ăn cân bằng, bổ sung các loại hạt (Hạnh nhân, Óc chó), Trái cây tươi."
    
    # So sánh VĐV (Cristiano Ronaldo)
    match = max(0, 100 - (abs(hr-52) + abs(bmi-23)*2 + stress*3))
    
    return {"BMI": bmi, "HR": hr, "BP": f"{bp_sys}/85", "SpO2": spo2, 
            "Lifespan": lifespan, "Risks": risks, "Diet": diet, "Match": match}

# ================= 3. GIAO DIỆN NHẬP LIỆU =================
with st.sidebar:
    st.title("🧪 Infinity Lab")
    name = st.text_input("Tên", "Khách hàng")
    age = st.number_input("Tuổi", 15, 100, 25)
    weight = st.number_input("Cân nặng (kg)", 40, 150, 68)
    height = st.number_input("Chiều cao (cm)", 100, 220, 172)
    st.divider()
    sleep = st.slider("🛌 Ngủ (h)", 0.0, 12.0, 7.5)
    exer = st.slider("🏃 Vận động (h)", 0.0, 5.0, 1.0)
    stress = st.slider("😰 Stress", 1, 10, 5)
    water = st.slider("💧 Nước (L)", 0.0, 5.0, 2.0)
    
    analyze_btn = st.button("🚀 PHÂN TÍCH TOÀN DIỆN", type="primary", use_container_width=True)

# ================= 4. HIỂN THỊ KẾT QUẢ TỔNG HỢP =================
if analyze_btn or 'analyzed' in st.session_state:
    st.session_state.analyzed = True
    res = analyze_infinity(age, weight, height, sleep, exer, stress, water)
    
    # --- KHU VỰC 1: CẢNH BÁO & TUỔI THỌ ---
    st.title("🏥 Kết luận Sức khỏe AI")
    c1, c2, c3 = st.columns([1.5, 2, 1])
    
    with c1:
        st.subheader("⏳ Tuổi thọ dự kiến")
        st.markdown(f"<h1 style='color: #00FFCC; font-size: 60px;'>{res['Lifespan']}</h1>", unsafe_allow_html=True)
        st.caption("Dự báo dựa trên lối sống hiện tại.")
        
    with c2:
        st.subheader("🚨 Nguy cơ bệnh lý")
        for r in res['Risks']:
            st.warning(r)
            
    with c3:
        st.subheader("🏅 Đối chiếu")
        st.metric("Tương đồng Ronaldo", f"{res['Match']:.0f}%")
        st.progress(res['Match']/100)

    st.divider()
    
    # --- KHU VỰC 2: CHỈ SỐ SINH HỌC & BIỂU ĐỒ ---
    st.subheader("📡 Cảm biến sinh học ảo")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Nhịp tim", f"{res['HR']} bpm", "Ước tính")
    m2.metric("Huyết áp", f"{res['BP']} mmHg", "Ước tính")
    m3.metric("SpO2", f"{res['SpO2']}%", "Ước tính")
    m4.metric("Chỉ số BMI", res['BMI'], f"{res['BMI']-22:.1f}")

    col_radar, col_diet = st.columns(2)
    with col_radar:
        labels = ['Ngủ', 'Vận động', 'Nước', 'Stress', 'BMI']
        vals = [sleep*8, exer*20, water*20, (11-stress)*10, (100-abs(res['BMI']-22)*5)]
        vals += vals[:1]; angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist(); angles += angles[:1]
        fig, ax = plt.subplots(figsize=(4,4), subplot_kw=dict(polar=True))
        ax.fill(angles, vals, color='#00FFCC', alpha=0.3); ax.plot(angles, vals, color='#00FFCC', linewidth=2)
        ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels)
        st.pyplot(fig)
        
    with col_diet:
        st.subheader("🥗 Thực đơn AI đề xuất")
        st.info(res['Diet'])
        st.subheader("📥 Xuất hồ sơ PDF")
        pdf_bytes = create_pdf(name, "Ổn định", res, res['Lifespan'], res['Risks'], res['Diet'], ["Uống đủ nước", "Ngủ sớm"])
        if pdf_bytes:
            st.download_button("Tải Báo Cáo Chuyên Sâu", data=bytes(pdf_bytes), file_name=f"AI_Health_{name}.pdf", use_container_width=True)

    # --- KHU VỰC 3: HỎI ĐÁP CHUYÊN GIA ---
    st.divider()
    st.subheader("💬 Trò chuyện với chuyên gia Longevity AI")
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": f"Chào {name}, tôi dự đoán bạn có thể sống đến {res['Lifespan']} tuổi. Bạn có muốn biết tại sao tôi cảnh báo về {res['Risks'][0]} không?"}]
        
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
        
    if pr := st.chat_input("Hỏi AI về bệnh lý, thực đơn, tuổi thọ..."):
        st.session_state.messages.append({"role": "user", "content": pr})
        with st.chat_message("user"): st.markdown(pr)
        
        # Logic phản hồi thông minh
        p_low = pr.lower()
        if "ăn" in p_low or "thực đơn" in p_low:
            ans = f"Với tình trạng hiện tại, bạn nên: {res['Diet']}"
        elif "bệnh" in p_low or "nguy cơ" in p_low:
            ans = f"Dựa trên chỉ số BMI {res['BMI']} và Huyết áp {res['BP']}, nguy cơ chính là {res['Risks'][0]}. Hãy đi khám định kỳ nếu chỉ số này tăng thêm."
        elif "tuổi thọ" in p_low:
            ans = f"Để tăng từ {res['Lifespan']} lên {res['Lifespan']+3} tuổi, bạn cần giảm stress và tăng giờ ngủ thêm 1h mỗi đêm."
        else:
            ans = f"Tôi khuyên bạn nên tập trung cải thiện chỉ số {res['Risks'][0]} để tối ưu hóa sức khỏe."
            
        st.session_state.messages.append({"role": "assistant", "content": ans})
        with st.chat_message("assistant"): st.markdown(ans)
