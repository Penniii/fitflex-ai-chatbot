import time
import google.generativeai as genai
import pandas as pd
import streamlit as st

# ==========================================
# 1. PAGE CONFIGURATION & CUSTOM CSS
# ==========================================
st.set_page_config(
    page_title="FitFlex AI - AI Workout & Habit Tracker",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling untuk Tampilan Mewah
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #FF4B4B, #FF8C00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1rem;
        color: #6c757d;
        margin-bottom: 20px;
    }
    .stMetric {
        background-color: #1e2229;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2e3440;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 2. SESSION STATE INITIALIZATION
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "habits" not in st.session_state:
    st.session_state.habits = {
        "Workout Harian": False,
        "Minum Air 2.5L": False,
        "Tidur 7-8 Jam": False,
        "Protein Cukup": False,
    }

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "weight": 65,
        "height": 170,
        "goal": "Fat Loss & Muscle Gain",
    }

# ==========================================
# 3. SIDEBAR: CONFIGURATION & METRICS
# ==========================================
with st.sidebar:
    st.title("⚡ FitFlex Dashboard")

    # API Key Input
    api_key = st.text_input("🔑 Gemini API Key:", type="password")

    st.divider()

    # Parameter AI & Persona
    st.subheader("🤖 AI Specialist Settings")
    persona = st.selectbox(
        "Pilih AI Persona:",
        ["Personal Trainer (Motivatif)", "Nutritionist & Dietitian (Presisi)"],
    )

    gaya_bahasa = st.select_slider(
        "Gaya Komunikasi:",
        options=["Casual & Santai", "Pro & Motivatif", "Strict Coach"],
        value="Pro & Motivatif",
    )

    temperature = st.slider(
        "Kreativitas AI (Temperature):", 0.0, 1.0, 0.6, step=0.1
    )

    st.divider()

    # User Profile Quick Edit
    st.subheader("👤 Profil Pengguna")
    weight = st.number_input(
        "Berat Badan (kg):",
        value=st.session_state.user_profile["weight"],
        step=1,
    )
    height = st.number_input(
        "Tinggi Badan (cm):",
        value=st.session_state.user_profile["height"],
        step=1,
    )
    goal = st.selectbox(
        "Target Utama:",
        [
            "Fat Loss & Muscle Gain",
            "Weight Loss",
            "Muscle Building (Bulking)",
            "Endurance & Health",
        ],
    )

    # Update Profile Session State
    st.session_state.user_profile.update(
        {"weight": weight, "height": height, "goal": goal}
    )

    if st.button("🗑️ Reset Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ==========================================
# 4. MAIN APP HEADER & METRICS
# ==========================================
st.markdown(
    '<div class="main-header">FitFlex AI Workspace</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">Personalized AI Workout Buddy, Nutrition Coach & Habit Tracker</div>',
    unsafe_allow_html=True,
)

# Hitung BMI Sederhana
bmi = weight / ((height / 100) ** 2)
if bmi < 18.5:
    bmi_category = "Underweight"
elif 18.5 <= bmi < 24.9:
    bmi_category = "Ideal"
elif 25 <= bmi < 29.9:
    bmi_category = "Overweight"
else:
    bmi_category = "Obesity"

# Quick Metrics Bar
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric(label="BMI Kamu", value=f"{bmi:.1f}", delta=bmi_category)
with col_m2:
    completed_habits = sum(st.session_state.habits.values())
    st.metric(
        label="Habit Progress",
        value=f"{completed_habits}/{len(st.session_state.habits)}",
    )
with col_m3:
    st.metric(
        label="Target Utama", value=st.session_state.user_profile["goal"]
    )
with col_m4:
    st.metric(label="Persona AI", value=persona.split(" ")[0])

st.divider()

# ==========================================
# 5. MULTI-TAB WORKSPACE
# ==========================================
tab_chat, tab_habits, tab_planner = st.tabs(
    ["💬 AI Workout Buddy", "✅ Habit Tracker", "📋 Daily Planner & Workout"]
)

# --- TAB 1: AI CHATBOT ---
with tab_chat:
    if not api_key:
        st.warning(
            "Silakan masukkan Gemini API Key di sidebar untuk mengaktifkan AI Assistant.",
            icon="⚠️",
        )
    else:
        genai.configure(api_key=api_key)

        # System Prompt Dynamic
        system_instruction = f"""
        Kamu adalah {persona}, seorang ahli kebugaran dan nutrisi profesional.
        
        Konteks Pengguna:
        - Berat Badan: {weight} kg
        - Tinggi Badan: {height} cm
        - BMI: {bmi:.1f} ({bmi_category})
        - Target Utama: {goal}
        
        Panduan Respon:
        1. Gunakan gaya bahasa: {gaya_bahasa}.
        2. Berikan saran workout atau jadwal nutrisi yang terstruktur (gunakan poin/tabel jika perlu).
        3. Selalu utamakan keselamatan (safety) dan form latihan yang benar.
        4. Sesuaikan rekomendasi kalori dan latihan berdasarkan target profil pengguna di atas.
        """

        model = genai.GenerativeModel(
            model_name="gemini-3.5-flash",
            generation_config={"temperature": temperature},
            system_instruction=system_instruction,
        )

        # Tampilkan Pesan Chat
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat Input
        if prompt := st.chat_input(
            "Tanyakan program latihan, rekomendasi nutrisi, atau evaluasi habit..."
        ):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()

                chat_history = [
                        {
                            "role": "user" if msg["role"] == "user" else "model",
                            "parts": [msg["content"]],
                        }
                        for msg in st.session_state.messages[:-1]
                    ]

                try:
                    chat = model.start_chat(history=chat_history)
                    response = chat.send_message(prompt)

                    full_response = response.text
                    message_placeholder.markdown(full_response)

                    st.session_state.messages.append(
                        {"role": "assistant", "content": full_response}
                    )
                except Exception as e:
                    st.error(f"Terjadi kesalahan pada Gemini API: {e}")

# --- TAB 2: HABIT TRACKER ---
with tab_habits:
    st.subheader("🎯 Checklist Kebiasaan Harian")
    st.write("Centang kebiasaan yang sudah kamu selesaikan hari ini:")

    col_h1, col_h2 = st.columns(2)

    with col_h1:
        for habit in list(st.session_state.habits.keys())[:2]:
            st.session_state.habits[habit] = st.checkbox(
                habit, value=st.session_state.habits[habit]
            )

    with col_h2:
        for habit in list(st.session_state.habits.keys())[2:]:
            st.session_state.habits[habit] = st.checkbox(
                habit, value=st.session_state.habits[habit]
            )

    # Progress Bar
    progress = completed_habits / len(st.session_state.habits)
    st.progress(progress)
    st.caption(f"Kemajuan Harian: {int(progress * 100)}% selesai")

    # Tombol Evaluasi
    if st.button("🤖 Evaluasi Habit Saya dengan AI"):
        if not api_key:
            st.warning("Masukkan API Key terlebih dahulu!")
        else:
            completed_habits = [k for k, v in st.session_state.habits.items() if v]
            
            if completed_habits:
                habits_text = ", ".join(completed_habits)
            else:
                habits_text = "Belum ada kebiasaan yang diselesaikan"

            # Prompt evaluasi
            eval_prompt = f"Saya telah menyelesaikan kebiasaan harian berikut: {habits_text}. Tolong berikan evaluasi singkat dan motivasi untuk mempertahankan konsistensi ini!"
            
            # Simpan pesan ke history & rerun aplikasi
            st.session_state.messages.append(
                {"role": "user", "content": eval_prompt}
            )
            st.rerun()

# --- TAB 3: DAILY PLANNER & WORKOUT TEMPLATE ---
with tab_planner:
    st.subheader("📅 Contoh Program Latihan Mingguan")

    df_workout = pd.DataFrame(
        {
            "Hari": ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"],
            "Fokus Latihan": [
                "Chest & Triceps",
                "Back & Biceps",
                "Rest & Mobility",
                "Legs & Core",
                "Shoulders & Abs",
                "Cardio & HIIT",
            ],
            "Durasi Target": [
                "45 Menit",
                "45 Menit",
                "20 Menit",
                "50 Menit",
                "40 Menit",
                "30 Menit",
            ],
        }
    )

    st.dataframe(df_workout, use_container_width=True)