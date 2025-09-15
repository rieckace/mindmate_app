import streamlit as st
import datetime
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os
import traceback
from deepface import DeepFace
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import tempfile
import cv2
import numpy as np

# --- AI and Environment Setup ---
load_dotenv()
if 'llm' not in st.session_state:
    st.session_state.llm = ChatGroq(temperature=0, model_name="llama-3.1-8b-instant")
DATA_FILE = "mood_logs.csv"

# --- Data Persistence Functions ---
def load_data():
    if os.path.exists(DATA_FILE):
        try: 
            return pd.read_csv(DATA_FILE)
        except pd.errors.EmptyDataError: 
            return pd.DataFrame(columns=["date", "mood", "note", "username"])
    return pd.DataFrame(columns=["date", "mood", "note", "username"])

def save_data(all_data_df):
    if 'note' not in all_data_df.columns: 
        all_data_df['note'] = ''
    all_data_df['note'] = all_data_df['note'].fillna('')
    all_data_df.to_csv(DATA_FILE, index=False)
    
def add_new_log(username, new_log_entry):
    all_data = load_data().to_dict('records')
    new_log_entry['username'] = username
    all_data.append(new_log_entry)
    save_data(pd.DataFrame(all_data))
    
def clear_today_log(username, today_iso):
    df = load_data()
    df_filtered = df[~((df['username'] == username) & (df['date'] == today_iso))]
    save_data(df_filtered)

# --- Helper Functions ---
def get_temp_file_path(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        return tmp_file.name
        
def analyze_mood_from_text(text_note):
    prompt = PromptTemplate(input_variables=["note"], 
                           template="Analyze a journal entry. Classify mood: Happy, Sad, Anxious, Angry, Neutral. Respond ONLY with the single word. Entry: \"{note}\" Mood:")
    chain = prompt | st.session_state.llm
    return chain.invoke({"note": text_note}).content.strip()

def detect_emotion_from_face(face_image):
    """
    Fixed face emotion detection without the 'silent' parameter
    Based on DeepFace documentation and compatibility requirements
    """
    img_path = None
    try:
        # Save the uploaded image to a temporary file path
        img_path = get_temp_file_path(face_image)
        
        # Try multiple detectors in order of reliability
        detectors = ['retinaface', 'mtcnn', 'opencv', 'ssd', 'dlib']
        detected_mood = None
        
        for detector in detectors:
            try:
                # Remove the 'silent' parameter as it's not supported
                analysis = DeepFace.analyze(
                    img_path=img_path,
                    actions=['emotion'],
                    enforce_detection=True,
                    detector_backend=detector
                    # 'silent' parameter removed to fix the error
                )
                
                if isinstance(analysis, list) and len(analysis) > 0:
                    detected_mood = analysis[0]['dominant_emotion'].capitalize()
                    st.success(f"Face detected using {detector} backend")
                    break
                    
            except Exception as e:
                st.write(f"Detector {detector} failed: {str(e)}")
                continue
        
        # Fallback with enforce_detection=False
        if detected_mood is None:
            try:
                analysis = DeepFace.analyze(
                    img_path=img_path,
                    actions=['emotion'],
                    enforce_detection=False,
                    detector_backend='opencv'
                    # 'silent' parameter removed to fix the error
                )
                
                if isinstance(analysis, list) and len(analysis) > 0:
                    detected_mood = analysis[0]['dominant_emotion'].capitalize()
                    st.info("Face detected with low confidence")
            except Exception as e:
                st.error(f"All detection methods failed: {str(e)}")
                return None
        
        return detected_mood

    except Exception as e:
        st.error(f"Face analysis error: {str(e)}")
        # Provide user guidance for better detection
        st.info("""
        💡 **Tips for better face detection:**
        - Ensure good lighting on your face
        - Face the camera directly
        - Remove obstructions like glasses or masks
        - Make sure your face is clearly visible
        - Try to maintain a neutral expression
        """)
        return None
    finally:
        # Clean up the temporary file
        if img_path and os.path.exists(img_path):
            os.remove(img_path)
            
            
            
# --- PDF Report Generation ---
def split_text(text, max_chars):
    words = str(text).split()
    lines, line = [], ""
    for word in words:
        if len(line + " " + word) <= max_chars:
            line += " " + word if line else word
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines

def generate_summary(logs):
    mood_count = {}
    for entry in logs:
        mood = entry["mood"]
        mood_count[mood] = mood_count.get(mood, 0) + 1
    return mood_count

def generate_pdf(log_data):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50
    
    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, y, "🧠 MindMates Mood Log Report")
    y -= 20
    
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(50, y, f"Generated for {log_data[0]['username']} on: {datetime.datetime.now().strftime('%B %d, %Y')}")
    y -= 30
    
    mood_summary = generate_summary(log_data)
    total_logs = len(log_data)
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Total Entries: {total_logs}")
    y -= 20
    
    p.setFont("Helvetica", 11)
    for mood, count in mood_summary.items():
        p.drawString(70, y, f"• {mood}: {count}")
        y -= 15
    
    y -= 10
    p.line(50, y, width - 50, y)
    y -= 30
    
    p.setFont("Helvetica", 12)
    entry_number = 1
    
    for entry in reversed(log_data):
        if y < 100:
            p.showPage()
            y = height - 50
            p.setFont("Helvetica", 12)
        
        p.setFillColor(colors.darkblue)
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, f"{entry_number}. {entry['date']} — {entry['mood']}")
        y -= 20
        
        note = entry.get('note', '')
        if pd.notna(note) and str(note).strip():
            p.setFont("Helvetica", 11)
            p.setFillColor(colors.black)
            wrapped_lines = split_text(note, 85)
            for line in wrapped_lines:
                p.drawString(70, y, "📝 " + line)
                y -= 15
            y -= 5
        
        p.setFillColor(colors.grey)
        p.line(50, y, width - 50, y)
        y -= 25
        entry_number += 1
    
    p.save()
    buffer.seek(0)
    return buffer

