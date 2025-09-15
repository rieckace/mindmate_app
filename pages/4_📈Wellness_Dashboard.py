import streamlit as st
import pandas as pd
import os
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import calendar
import plotly.graph_objects as go
import numpy as np

# --- Data Connection Logic ---
DATA_FILE = "mood_logs.csv"
def load_data():
    if os.path.exists(DATA_FILE):
        try: 
            return pd.read_csv(DATA_FILE)
        except pd.errors.EmptyDataError: 
            return pd.DataFrame(columns=["date", "mood", "note", "username"])
    return pd.DataFrame(columns=["date", "mood", "note", "username"])

# --- Helper Functions ---
def add_dashboard_styles():
    st.markdown("""
        <style>
            .metric-card {
                background-color: #262730; 
                border-radius: 1rem; 
                padding: 1.5rem;
                text-align: center; 
                border: 1px solid #333; 
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin-bottom: 1rem;
            }
            .metric-card h3 { 
                font-size: 1.1rem; 
                color: #A1A1AA; 
                margin-bottom: 0.5rem; 
            }
            .metric-card p { 
                font-size: 2rem; 
                font-weight: 600; 
                color: #FFFFFF; 
            }
            /* Fix chart alignment */
            .stPlotlyChart {
                width: 100% !important;
            }
            /* Calendar styling */
            .calendar-container {
                margin-top: 2rem;
            }
            .calendar-day {
                border: 1px solid #333;
                padding: 0.5rem;
                text-align: center;
                border-radius: 0.5rem;
                min-height: 80px;
            }
            .calendar-day.empty {
                background-color: #1E1E1E;
            }
            .mood-5 { background-color: #4CAF50; color: white; }
            .mood-4 { background-color: #8BC34A; color: white; }
            .mood-3 { background-color: #FFEB3B; color: black; }
            .mood-2 { background-color: #FF9800; color: white; }
            .mood-1 { background-color: #F44336; color: white; }
        </style>
    """, unsafe_allow_html=True)

