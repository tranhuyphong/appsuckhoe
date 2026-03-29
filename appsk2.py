import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

# ================= 1. CẤU HÌNH & ENGINE AI THỰC TẾ =================
st.set_page_config(page_title="AI Health Infinity Pro", layout="wide")

def run_comprehensive_analysis(age, w, h, sleep, exer, stress, water):
    bmi = round(w / ((h/100)**2), 1)
    
    # Dự báo tuổi thọ thực tế (Dựa trên nền tảng y khoa)
    base_life = 75.5 
    life_impact = (sleep - 7.5)*0.7 + (exer*1.3) - (stress - 4)*0.6 - abs(bmi - 22.5)*0.4
    final_life = np.clip(base_life + life_impact, 65.0, 95.0)

    # Chỉ số sinh học ẩn
    bp_sys = int(110 + (age * 0.15) + (bmi - 22)*1.1 + (stress * 0.5))
    hr_rest = int(70 + (stress * 1.2) - (exer * 2))
    
    # Nguy cơ bệnh lý
    risks = []
    if bp_sys > 135: risks.append("Nguy cơ Cao huyết áp")
    if bmi > 25.5: risks.append("Nguy cơ Rối loạn chuyển hóa (Tiểu đường)")
    if stress > 7: risks.append("Nguy cơ Kiệt sức & Lo âu")
    if not risks: risks.append("Chỉ số sức khỏe hiện tại ổn định")

    return {
        "BMI": bmi, "Lifespan": round(final_life, 1), 
        "BP": f"{bp_sys}/85", "HR": hr_rest, "Risks": risks
    }

# ================= 2. HÀM TẠO PDF (FIX LỖI UNICODE & TRÀN KHUNG) =================
def create_pdf_full(name, res, diet):
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Sử dụng font bạn đã upload để hiển thị Tiếng Việt
        font_path = "Roboto-VariableFont_wdth,wght.ttf"
        if os.path.exists(font_path):
            pdf.add_font("Roboto", "", font_path)
            pdf.set_font("Roboto", size=12)
            f = "Roboto"
        else:
            pdf.set_font("Arial", size=12)
            f = "Arial"

        pdf.set_font(f, 'B', 16)
        pdf.cell(0, 15, txt="HỒ SƠ SỨC KHỎE TỔNG THỂ AI 2026", ln=True, align='C')
        pdf.ln(5)
        
        pdf.set_font(f, size=12)
        pdf.cell(0, 10, txt=f"Khách hàng: {name}", ln=True)
        pdf.cell(0, 10, txt=f"Tuổi thọ dự báo: {res['Lifespan']} tuổi", ln=True)
        pdf.cell(0, 10, txt=f"Huyết áp ước tính: {res['BP']} mmHg", ln=True)
        
        pdf.ln(5)
        pdf.set_font(f, 'B', 12)
        pdf.cell(0, 10, txt="Chẩn đoán & Nguy cơ:", ln=True)
        pdf.set_font(f, size=11)
        # Sử dụng multi_cell để tự xuống dòng, tránh lỗi FPDFException
        pdf.multi_cell(0, 8, txt=", ".join(res['Risks']))
        
        pdf.ln(5)
        pdf.multi_cell(0, 8, txt=f"Thực đơn & Lời khuyên: {diet}")
        
        return pdf.output()
    except Exception as e:
        st.error(f"Lỗi tạo PDF: {e}")
        return None

# ================= 3. GIAO DIỆN CHÍNH =================
with st.sidebar:
    st.header("🧬 Nhập dữ liệu")
    u_name = st.text_input("Họ tên", "Khách hàng")
    u_age = st.number_input("Tuổi", 18, 100, 30)
    u_w = st.number_input("Cân nặng (kg)", 40.0, 150.0, 70.0)
    u_h = st.number_input("Chiều cao (cm)", 140, 210, 170)
    st.divider()
    u_sleep = st.slider("Giờ ngủ", 0.0, 12.0, 7.5)
    u_ex = st.slider("Vận động (h)", 0.0, 5.0, 1.0)
    u_st = st.slider("Mức độ Stress", 1, 10, 5)
    analyze_btn = st.button("PHÂN TÍCH TOÀN DIỆN", type="primary")

if analyze_btn or 'analyzed' in st.session_state:
    st.session_state.analyzed = True
    res = run_comprehensive_analysis(u_age, u_w, u_h, u_sleep, u_ex, u_st, 2.0)

    # --- KHU VỰC HIỂN THỊ CHỈ SỐ ---
    st.title("🏥 Kết quả Chẩn đoán AI")
    c1, c2, c3 = st.columns(3)
    c1.metric("Tuổi thọ dự kiến", f"{res['Lifespan']} tuổi")
    c2.metric("Huyết áp ước tính", f"{res['BP']}")
    c3.metric("Chỉ số BMI", res['BMI'])

    st.divider()

    # --- BIỂU ĐỒ RADAR & CẢNH BÁO ---
    col_chart, col_risk = st.columns([1, 1])
    
    with col_chart:
        labels = ['Ngủ', 'Vận động', 'BMI', 'Tâm lý', 'Nước']
        stats = [u_sleep*8, u_ex*20, (100 - abs(res['BMI']-22)*5), (11-u_st)*10, 70]
        stats += stats[:1]; angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist(); angles += angles[:1]
        fig, ax = plt.subplots(figsize=(4,4), subplot_kw=dict(polar=True))
        ax.fill(angles, stats, color='#00FFCC', alpha=0.3); ax.plot(angles, stats, color='#00FFCC', linewidth=2)
        ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels)
        st.pyplot(fig)

    with col_risk:
        st.subheader("⚠️ Nguy cơ bệnh lý")
        for r in res['Risks']: st.warning(r)
        
        diet_str = "Tăng chất xơ, giảm tinh bột và đường." if res['BMI'] > 25 else "Duy trì chế độ ăn cân bằng hiện tại."
        st.info(f"🥗 **Thực đơn AI:** {diet_str}")

    # --- CHAT AI & XUẤT PDF ---
    st.divider()
    c_chat, c_pdf = st.columns([2, 1])
    
    with c_chat:
        st.subheader("💬 Chat với Bác sĩ AI")
        if "msgs" not in st.session_state:
            st.session_state.msgs = [{"role": "assistant", "content": f"Chào {u_name}, tôi lo ngại về {res['Risks'][0]}. Bạn muốn tư vấn thêm không?"}]
        for m in st.session_state.msgs:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        
        if pr := st.chat_input("Hỏi AI về sức khỏe..."):
            st.session_state.msgs.append({"role": "user", "content": pr})
            ans = f"Dựa trên BMI {res['BMI']}, bạn nên tập trung vào {diet_str.lower()}"
            st.session_state.msgs.append({"role": "assistant", "content": ans})
            st.rerun()

    with c_pdf:
        st.subheader("📥 Hồ sơ PDF")
        pdf_bytes = create_pdf_full(u_name, res, diet_str)
        if pdf_bytes:
            st.download_button("Tải Báo Cáo Chuẩn", data=bytes(pdf_bytes), file_name=f"Health_Report_{u_name}.pdf", use_container_width=True)