# --- Main Page Logic ---
st.title("🧠 Mood Tracker")

if "username" not in st.session_state or not st.session_state.username:
    st.warning("Please go to the main page and enter your name to start.")
    st.stop()

username = st.session_state.username
st.markdown(f"Logging mood for **{username}**.")

all_logs_df = load_data()
user_logs = all_logs_df[all_logs_df["username"] == username].to_dict('records')

today = datetime.date.today().isoformat()
already_logged_today = any(entry["date"] == today for entry in user_logs)

if already_logged_today:
    st.success("✅ You've already logged your mood today. See your history and analysis below.")
    if st.button("Log a Different Mood for Today"):
        clear_today_log(username, today)
        st.rerun()
else:
    tab1, tab2 = st.tabs(["✍️ Log with Text/Emoji", "📸 Scan with AI"])
    
    with tab1:
        with st.form("mood_form", clear_on_submit=True):
            st.info("💡 If you write a note, the AI will analyze your text to determine the mood.")
            moods = ["😄 Happy", "😐 Neutral", "😟 Anxious", "😢 Sad", "😠 Angry"]
            mood_selection = st.radio("Select an emoji:", options=moods, index=None, horizontal=True)
            note = st.text_area("How was your day?", placeholder="Share your thoughts...")
            submitted = st.form_submit_button("Log Mood")
            
            if submitted:
                final_mood = ""
                if note.strip():
                    with st.spinner("Analyzing your thoughts..."):
                        final_mood = analyze_mood_from_text(note)
                elif mood_selection:
                    final_mood = mood_selection.split(" ")[1]
                else:
                    st.warning("Please either select a mood or write a note.")
                    st.stop()
                
                entry = {"date": today, "mood": final_mood, "note": note.strip()}
                add_new_log(username, entry)
                st.success(f"Mood logged as: **{final_mood}**")
                st.rerun()

    with tab2:
        st.subheader("Let AI detect your mood")
        st.info("💡 For best results: Ensure good lighting, face the camera directly, and remove sunglasses/hats")
        
        face_image = st.camera_input("Take a picture to detect your mood")
        
        if face_image:
            # Display the captured image for user confirmation
            st.image(face_image, caption="Captured Image", use_column_width=True)
            
            detected_mood = None
            with st.spinner("Analyzing your expression..."):
                detected_mood = detect_emotion_from_face(face_image)
            
            if detected_mood:
                entry = {"date": today, "mood": detected_mood, "note": "Auto-detected via face scan"}
                add_new_log(username, entry)
                st.success(f"😊 Detected Mood: **{detected_mood}**")
                
                # Add confirmation buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Confirm and Save", key="confirm_mood"):
                        st.rerun()
                with col2:
                    if st.button("Try Again", key="retry_mood"):
                        st.session_state.retry_face = True
                        st.rerun()
            else:
                st.error("""
                **Face analysis failed.** Possible reasons:
                - No face detected in the image
                - Poor lighting conditions
                - Face obstructed or not clearly visible
                """)
                st.info("Please try again or use the text entry method instead.")

