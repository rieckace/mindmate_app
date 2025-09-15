import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="MindMates",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- User Session Management ---
if "username" not in st.session_state:
    st.session_state.username = ""

# --- LOGIN PAGE ---
if not st.session_state.username:
    # --- Custom CSS for Login Page ---
    st.markdown("""
        <style>
            /* Hide the sidebar and default Streamlit elements */
            [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stFooter"] {
                display: none;
            }

            /* Make login page take full height and center content */
            .main > div {
                background: linear-gradient(135deg, #1a1c2c, #232946, #2a2d43);
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }

            .login-box {
                background: rgba(255, 255, 255, 0.05);
                padding: 2.5rem;
                border-radius: 1rem;
                border: 1px solid #334155;
                width: 100%;
                max-width: 420px;
                text-align: center;
                box-shadow: 0 10px 25px rgba(0,0,0,0.4);
                animation: fadeIn 1s ease-in-out;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-20px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .login-box h1 {
                font-size: 2.2rem;
                font-weight: 700;
                color: white;
                margin-bottom: 0.5rem;
            }

            .login-box p {
                font-size: 1rem;
                color: #A0AEC0;
                margin-bottom: 1.5rem;
            }

            .login-box h2 {
                color: white;
                margin-bottom: 0.5rem;
            }

            .login-box small {
                color: #A0AEC0;
                display: block;
                margin-bottom: 1.5rem;
            }

            /* Style input */
            div[data-testid="stTextInput"] input {
                background-color: #334155 !important;
                color: white !important;
                border: 1px solid #475569;
                border-radius: 0.5rem;
                padding: 0.6rem;
                text-align: center;
                width: 80%;
                max-width: 280px;
                margin: auto;
                display: block;
            }

            /* Style button */
            div[data-testid="stForm"] div[data-testid="stButton"] button {
                background: linear-gradient(90deg, #8B5CF6, #EC4899);
                color: white;
                font-weight: 600;
                width: 80%;
                max-width: 280px;
                border-radius: 0.5rem;
                padding: 0.6rem;
                border: none;
                margin: auto;
                display: block;
            }

            .privacy-text {
                margin-top: 1.2rem;
                color: #A0AEC0;
                font-size: 0.85rem;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- Login Form ---
    with st.container():
        # st.markdown('<div class="login-box">', unsafe_allow_html=True)

        st.markdown('<h1>💜 MindMates</h1>', unsafe_allow_html=True)
        st.markdown('<p>Your AI-powered wellness companion</p>', unsafe_allow_html=True)

        st.markdown('<h2>Welcome to Your Wellness Journey</h2>', unsafe_allow_html=True)
        st.markdown('<small>Enter your name to start tracking your mental wellness and connect with your AI companion</small>', unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("", placeholder="Enter your name...")
            submitted = st.form_submit_button("Begin Your Journey")
            if submitted:
                if username.strip():
                    st.session_state.username = username.strip()
                    st.rerun()
                else:
                    st.warning("⚠️ Please enter a name.")

        # st.markdown('<p class="privacy-text">Your data is stored locally and privately on your device</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# --- MAIN APP (Dashboard after login) ---
# --- Custom CSS for Sidebar + Dashboard ---
st.markdown("""
    <style>
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #111827;
        }
        .sidebar-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: white;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
        }
        .sidebar-title span {
            margin-right: 0.5rem;
        }
        .user-welcome {
            color: #E5E7EB;
            margin-bottom: 1.5rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }
        .user-welcome .avatar {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: #6366F1;
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
            font-size: 0.9rem;
            font-weight: bold;
        }

        /* Main Page */
        .dashboard-header {
            background: linear-gradient(90deg, #6366F1, #A855F7);
            padding: 2rem;
            border-radius: 1rem;
            color: white;
            margin-bottom: 2rem;
        }
        .feature-card {
            background: #1E293B;
            color: white;
            border-radius: 1rem;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 6px 15px rgba(0,0,0,0.3);
            transition: all 0.2s ease-in-out;
            height: 100%;
        }
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 20px rgba(0,0,0,0.4);
        }
        .feature-card h3 {
            margin-top: 1rem;
            font-size: 1.3rem;
        }
        .feature-card p {
            font-size: 0.95rem;
            color: #CBD5E1;
        }

        /* Fixed Logout Button */
        .logout-btn-container {
            position: fixed;
            bottom: 2rem;
            left: 0;
            width: 16rem; /* Sidebar width */
            z-index: 100;
            padding: 0 1rem;
        }
        @media (max-width: 768px) {
            .logout-btn-container {
                width: 100vw;
                left: 0;
                padding: 0 1rem;
            }
        }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown('<div class="sidebar-title"><span>💜</span> MindMates</div>', unsafe_allow_html=True)
    first_letter = st.session_state.username[0].upper()
    st.markdown(f"""
        <div class="user-welcome">
            <div class="avatar">{first_letter}</div>
            <span>Welcome back, <b>{st.session_state.username}</b>!</span>
        </div>
    """, unsafe_allow_html=True)

    # # Sidebar links (example placeholders)
    # st.markdown("🏠 Home")
    # st.markdown("📊 Mood Tracker")
    # st.markdown("📖 Journal & Coping")
    # st.markdown("💬 AI Companion")
    # st.markdown("📈 Wellness Dashboard")
    # st.markdown("💡 Wellness Tips")
    # st.markdown("🎵 Mood Music")

    # Static logout button at bottom
    st.markdown('<div class="logout-btn-container">', unsafe_allow_html=True)
    if st.button("🚪 Log Out", use_container_width=True, key="logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    # st.markdown("</div>", unsafe_allow_html=True)

# --- Dashboard ---
st.markdown(f"""
    <div class="dashboard-header">
        <h2>Hi {st.session_state.username}, ready to check in? 👋</h2>
        <p>Select a tool from the sidebar to begin your wellness journey.</p>
    </div>
""", unsafe_allow_html=True)

st.subheader("Your Wellness Tools")
cols = st.columns(3)

tools = [
    ("📊", "Mood Tracker", "Log your daily emotions and track mood trends."),
    ("💬", "AI Companion", "Chat with MindMate, your supportive AI friend."),
    ("🎵", "Mood Music", "Listen to personalized music for relaxation."),
]

for i, col in enumerate(cols):
    with col:
        st.markdown(f"""
            <div class="feature-card">
                <div style="font-size:3rem;">{tools[i][0]}</div>
                <h3>{tools[i][1]}</h3>
                <p>{tools[i][2]}</p>
            </div>
        """, unsafe_allow_html=True)
