import streamlit as st
import pandas as pd
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from youtube_search import YoutubeSearch # This is the correct import for the 'youtube-search-python' library

# --- Setup ---
load_dotenv()
DATA_FILE = "mood_logs.csv"
if 'llm' not in st.session_state:
    st.session_state.llm = ChatGroq(temperature=0.7, model_name="llama-3.1-8b-instant")

# --- Data Connection Logic ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except pd.errors.EmptyDataError:
            return pd.DataFrame()
    return pd.DataFrame()

# --- AI Prompt for Music Suggestion ---
prompt = PromptTemplate(
    input_variables=["mood"],
    template="""You are an AI music therapist. Create a concise, effective YouTube search query for a song or playlist that matches the user's mood.
    Then, write a short, therapeutic reason explaining why this music is helpful.
    Format your response with "SEARCH_QUERY:" on the first line and "REASON:" on the second.
    User's mood: {mood}
    Response:"""
)
chain = prompt | st.session_state.llm

# --- Main Page Logic ---
st.header("🎵 Mood-to-Music Companion")

if "username" not in st.session_state or not st.session_state.username:
    st.warning("Please log in from the main page to get a music suggestion.")
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
    st.info("Log your mood in the 'Mood Tracker' page to get a personalized music suggestion!")
    st.stop()

st.success(f"Detected your latest mood: **{latest_mood}**. Ready to find some music?")

if st.button(f"Find Music for a '{latest_mood}' Mood", use_container_width=True):
    with st.spinner("Asking our AI music therapist... 🎶"):
        response = chain.invoke({"mood": latest_mood})
        response_content = response.content if hasattr(response, 'content') else str(response)

        try:
            lines = response_content.strip().split('\n')
            search_query = lines[0].replace("SEARCH_QUERY:", "").strip()
            therapeutic_reason = lines[1].replace("REASON:", "").strip()
        except IndexError:
            search_query = f"{latest_mood} music"
            therapeutic_reason = "This music is chosen to match your current emotional state."

        st.markdown(f"**MindMate's Recommendation:** *{therapeutic_reason}*")
        
        try:
            results_list = YoutubeSearch(search_query, max_results=1).to_dict()
            if results_list:
                video_id = results_list[0]['id']
                music_url = f"https://www.youtube.com/watch?v={video_id}"
                st.video(music_url)
            else:
                st.error("Could not find any music for your mood. Please try again.")
        except Exception as e:
            st.error(f"An error occurred while searching for music: {e}")