# --- Mood History and Analysis Display ---
if user_logs:
    st.markdown("---")
    st.subheader("📅 Your Mood Log History")
    
    for entry in reversed(user_logs):
        mood_color_map = {"Happy": "#d4edda", "Neutral": "#e2e3e5", "Anxious": "#fff3cd", 
                         "Sad": "#d1ecf1", "Angry": "#f8d7da"}
        text_color_map = {"Happy": "#155724", "Neutral": "#383d41", "Anxious": "#856404", 
                         "Sad": "#0c5460", "Angry": "#721c24"}
        
        mood_color = mood_color_map.get(entry["mood"], "#f0f2f6")
        text_color = text_color_map.get(entry["mood"], "#333")
        note_text = entry.get('note', '')
        display_note = ""
        
        if pd.notna(note_text) and str(note_text).strip():
            display_note = f"📝 {str(note_text)}"
        
        st.markdown(f"""
        <div style="background-color:{mood_color}; color:{text_color}; padding:12px; 
                    border-left: 5px solid {text_color}; border-radius:8px; margin-bottom:10px;">
            <strong>{entry['date']}</strong><br>
            Mood: <span style="font-size:18px; font-weight:bold;">{entry['mood']}</span><br>
            {display_note}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📊 Mood Analysis & Report")
    
    mood_summary = generate_summary(user_logs)
    if mood_summary:
        # Create the plot with a dark theme to match your app
        plt.style.use('dark_background')
        fig, ax = plt.subplots()
        
        bars = ax.bar(mood_summary.keys(), mood_summary.values(), color="#8B5CF6")
        
        # Add data labels on top of each bar for clarity
        ax.bar_label(bars, padding=3, color='white')

        # Styling the chart for better readability
        ax.set_ylabel("Count of Days", color='white')
        ax.set_title("Mood Distribution", color='white')
        ax.tick_params(axis='x', colors='white', rotation=25)
        ax.tick_params(axis='y', colors='white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Ensure Y-axis uses whole numbers and has a better scale
        max_count = max(mood_summary.values())
        ax.set_ylim(0, max(max_count + 1, 4))  # Set a minimum height of 4 for scale
        ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))

        st.pyplot(fig)

        # Improved layout for the download button
        st.markdown("<br>", unsafe_allow_html=True)
        _, col2, _ = st.columns([1.5, 1, 1.5])
        with col2:
            pdf_buffer = generate_pdf(user_logs)
            st.download_button(
                "📥 Download Full Report (PDF)", 
                pdf_buffer, 
                "MindMates_Mood_Log.pdf", 
                "application/pdf", 
                use_container_width=True
            )