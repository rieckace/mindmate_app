import streamlit as st
import datetime
import pandas as pd
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

# --- Page Configuration and Custom CSS ---
st.set_page_config(page_title="AI Companion", page_icon="🧠")

def add_custom_css():
    st.markdown("""
        <style>
            .chat-container {
                display: flex; flex-direction: column; height: 65vh;
                overflow-y: auto; padding: 10px; border: 1px solid #333;
                border-radius: 10px; background-color: #1E1E2E;
            }
            .chat-message {
                padding: 10px 15px; border-radius: 20px; margin-bottom: 10px;
                max-width: 75%; color: white; width: fit-content;
            }
            .chat-message.user {
                background-color: #4A4A6A; align-self: flex-end;
            }
            .chat-message.assistant {
                background-color: #2C3E50; align-self: flex-start;
            }
            .chat-message.assistant blockquote {
                border-left: 4px solid #667eea; padding-left: 1rem;
                margin-left: 0; font-style: italic; color: #d1d5db;
            }
            .chat-message.assistant img {
                max-width: 100%; border-radius: 10px; margin-top: 10px;
            }
            .stChatInputContainer {
                position: fixed; bottom: 1rem; width: calc(100% - 2rem); 
                background-color: #0E0E17; padding: 0.5rem; 
                border-radius: 10px; margin: 0 1rem;
            }
        </style>
    """, unsafe_allow_html=True)

add_custom_css()

# --- Backend Logic ---
load_dotenv()
if 'llm' not in st.session_state:
    st.session_state.llm = ChatGroq(temperature=0.7, model_name="llama-3.1-8b-instant")
DATA_FILE = "mood_logs.csv"

# --- Session State Initialization ---
# Initialize all session state variables with proper default values
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'processing' not in st.session_state:
    st.session_state.processing = False

if 'user_input' not in st.session_state:
    st.session_state.user_input = None

if 'last_input' not in st.session_state:
    st.session_state.last_input = None

# --- Data Connection Logic ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=["date", "mood", "note", "username"])
    return pd.DataFrame(columns=["date", "mood", "note", "username"])

def format_history(messages):
    history_str = ""
    for msg in messages:
        role = "User" if msg["role"] == "user" else "MindMate"
        history_str += f"{role}: {msg['content']}\n"
    return history_str

def get_conversation_prompt(history, current_input, mood_context):
    return f"""
You are MindMate, an AI companion designed to respond with a {mood_context.lower()} tone based on the user's mood history.

Previous conversation:
{history}

Current user message: {current_input}

Respond in a {mood_context.lower()} and supportive manner. Keep your response concise but empathetic.
Response:
"""

def get_suggestion_prompt(suggestion_type):
    prompts = {
        "💡 Motivational Quote": "Share a brief motivational quote that's uplifting but not overly cheerful.",
        "🧘 Calm Me Down": "Provide a short calming technique or breathing exercise for anxiety.",
        "🌿 Mindfulness Tip": "Offer a quick mindfulness exercise that can be done in under a minute."
    }
    return prompts.get(suggestion_type, "Provide supportive response.")

# --- Main Page Logic ---
st.header("🧠 AI Companion Chat - MindMate")

if "username" not in st.session_state or not st.session_state.username:
    st.warning("Please log in from the main page to use the AI Companion.")
    st.stop()

username = st.session_state.username
all_logs_df = load_data()
user_logs_df = pd.DataFrame()

if not all_logs_df.empty:
    user_logs_df = all_logs_df[all_logs_df["username"] == username]

latest_mood = "Calm"
if not user_logs_df.empty and 'date' in user_logs_df.columns:
    user_logs_df['date'] = pd.to_datetime(user_logs_df['date'])
    latest_mood = user_logs_df.sort_values(by="date", ascending=False).iloc[0].get("mood", "Calm")

st.info(f"MindMate is responding with a **{latest_mood.lower()}** tone based on your last entry.")

# Display chat messages
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(name=msg["role"]):
            st.markdown(msg["content"])

# --- Input Handling ---
def handle_suggestion(prompt):
    if not st.session_state.processing:
        st.session_state.user_input = prompt
        st.session_state.processing = True

st.subheader("✨ Quick Suggestions")
cols = st.columns(3)
quick_suggestion_prompts = {
    "💡 Motivational Quote": "Share a motivational quote.",
    "🧘 Calm Me Down": "I feel anxious, can you help calm me down?",
    "🌿 Mindfulness Tip": "Give me a short mindfulness exercise."
}

for i, (label, prompt_text) in enumerate(quick_suggestion_prompts.items()):
    cols[i].button(label, on_click=handle_suggestion, args=[prompt_text], use_container_width=True)

# Get user input
user_input = st.chat_input("Type your message here...")

# Process input from chat box or button clicks
if user_input:
    st.session_state.user_input = user_input
    st.session_state.processing = True

# Process the input only if we have new input and not currently processing another request
if (st.session_state.user_input is not None and 
    st.session_state.processing and 
    st.session_state.user_input != st.session_state.last_input):
    
    user_prompt = st.session_state.user_input
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    
    with st.spinner("MindMate is thinking..."):
        try:
            # Determine which prompt template to use
            if user_prompt in quick_suggestion_prompts.values():
                # Find the key for the suggestion prompt
                suggestion_type = [k for k, v in quick_suggestion_prompts.items() if v == user_prompt][0]
                prompt_template = get_suggestion_prompt(suggestion_type)
                response = st.session_state.llm.invoke(prompt_template)
            else:
                history = format_history(st.session_state.messages[:-1])
                prompt_template = get_conversation_prompt(history, user_prompt, latest_mood)
                response = st.session_state.llm.invoke(prompt_template)
            
            ai_response_content = response.content if hasattr(response, 'content') else str(response)
            
            # Add AI response to chat history
            st.session_state.messages.append({"role": "assistant", "content": ai_response_content})
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.session_state.messages.append({"role": "assistant", "content": "I apologize, but I'm experiencing technical difficulties. Please try again."})
    
    # Reset processing state and update last_input
    st.session_state.processing = False
    st.session_state.last_input = user_prompt
    st.session_state.user_input = None
    
    # Rerun to update the UI with new messages
    st.rerun()