# --- PDF GENERATION FUNCTION ---
def generate_pdf_report(goals_checked, mood_df, username):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # --- Title ---
    p.setFont("Helvetica-Bold", 16)
    p.drawString(72, height - 72, f"🧠 MindMate - Wellness Report for {username}")
    p.setFont("Helvetica", 10)
    p.drawString(72, height - 88, f"Generated on: {datetime.date.today().strftime('%B %d, %Y')}")

    # --- Goals Checklist ---
    p.setFont("Helvetica-Bold", 12)
    p.drawString(72, height - 140, "✅ Daily Goals Checklist")
    p.setFont("Helvetica", 11)
    y_position = height - 160
    if goals_checked:
        for goal in goals_checked:
            p.drawString(90, y_position, f"- {goal}")
            y_position -= 20
    else:
        p.drawString(90, y_position, "- No goals were marked as completed.")
        y_position -= 20

    # --- Mood Trend Chart ---
    y_position -= 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(72, y_position, "📈 7-Day Mood Trend")
    y_position -= 220  # Make space for the chart

    if not mood_df.empty and len(mood_df) > 1:
        try:
            # Create a plot specifically for the PDF
            fig, ax = plt.subplots(figsize=(7, 3.5))
            ax.plot(mood_df["Date"], mood_df["Mood_Score"], marker='o', linestyle='-', color='#667eea', linewidth=2)
            
            # Styling for a light background PDF
            ax.set_title("Recent Mood Trend", fontsize=12)
            ax.set_xlabel("Date", fontsize=10)
            ax.set_ylabel("Mood Score (1-5)", fontsize=10)
            ax.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()

            # Save the plot to an in-memory buffer
            img_buffer = BytesIO()
            fig.savefig(img_buffer, format='PNG', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            
            # Draw image on PDF
            p.drawImage(ImageReader(img_buffer), 72, y_position, width=450, height=200)
            plt.close(fig)  # Close the figure to free memory
        except Exception as e:
            p.setFont("Helvetica", 11)
            p.drawString(90, y_position + 100, f"Chart error: {str(e)}")
    else:
        p.setFont("Helvetica", 11)
        p.drawString(90, y_position + 100, "Not enough mood data available to generate a chart.")

    p.save()
    buffer.seek(0)
    return buffer

# --- MONTHLY CALENDAR FUNCTION ---
def create_monthly_calendar(user_logs_df, current_date):
    # Create a calendar for the current month
    cal = calendar.monthcalendar(current_date.year, current_date.month)
    mood_mapping = {"Happy": 5, "Neutral": 3, "Anxious": 2, "Sad": 1, "Angry": 1}
    user_logs_df['Mood_Score'] = user_logs_df['mood'].map(mood_mapping).fillna(0)
    
    # Create a dictionary of mood scores by date
    mood_by_date = {}
    for _, row in user_logs_df.iterrows():
        if pd.notna(row['Date']):
            date_str = row['Date'].strftime('%Y-%m-%d')
            mood_by_date[date_str] = row['Mood_Score']
    
    # Create the calendar header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"### {current_date.strftime('%B %Y')}")
    
    # Create weekday headers
    weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    cols = st.columns(7)
    for i, col in enumerate(cols):
        col.markdown(f"**{weekdays[i]}**", help=weekdays[i])
    
    # Create the calendar grid
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.markdown('<div class="calendar-day empty"></div>', unsafe_allow_html=True)
                else:
                    date_str = f"{current_date.year}-{current_date.month:02d}-{day:02d}"
                    mood_score = mood_by_date.get(date_str, 0)
                    
                    if mood_score > 0:
                        mood_class = f"mood-{int(mood_score)}"
                        mood_emoji = {5: "😄", 4: "😊", 3: "😐", 2: "😟", 1: "😢"}.get(int(mood_score), "")
                        st.markdown(f'''
                            <div class="calendar-day {mood_class}">
                                <strong>{day}</strong><br>
                                {mood_emoji}
                            </div>
                        ''', unsafe_allow_html=True)
                    else:
                        st.markdown(f'''
                            <div class="calendar-day">
                                <strong>{day}</strong>
                            </div>
                        ''', unsafe_allow_html=True)

# --- Main Page Logic ---
st.title("📊 Wellness Dashboard")
add_dashboard_styles()

if "username" not in st.session_state or not st.session_state.username:
    st.warning("Please log in from the main page to view your dashboard.")
    st.stop()

username = st.session_state.username
all_logs_df = load_data()
user_logs_df = pd.DataFrame()
if not all_logs_df.empty:
    user_logs_df = all_logs_df[all_logs_df["username"] == username]

if user_logs_df.empty:
    st.info("Your dashboard is waiting! Log your mood in the 'Mood Tracker' to see your trends.")
    st.stop()

# --- Process Data ---
user_logs_df['Date'] = pd.to_datetime(user_logs_df['date'])
mood_mapping = {"Happy": 5, "Neutral": 3, "Anxious": 2, "Sad": 1, "Angry": 1}
user_logs_df['Mood_Score'] = user_logs_df['mood'].map(mood_mapping).fillna(3)

# --- Tabbed Layout ---
tab1, tab2 = st.tabs(["📈 Weekly Summary", "📅 Monthly Calendar"])

with tab1:
    today = pd.to_datetime(datetime.date.today())
    seven_days_ago = today - pd.to_timedelta('6D')
    df_week = user_logs_df[user_logs_df['Date'] >= seven_days_ago].copy()
    
    if not df_week.empty:
        df_week.sort_values(by="Date", inplace=True)
        
        # Top Metric Cards
        st.markdown("### **Your Week at a Glance**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_mood = df_week['Mood_Score'].mean()
            st.markdown(f'''
                <div class="metric-card">
                    <h3>Average Mood</h3>
                    <p>{avg_mood:.1f}/5</p>
                </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            entries_count = len(df_week)
            st.markdown(f'''
                <div class="metric-card">
                    <h3>Entries This Week</h3>
                    <p>{entries_count}</p>
                </div>
            ''', unsafe_allow_html=True)
        
        with col3:
            dominant_mood = df_week['mood'].mode()[0] if not df_week['mood'].mode().empty else "No data"
            st.markdown(f'''
                <div class="metric-card">
                    <h3>Most Common Mood</h3>
                    <p>{dominant_mood}</p>
                </div>
            ''', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 7-Day Mood Trend Chart
        st.markdown("### **Your 7-Day Mood Trend**")
        if len(df_week) > 1:
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(df_week["Date"], df_week["Mood_Score"], marker='o', linestyle='-', color='#667eea', linewidth=2)
            ax.set_ylim(0, 6)
            ax.set_yticks([1, 2, 3, 4, 5])
            ax.set_yticklabels(["😢 Sad", "😟 Anxious", "😐 Neutral", "😊 Good", "😄 Happy"])
            ax.grid(True, alpha=0.3)
            ax.set_title("Your Mood Over the Past Week")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("Not enough data to show a trend chart. Log more moods to see your pattern!")
        
        # Goals and Download Section
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.markdown("### **Daily Goals**")
            goals = ["Drink 2L water", "Walk 5,000 steps", "Journaling", "Read for 30 mins", "Reflect"]
            checked_goals = []
            for goal in goals:
                if st.checkbox(goal, key=f"goal_{goal}"):
                    checked_goals.append(goal)
        
        with col_right:
            st.markdown("### **Download Report**")
            if st.button("📥 Generate PDF Report", use_container_width=True):
                pdf_buffer = generate_pdf_report(checked_goals, df_week, username)
                st.download_button(
                    label="Download Full Report (PDF)",
                    data=pdf_buffer,
                    file_name=f"MindMate_Report_{username}_{datetime.date.today()}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

with tab2:
    st.markdown("### **Your Monthly Mood Calendar**")
    
    # Month navigation
    current_date = datetime.date.today()
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Previous Month"):
            st.session_state.calendar_date = current_date - datetime.timedelta(days=current_date.day)
            st.rerun()
    
    with col3:
        if st.button("Next Month →"):
            next_month = current_date.replace(day=28) + datetime.timedelta(days=4)
            st.session_state.calendar_date = next_month.replace(day=1)
            st.rerun()
    
    # Initialize calendar date in session state
    if 'calendar_date' not in st.session_state:
        st.session_state.calendar_date = current_date
    
    # Create the calendar
    create_monthly_calendar(user_logs_df, st.session_state.calendar_date)
    
    # Legend
    st.markdown("---")
    st.markdown("**Mood Legend:**")
    legend_cols = st.columns(5)
    moods = [
        ("😄 Happy", "mood-5", "#4CAF50"),
        ("😊 Good", "mood-4", "#8BC34A"), 
        ("😐 Neutral", "mood-3", "#FFEB3B"),
        ("😟 Anxious", "mood-2", "#FF9800"),
        ("😢 Sad/Angry", "mood-1", "#F44336")
    ]
    
    for i, (label, _, color) in enumerate(moods):
        with legend_cols[i]:
            st.markdown(f'<div style="background-color: {color}; padding: 0.5rem; border-radius: 0.5rem; text-align: center; color: white;">{label}</div>', 
                       unsafe_allow_html=True)