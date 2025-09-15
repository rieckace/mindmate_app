import streamlit as st
import pandas as pd
import os
import datetime
import random

# --- File Paths and Constants ---
DATA_FILE = "mood_logs.csv"
ROUTINE_FILE = "routines.csv"

# --- Custom CSS for Styling ---
def add_custom_css():
    st.markdown("""
        <style>
            .tip-card {
                background-color: #262730; border-radius: 1rem; padding: 1.5rem;
                margin-bottom: 1rem; border: 1px solid #333;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .tip-card p { font-size: 1.1rem; color: #E0E0E0; }
            .routine-container {
                background-color: #1E293B; border-radius: 1rem;
                padding: 2rem; border: 1px solid #334155;
            }
        </style>
    """, unsafe_allow_html=True)

# --- Data Connection Logic ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=["date", "mood", "note", "username"])
    return pd.DataFrame(columns=["date", "mood", "note", "username"])

# --- Helper Functions ---
def generate_wellness_tips(mood):
    tips_database = {
        "Happy": ["Share your joy with someone.", "Take a moment to savor a happy memory.", "Channel this energy into a creative project."],
        "Sad": ["Listen to some comforting music.", "Write down your feelings without judgment.", "Reach out to a friend or family member."],
        "Anxious": ["Try the 5-4-3-2-1 grounding technique.", "Practice slow, deep breaths for two minutes.", "Step outside for some fresh air."],
        "Angry": ["Engage in some physical activity to release energy.", "Scribble on a piece of paper and then tear it up.", "Listen to intense music that matches your energy."],
        "Neutral": ["Take a moment to check in with yourself.", "Plan one small, enjoyable activity for later.", "Read a chapter of a book."],
        "Calm": ["Enjoy the stillness with some gentle stretching.", "Practice mindfulness of your surroundings.", "Do a simple, focused task you enjoy."]
    }
    mood_tips = tips_database.get(mood, tips_database.get("Calm"))
    return random.sample(mood_tips, min(2, len(mood_tips)))

def save_routine(date, activities, username):
    df_new = pd.DataFrame({
        "date": [date] * len(activities),
        "activity": activities,
        "username": [username] * len(activities)
    })
    
    if os.path.exists(ROUTINE_FILE):
        try:
            df_existing = pd.read_csv(ROUTINE_FILE)
            df_existing = df_existing[~((df_existing["username"] == username) & (df_existing["date"] == date))]
            df_final = pd.concat([df_existing, df_new], ignore_index=True)
        except pd.errors.EmptyDataError:
            df_final = df_new
    else:
        df_final = df_new
    df_final.to_csv(ROUTINE_FILE, index=False)

def load_today_routine(date, username):
    if os.path.exists(ROUTINE_FILE):
        try:
            df = pd.read_csv(ROUTINE_FILE)
            if "username" in df.columns and "date" in df.columns:
                user_routine = df[(df["username"] == username) & (df["date"] == date)]
                return user_routine["activity"].tolist()
        except pd.errors.EmptyDataError:
            return []
    return []

# --- UI Builder ---
def build_routine_ui(date, username):
    st.header("🗓️ Build Your Daily Wellness Routine")
    st.markdown('<div class="routine-container">', unsafe_allow_html=True)
    
    today_routine = load_today_routine(date, username)
    
    # Use session state to track checked items
    if 'activity_states' not in st.session_state or st.session_state.get('routine_date') != date:
        st.session_state.activity_states = {activity: False for activity in today_routine}
        st.session_state.routine_date = date

    if not today_routine:
        st.info("No activities in your routine for today. Add one below!")
    else:
        st.markdown("**Your routine for today:**")
        for activity in today_routine:
            st.session_state.activity_states[activity] = st.checkbox(
                activity, 
                value=st.session_state.activity_states.get(activity, False),
                key=f"check_{activity}"
            )

    # --- NEW: Logic for Resetting Completed Activities ---
    completed_activities = [activity for activity, is_done in st.session_state.activity_states.items() if is_done]
    if completed_activities:
        if st.button("Clear Completed Activities", use_container_width=True):
            activities_to_keep = [activity for activity, is_done in st.session_state.activity_states.items() if not is_done]
            save_routine(date, activities_to_keep, username)
            # Clear the state to force a reload from the updated file
            del st.session_state.activity_states 
            st.rerun()

    with st.form("new_activity_form", clear_on_submit=True):
        new_activity = st.text_input("Add a new activity to your routine:")
        if st.form_submit_button("➕ Add Activity"):
            if new_activity.strip() and new_activity.strip() not in today_routine:
                updated_routine = today_routine + [new_activity.strip()]
                save_routine(date, updated_routine, username)
                # Clear state to ensure the new item is loaded correctly
                if 'activity_states' in st.session_state:
                    del st.session_state.activity_states
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# --- Main Page Logic ---
st.title("🌟 Personalized Wellness Tips & Routine")
add_custom_css()

if "username" not in st.session_state or not st.session_state.username:
    st.warning("Please log in from the main page to get personalized tips.")
    st.stop()

username = st.session_state.username
all_logs_df = load_data()
user_logs_df = pd.DataFrame()
if not all_logs_df.empty:
    user_logs_df = all_logs_df[all_logs_df["username"] == username]

latest_mood = None
if not user_logs_df.empty:
    user_logs_df['date'] = pd.to_datetime(user_logs_df['date'])
    latest_mood = user_logs_df.sort_values(by="date", ascending=True).iloc[-1].get("mood")

if latest_mood is None:
    st.info("Log your mood in the 'Mood Tracker' page to get personalized tips!")
    st.stop()

# --- Display Wellness Tips ---
st.markdown(f"#### Based on your latest mood: **{latest_mood}**")
tips = generate_wellness_tips(latest_mood)
for tip in tips:
    st.markdown(f'<div class="tip-card"><p>💡 {tip}</p></div>', unsafe_allow_html=True)

if st.button("🔄 Get New Tips"):
    st.rerun()

st.markdown("---")

# --- Display Routine Builder ---
date_today = datetime.date.today().isoformat()
build_routine_ui(date_today, username)