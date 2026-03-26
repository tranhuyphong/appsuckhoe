import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time

from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor

# ================= UI =================
st.set_page_config(page_title="AI Health Platform", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}
.title {
    font-size: 40px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🚀 AI Health Intelligence Platform</div>', unsafe_allow_html=True)

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

# ================= DATA =================
@st.cache_data
def generate_data(n=1000):
    np.random.seed(42)
    sleep = np.random.uniform(4, 9, n)
    exercise = np.random.uniform(0, 2, n)
    bmi = np.random.uniform(18, 30, n)
    heart = np.random.uniform(55, 100, n)
    water = np.random.uniform(1, 3, n)
    stress = np.random.uniform(1, 10, n)

    score = (
        40 + sleep*5 + exercise*15 +
        20*np.exp(-(bmi-22)**2/10) -
        abs(heart-75)*0.3 + water*4 - stress*3
    )

    return np.column_stack([sleep, exercise, bmi, heart, water, stress]), np.clip(score,0,100)

# ================= MODEL =================
@st.cache_resource
def train():
    X, y = generate_data()
    rf = RandomForestRegressor().fit(X, y)
    dl = MLPRegressor(hidden_layer_sizes=(64,32), max_iter=500).fit(X, y)
    return rf, dl

rf, dl = train()

# ================= SCORE =================
def rule_score():
    return max(0, min(
        50 + sleep*4 + exercise*12
        - abs(bmi-22)*2 - abs(heart-75)*0.5
        + water*3 - stress*2, 100))

def ml_score():
    return rf.predict([[sleep,exercise,bmi,heart,water,stress]])[0]

def dl_score():
    return dl.predict([[sleep,exercise,bmi,heart,water,stress]])[0]

def calc_final(s, e):
    r = max(0, min(
        50 + s*4 + e*12
        - abs(bmi-22)*2 - abs(heart-75)*0.5
        + water*3 - stress*2, 100))
    m = rf.predict([[s,e,bmi,heart,water,stress]])[0]
    d = dl.predict([[s,e,bmi,heart,water,stress]])[0]
    return 0.3*r + 0.4*m + 0.3*d

# ================= BUTTON =================
if st.button("🚀 Analyze Now"):

    with st.spinner("🤖 AI is analyzing your health..."):
        time.sleep(1.5)

    r = rule_score()
    m = ml_score()
    d = dl_score()
    final = 0.3*r + 0.4*m + 0.3*d

    # ================= TABS =================
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard",
        "🧪 Simulator",
        "🎯 Goal AI",
        "🧬 Future"
    ])

    # ===== TAB 1 =====
    with tab1:
        st.subheader("📊 Health Dashboard")

        st.metric("💯 Final Score", f"{final:.1f}")
        st.progress(int(final))

        if final < 50:
            st.error("🔴 High Risk")
        elif final < 75:
            st.warning("🟡 Medium Risk")
        else:
            st.success("🟢 Low Risk")

    # ===== TAB 2 =====
    with tab2:
        st.subheader("🧪 What-if Simulator")

        delta_sleep = st.slider("Sleep Change", -2.0, 2.0, 0.0)
        delta_ex = st.slider("Exercise Change", -1.0, 1.0, 0.0)

        new_score = calc_final(sleep + delta_sleep, exercise + delta_ex)

        st.metric("🔮 New Score", f"{new_score:.1f}",
                  delta=f"{new_score-final:.1f}")

    # ===== TAB 3 =====
    with tab3:
        st.subheader("🎯 Goal-based AI")

        target = st.slider("Target Score", 50, 100, 85)
        gap = target - final

        if gap > 0:
            st.write("👉 To reach your goal:")
            st.write(f"- Sleep +{gap/10:.1f}h")
            st.write(f"- Exercise +{gap/20:.1f}h")
            st.write(f"- Reduce stress {gap/15:.1f}")
        else:
            st.success("🔥 Goal achieved!")

    # ===== TAB 4 =====
    with tab4:
        st.subheader("🧬 Digital Twin (Future Simulation)")

        future = []
        cur = final

        for _ in range(30):
            cur += (exercise*2 + sleep*0.5 - stress*1.2)*0.3
            cur = np.clip(cur,0,100)
            future.append(cur)

        st.line_chart(future)
        st.write(f"📅 After 30 days: {future[-1]:.1f}")