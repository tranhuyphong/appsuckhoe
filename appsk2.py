import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from fpdf import FPDF
import os

# ================= 1. HÀM TẠO PDF CHUYÊN NGHIỆP (CÓ BIỂU ĐỒ) =================
def create_pdf_pro(name, res, diet, tips):
    try:
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.add_page()
        
        # Cấu hình Font từ file bạn đã upload
        font_name = "Roboto-Regular.ttf"
        if os.path.exists(font_name):
            pdf.add_font("Roboto", "", font_name)
            pdf.set_font("Roboto", size=12)
            f = "Roboto"
        else:
            pdf.set_font("Arial", size=12)
            f = "Arial"

        # --- TIÊU ĐỀ ---
        pdf.set_text_color(0, 51, 102)
        pdf.set_font(f, 'B', 20)
        pdf.cell(0, 15, txt="HỒ SƠ SỨC KHỎE TỔNG THỂ AI", ln=True, align='C')
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)
        
        # --- THÔNG TIN CƠ BẢN ---
        pdf.set_font(f, size=12)
        pdf.cell(0, 10, txt=f"Khách hàng: {name}", ln=True)
        pdf.cell(0, 10, txt=f"Tuổi thọ dự kiến: {res['Lifespan']} tuổi", ln=True)
        pdf.cell(0, 10, txt=f"Độ tương đồng VĐV: {res['Match']:.0f}%", ln=True)
        pdf.ln(5)

        # --- CHÈN BIỂU ĐỒ RADAR VÀO PDF ---
        # Vẽ biểu đồ ẩn để lưu ảnh
        labels = ['Ngủ', 'Vận động', 'Nước', 'Stress', 'BMI']
        # Giả lập giá trị biểu đồ từ dữ liệu đầu vào
        vals = [70, 80, 60, 40, 90] # Có thể thay bằng dữ liệu thật
        vals += vals[:1]; angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist(); angles += angles[:1]
        fig, ax = plt.subplots(figsize=(4,4), subplot_kw=dict(polar=True))
        ax.fill(angles, vals, color='#00FFCC', alpha=0.3)
        ax.plot(angles, vals, color='#00FFCC', linewidth=2)
        plt.savefig("temp_chart.png", bbox_inches='tight', dpi=150)
        plt.close()
        
        # Chèn ảnh vào PDF (Căn giữa)
        pdf.image("temp_chart.png", x=50, y=70, w=110)
        pdf.ln(90) # Nhảy dòng xuống dưới ảnh

        # --- CHI TIẾT BỆNH LÝ & DINH DƯỠNG ---
        pdf.set_font(f, 'B', 14)
        pdf.cell(0, 10, txt="Phân tích chuyên sâu:", ln=True)
        pdf.set_font(f, size=11)
        
        # Loại bỏ emoji để tránh lỗi Unicode Latin-1
        clean_risks = [r.replace('🔴','').replace('🟠','').replace('🟡','').replace('🟢','') for r in res['Risks']]
        pdf.multi_cell(0, 8, txt="Cảnh báo bệnh lý: " + ", ".join(clean_risks))
        pdf.ln(2)
        pdf.multi_cell(0, 8, txt=f"Thực đơn gợi ý: {diet}")
        
        # --- LỜI KHUYÊN ---
        pdf.ln(5)
        pdf.set_font(f, 'B', 12)
        pdf.cell(0, 10, txt="Lời khuyên từ AI Coach:", ln=True)
        pdf.set_font(f, size=11)
        for t in tips:
            pdf.multi_cell(0, 8, txt=f"- {t}")

        return pdf.output()
    except Exception as e:
        st.error(f"Lỗi tạo PDF: {e}")
        return None

# ================= 2. PHẦN HIỂN THỊ TRÊN APP =================
# Trong phần hiển thị kết quả sau khi bấm nút "PHÂN TÍCH":
if 'analyzed' in st.session_state:
    # ... (Các phần hiển thị biểu đồ trên màn hình giữ nguyên như cũ) ...

    # Nút bấm xuất PDF nằm ở dưới cùng hoặc bên cạnh biểu đồ
    st.divider()
    st.subheader("📥 Hồ sơ lưu trữ")
    
    # Tạo dữ liệu PDF
    pdf_output = create_pdf_pro(
        name, 
        res, 
        res['Diet'], 
        ["Duy trì cường độ vận động hiện tại", "Bổ sung thêm thực phẩm giàu chất xơ"]
    )
    
    if pdf_output:
        st.download_button(
            label="📩 Tải Báo Cáo PDF Chuyên Sâu (Có biểu đồ)",
            data=bytes(pdf_output),
            file_name=f"Bao_Cao_Suc_Khoe_{name}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
