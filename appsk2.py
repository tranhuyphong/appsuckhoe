import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

# ================= 1. CẤU HÌNH & ENGINE AI CHUẨN =================
st.set_page_config(page_title="AI Health Infinity Pro", layout="wide", page_icon="🧬")

def analyze_infinity(age, w, h, sleep, exer, stress, water):
    bmi = round(w / ((h/100)**2), 1)
    # Thuật toán tuổi thọ thực tế (Nền tảng 75.5 tuổi)
    lifespan = 75.5 + (sleep-7.5)*0.7 + exer*1.3 - (stress-4)*0.6 - abs(bmi-22.5)*0.4
    final_life = np.clip(lifespan, 65.0, 95.0)

    # Chỉ số sinh học ảo
    bp_sys = int(110 + (age * 0.15) + (bmi - 22)*1.1 + (stress * 0.5))
    hr_rest = int(70 + (stress * 1.2) - (exer * 2))
    
    risks = []
    if bp_sys > 135: risks.append("Nguy cơ Cao huyết áp")
    if bmi > 25.5: risks.append("Nguy cơ Tiểu đường & Chuyển hóa")
    if stress > 7: risks.append("Nguy cơ Kiệt sức (Burnout)")
    if not risks: risks.append("Sức khỏe hiện tại ổn định")

    diet = "Ưu tiên: Ức gà, Cá hồi, Rau xanh đậm. Hạn chế: Đường, Muối." if bmi > 25 else "Duy trì chế độ ăn cân bằng, bổ sung hạt & trái cây."
    match = max(0, 100 - (abs(hr_rest-52) + abs(bmi-23)*2 + stress*3))
    
    return {"BMI": bmi, "HR": hr_rest, "BP": f"{bp_sys}/85", "Lifespan": round(final_life, 1), "Risks": risks, "Diet": diet, "Match": match}

# ================= 2. HÀM TẠO PDF (KHÔNG LỖI UNICODE) =================
def create_pdf_fixed(name, res, diet):
    try:
        pdf = FPDF()
        pdf.add_page()
        # Dùng Font Roboto từ file bạn có để gõ Tiếng Việt
        font_path = "Roboto-Regular.ttf"
        if os.path.exists(font_path):
            pdf.add_font("Roboto", "", font_path); pdf.set_font("Roboto", size=12); f = "Roboto"
        else:
            pdf.set_font("Arial", size=12); f = "Arial"

        pdf.set_font(f, 'B', 16)
        pdf.cell(0, 10, txt="HO SO SUC KHOE AI 2026", ln=True, align='C')
        pdf.ln(5)
        
        pdf.set_font(f, size=12)
        pdf.cell(0, 10, txt=f"Khach hang: {name} | Du bao tuoi tho: {res['Lifespan']} tuoi", ln=True)
        # Dùng multi_cell để tránh lỗi tràn khung hình
        pdf.multi_cell(0, 8, txt=f"Nguy co: {', '.join(res['Risks'])}")
        pdf.multi_cell(0, 8, txt=f"Thuc don: {diet}")
        return pdf.output()
    except: return None

# ================= 3. GIAO DIỆN CHÍNH =================
with st.sidebar:
    st.title("🧪 Infinity Lab")
    name = st.text_input("Tên", "Khách hàng")
    age = st.number_input("Tuổi", 15, 100, 30)
    w = st.number_input("Cân nặng (kg)", 40.0, 150.0, 70.0)
    h = st.number_input("Chiều cao (cm)", 100, 220, 170)
    st.divider()
    sl = st.slider("🛌 Ngủ (h)", 0.0, 12.0, 7.5)
    ex = st.slider("🏃 Vận động (h)", 0.0, 5.0, 1.0)
    st_val = st.slider("😰 Stress", 1, 10, 5)
    wa = st.slider("💧 Nước (L)", 0.0, 5.0, 2.0)
    analyze_btn = st.button("🚀 PHÂN TÍCH TOÀN DIỆN", type="primary", use_container_width=True)

if analyze_btn or 'analyzed' in st.session_state:
    st.session_state.analyzed = True
    res = analyze_infinity(age, w, h, sl, ex, st_val, wa)

    # --- HIỂN THỊ CHỈ SỐ ---
    st.title("🏥 Kết quả Chẩn đoán AI")
    c1, c2, c3 = st.columns(3)
    c1.metric("Tuổi thọ dự báo", f"{res['Lifespan']} tuổi")
    c2.metric("Huyết áp ước tính", f"{res['BP']}")
    c3.metric("Tương đồng Ronaldo", f"{res['Match']:.0f}%")

    # --- BIỂU ĐỒ RADAR ---
    st.divider()
    col_radar, col_risk = st.columns(2)
    with col_radar:
        labels = ['Ngủ', 'Vận động', 'Nước', 'Stress', 'BMI']
        vals = [sl*8, ex*20, wa*20, (11-st_val)*10, (100-abs(res['BMI']-22)*5)]
        vals += vals[:1]; angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist(); angles += angles[:1]
        fig, ax = plt.subplots(figsize=(4,4), subplot_kw=dict(polar=True))
        ax.fill(angles, vals, color='#00FFCC', alpha=0.3); ax.plot(angles, vals, color='#00FFCC', linewidth=2)
        ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels)
        st.pyplot(fig)

    with col_risk:
        st.subheader("⚠️ Nguy cơ & Thực đơn")
        for r in res['Risks']: st.warning(r)
        st.info(f"🥗 **Thực đơn:** {res['Diet']}")
        # Nút PDF đã fix lỗi Unicode
        pdf_data = create_pdf_fixed(name, res, res['Diet'])
        if pdf_data:
            st.download_button("📥 Tải Hồ Sơ PDF", data=bytes(pdf_data), file_name=f"Health_{name}.pdf", use_container_width=True)

    # --- CHAT AI ---
    st.divider()
    st.subheader("💬 Chat với Bác sĩ Longevity AI")
    if "msgs" not in st.session_state:
        st.session_state.msgs = [{"role": "assistant", "content": f"Chào {name}, tôi lo ngại về {res['Risks'][0]}. Bạn muốn tư vấn thêm không?"}]
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    if pr := st.chat_input("Hỏi AI..."):
        st.session_state.msgs.append({"role": "user", "content": pr})
        ans = f"Dựa trên BMI {res['BMI']}, bạn nên {res['Diet'].lower()}"
        st.session_state.msgs.append({"role": "assistant", "content": ans})
        st.rerun()
