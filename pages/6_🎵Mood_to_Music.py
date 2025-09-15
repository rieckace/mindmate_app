import streamlit as st
import pandas as pd
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from youtube_search import YoutubeSearch
import random

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

# --- Custom CSS for Enhanced UI ---
st.markdown("""
    <style>
        .music-header {
            background: linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%);
            padding: 2rem;
            border-radius: 1rem;
            color: white;
            margin-bottom: 2rem;
            text-align: center;
        }
        .video-card {
            background: rgba(30, 41, 59, 0.7);
            border-radius: 1rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }
        .video-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(139, 92, 246, 0.3);
        }
        .recommendation-reason {
            background: rgba(139, 92, 246, 0.15);
            padding: 1.2rem;
            border-radius: 0.75rem;
            border-left: 4px solid #8B5CF6;
            margin: 1.5rem 0;
            font-style: italic;
        }
        .language-pill {
            display: inline-block;
            background: rgba(139, 92, 246, 0.2);
            color: #E9D5FF;
            padding: 0.4rem 1rem;
            border-radius: 2rem;
            margin: 0.3rem;
            font-size: 0.9rem;
            border: 1px solid rgba(139, 92, 246, 0.3);
        }
        .language-pill.active {
            background: linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%);
            color: white;
            font-weight: 600;
        }
        .stButton button {
            background: linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%);
            color: white;
            border: none;
            border-radius: 0.75rem;
            padding: 0.8rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(139, 92, 246, 0.4);
        }
    </style>
""", unsafe_allow_html=True)

# --- Language Options ---
LANGUAGE_OPTIONS = {
    "English": "English",
    "Hindi": "Hindi",
    "Spanish": "Spanish",
    "French": "French",
    "Korean": "Korean",
    "Japanese": "Japanese",
    "Tamil": "Tamil",
    "Telugu": "Telugu",
    "Punjabi": "Punjabi",
    "All Languages": "All Languages"
}

# --- AI Prompt for Music Suggestion ---
def get_music_prompt(mood, language):
    return PromptTemplate(
        input_variables=["mood", "language"],
        template="""You are an AI music therapist. Create 3 different concise YouTube search queries for songs or playlists that match the user's mood and preferred language.
        Then, write a short, therapeutic reason explaining why this music is helpful.
        
        Format your response exactly as follows:
        SEARCH_QUERY_1: [first search query]
        SEARCH_QUERY_2: [second search query] 
        SEARCH_QUERY_3: [third search query]
        REASON: [therapeutic reason]
        
        User's mood: {mood}
        Preferred language: {language}
        Response:"""
    )

# --- YouTube Search Function ---
def search_youtube_videos(query, max_results=5):
    try:
        results = YoutubeSearch(query, max_results=max_results).to_dict()
        return results
    except Exception as e:
        st.error(f"Search error: {str(e)}")
        return []

# --- Main Page Logic ---
st.markdown("""
    <div class="music-header">
        <h1>🎵 Mood-to-Music Companion</h1>
        <p>Discover music that resonates with your emotions</p>
    </div>
""", unsafe_allow_html=True)

if "username" not in st.session_state or not st.session_state.username:
    st.warning("Please log in from the main page to get music suggestions.")
    st.stop()

username = st.session_state.username
all_logs_df = load_data()
user_logs_df = pd.DataFrame()
if not all_logs_df.empty:
    user_logs_df = all_logs_df[all_logs_df["username"] == username]

latest_mood = None
if not user_logs_df.empty:
    user_logs_df['date'] = pd.to_datetime(user_logs_df['date'])
    latest_mood = user_logs_df.sort_values(by="date", ascending=False).iloc[0].get("mood")

if latest_mood is None:
    st.info("Log your mood in the 'Mood Tracker' page to get personalized music suggestions!")
    st.stop()

# Display detected mood
st.success(f"Detected your latest mood: **{latest_mood}**")

# Language selection
st.subheader("🎯 Select Your Preferred Language")
st.markdown("Choose the language for music recommendations:")

# Create language pills
cols = st.columns(6)
language_keys = list(LANGUAGE_OPTIONS.keys())
selected_language = "All Languages"

for i, lang in enumerate(language_keys):
    with cols[i % 6]:
        if st.button(lang, key=f"lang_{lang}", use_container_width=True):
            selected_language = lang

st.markdown(f"**Selected:** <span class='language-pill'>{selected_language}</span>", unsafe_allow_html=True)
st.markdown("---")

