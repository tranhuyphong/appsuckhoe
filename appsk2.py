import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor

# ================= CONFIG =================
st.set_page_config(page_title="AI Health Pro MAX", layout="wide")
st.title("💪 AI Health Pro MAX - National Version")

# ================= INPUT =================
col1, col2 = st.columns(2)

with col1:
    sleep = st.slider("🛌 Sleep (h)", 0.0, 10.0, 6.0)
    exercise = st.slider("🏃 Exercise (h)", 0.0, 2.0, 0.5)
    water = st.slider("💧 Water (L)", 0.5, 4.0, 2.0)

with col2:
    bmi = st.slider("⚖️ BMI", 15.0, 35.0, 22.0)
    heart = st.slider("❤️ Heart Rate", 40, 120, 75)
    stress = st.slider("😰 Stress", 1, 10, 5)

# ================= MODEL =================
def calculate_score():
    score = (
        50
        + sleep * 4
        + exercise * 12
        - abs(bmi - 22) * 2
        - abs(heart - 75) * 0.5
        + water * 3
        - stress * 2
    )
    return max(0, min(score, 100))

# ================= TRAIN FAKE ML MODEL =================
np.random.seed(42)
data = pd.DataFrame({
    "Sleep": np.random.uniform(4,9,200),
    "Exercise": np.random.uniform(0,2,200),
    "Water": np.random.uniform(1,3,200),
    "Stress": np.random.uniform(1,10,200)
})

data["Score"] = 50 + data["Sleep"]*5 + data["Exercise"]*12 + data["Water"]*3 - data["Stress"]*2

model = RandomForestRegressor()
model.fit(data[["Sleep","Exercise","Water","Stress"]], data["Score"])

# ================= RUN =================
if st.button("🚀 Analyze"):

    score = calculate_score()

    # KPI
    c1, c2, c3 = st.columns(3)
    c1.metric("💯 Score", f"{score:.1f}")
    c2.metric("📈 AI Predict", f"{model.predict([[sleep,exercise,water,stress]])[0]:.1f}")
    c3.metric("🏆 Rank", f"{np.random.randint(70,98)}%")

    # Risk
    st.write("## 🚨 Risk Level")
    if score < 50:
        st.error("🔴 High Risk")
    elif score < 75:
        st.warning("🟡 Medium Risk")
    else:
        st.success("🟢 Low Risk")

    # Explain
    st.write("## 🧠 AI Explain")
    contributions = {
        "Sleep": sleep * 4,
        "Exercise": exercise * 12,
        "BMI": -abs(bmi - 22) * 2,
        "Heart": -abs(heart - 75) * 0.5,
        "Water": water * 3,
        "Stress": -stress * 2
    }
    df_exp = pd.DataFrame(contributions.items(), columns=["Factor", "Impact"])
    st.bar_chart(df_exp.set_index("Factor"))

    # Radar
    st.write("## 📊 Health Radar")
    labels = list(contributions.keys())
    values = list(contributions.values())
    values += values[:1]
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig = plt.figure()
    ax = fig.add_subplot(111, polar=True)
    ax.plot(angles, values)
    ax.fill(angles, values, alpha=0.1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    st.pyplot(fig)

    # Future prediction
    st.write("## 📈 30-Day Prediction")
    days = list(range(30))
    trend = [score + i*(exercise - stress*0.1) for i in days]
    df_trend = pd.DataFrame({"Day": days, "Score": trend})
    st.line_chart(df_trend.set_index("Day"))

    # ================= AI COACH =================
    st.write("## 🤖 AI Health Coach")

    def get_tips():
        tips = []
        if sleep < 7:
            tips.append("Ngủ thêm 1-2h")
        if exercise < 1:
            tips.append("Tăng vận động")
        if water < 2:
            tips.append("Uống thêm nước")
        if stress > 6:
            tips.append("Giảm stress")
        return tips

    tips = get_tips()
    worst = min(contributions, key=contributions.get)

    st.write(f"👉 Yếu tố cần cải thiện nhất: **{worst}**")
    for t in tips:
        st.write("-", t)

    # Q&A
    question = st.text_input("💬 Hỏi AI")
    if st.button("💡 Trả lời"):
        if "tăng" in question.lower():
            st.success("Tăng exercise + giảm stress là nhanh nhất")
        elif "stress" in question.lower():
            st.write("Thiền, ngủ đủ, giảm áp lực")
        else:
            st.write("Cải thiện các yếu tố trên")

    # Goal system
    goal = st.slider("🎯 Goal Score", 50, 100, 80)
    if score < goal:
        st.warning(f"Cần thêm {goal-score:.1f} điểm để đạt goal")
    else:
        st.success("Đã đạt mục tiêu 🎉")