# Music recommendation section
if st.button(f"🎵 Find Music for '{latest_mood}' Mood", use_container_width=True, type="primary"):
    with st.spinner("Consulting our AI music therapist... 🎶"):
        # Get AI recommendation
        prompt_template = get_music_prompt(latest_mood, selected_language)
        chain = prompt_template | st.session_state.llm
        
        try:
            response = chain.invoke({"mood": latest_mood, "language": selected_language})
            response_content = response.content if hasattr(response, 'content') else str(response)
            
            # Parse response
            lines = response_content.strip().split('\n')
            search_queries = []
            therapeutic_reason = ""
            
            for line in lines:
                if line.startswith('SEARCH_QUERY_'):
                    search_queries.append(line.split(':', 1)[1].strip())
                elif line.startswith('REASON:'):
                    therapeutic_reason = line.split(':', 1)[1].strip()
            
            # If parsing failed, use fallback
            if not search_queries:
                search_queries = [
                    f"{latest_mood} {selected_language} music",
                    f"{latest_mood} songs {selected_language}",
                    f"{selected_language} music for {latest_mood} mood"
                ]
                therapeutic_reason = "This music is chosen to match your current emotional state and language preference."
            
            # Display recommendation reason
            st.markdown(f"""
                <div class="recommendation-reason">
                    💡 <strong>AI Music Therapist's Insight:</strong> {therapeutic_reason}
                </div>
            """, unsafe_allow_html=True)
            
            # Search for videos for each query
            all_videos = []
            for query in search_queries:
                videos = search_youtube_videos(query, max_results=2)
                all_videos.extend(videos)
            
            # Remove duplicates by video ID
            seen_ids = set()
            unique_videos = []
            for video in all_videos:
                if video['id'] not in seen_ids:
                    seen_ids.add(video['id'])
                    unique_videos.append(video)
            
            # Display videos
            if unique_videos:
                st.subheader("🎧 Recommended Music Videos")
                st.markdown(f"Found **{len(unique_videos)}** videos matching your **{latest_mood}** mood in **{selected_language}**")
                
                for i, video in enumerate(unique_videos[:5]):  # Limit to 5 videos
                    with st.container():
                        st.markdown(f"### {i+1}. {video['title']}")
                        
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            video_url = f"https://www.youtube.com/watch?v={video['id']}"
                            st.video(video_url)
                        
                        with col2:
                            st.markdown(f"""
                                **Channel:** {video['channel']}  
                                **Duration:** {video['duration']}  
                                **Published:** {video['publish_time']}
                            """)
                            
                            # Additional metadata
                            st.markdown(f"""
                                <div style="margin-top: 1rem;">
                                    <a href="{video_url}" target="_blank" style="text-decoration: none;">
                                        <button style="background: #FF0000; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.5rem; cursor: pointer;">
                                            ▶ Watch on YouTube
                                        </button>
                                    </a>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("---")
            else:
                st.error("Could not find any music videos. Please try different search terms or check your internet connection.")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.info("Please try again or check your API key configuration.")

# Alternative manual search option
st.markdown("---")
st.subheader("🔍 Manual Music Search")

manual_query = st.text_input("Or search for specific music:", placeholder="E.g., Relaxing piano music, Happy pop songs, etc.")
manual_language = st.selectbox("Select language for manual search:", options=list(LANGUAGE_OPTIONS.keys()))

if st.button("Search Manual Query", use_container_width=True):
    if manual_query:
        search_term = f"{manual_query} {LANGUAGE_OPTIONS[manual_language]}" if manual_language != "All Languages" else manual_query
        with st.spinner(f"Searching for '{search_term}'..."):
            videos = search_youtube_videos(search_term, max_results=5)
            
            if videos:
                st.subheader("🎵 Search Results")
                for i, video in enumerate(videos):
                    with st.container():
                        st.markdown(f"### {i+1}. {video['title']}")
                        video_url = f"https://www.youtube.com/watch?v={video['id']}"
                        st.video(video_url)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Channel:** {video['channel']}")
                        with col2:
                            st.markdown(f"**Duration:** {video['duration']}")
                        
                        st.markdown(f"[Watch on YouTube]({video_url})")
                        st.markdown("---")
            else:
                st.warning("No videos found for your search query. Please try different keywords.")
    else:
        st.warning("Please enter a search query first.")

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 3rem;">
        <p>Powered by YouTube Music • AI-Powered Recommendations • Personalized for You</p>
    </div>
""", unsafe_allow_html=True)