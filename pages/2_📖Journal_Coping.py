import streamlit as st
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize LLM
# This will use the GROQ_API_KEY from your .env file
llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
)

# --- Start of the Streamlit page ---
st.title("🧘 Mood Journal & Coping Assistant")

mood = st.selectbox(
    "How are you feeling today?",
    ["😊 Happy", "😢 Sad", "😠 Angry", "😰 Anxious", "😐 Neutral"]
)

journal_entry = st.text_area("Write about your day:", height=200, placeholder="Let your thoughts flow...")

if st.button("Reflect & Recommend"):
    if not journal_entry.strip():
        st.warning("Please write something in your journal entry.")
    else:
        with st.spinner("Processing your emotions gently... 🌿"):
            # Reflection
            reflection_prompt = PromptTemplate.from_template("""
You are a compassionate mental wellness assistant. Read the user's mood and journal.
Reply with a warm, 1-2 line reflection that validates the mood.

Mood: {mood}
Journal Entry: {journal}
""")
            reflection = llm.invoke(reflection_prompt.format(mood=mood, journal=journal_entry))
            reflection_text = reflection.content if hasattr(reflection, 'content') else str(reflection)

            # Coping Suggestions
            coping_prompt = PromptTemplate.from_template("""
You are a mental wellness coach. Based on the user's mood and journal entry, suggest exactly 3 practical coping strategies.
Format your response EXACTLY like this example (include the numbers and dashes):

1. [Strategy 1 - specific action]
2. [Strategy 2 - specific action] 
3. [Strategy 3 - specific action]

Mood: {mood}
Journal Entry: {journal}
""")
            coping = llm.invoke(coping_prompt.format(mood=mood, journal=journal_entry))
            coping_text = coping.content if hasattr(coping, 'content') else str(coping)

        # Display results
        emoticon, emotion = mood.split(" ", 1)
        
        st.markdown("### 🌸 Reflection")
        st.markdown(f"""
        <div style="
            background: linear-gradient(to right, #fceabb, #f8b500);
            padding: 20px;
            border-radius: 15px;
            color: #000;
            font-size: 18px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            margin-bottom: 15px;">
            <strong>💬 {reflection_text.strip()}</strong><br><br>
            <em>— Based on your current feeling: {emoticon} <strong>{emotion}</strong></em>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🧰 Coping Tools")
        st.markdown("Here are a few calming strategies just for you:")
        
        # Display strategies
        if coping_text:
            strategies = [line.strip() for line in coping_text.split('\n') 
                          if line.strip() and line[0].isdigit()]
            if len(strategies) >= 3:
                for strategy in strategies[:3]:
                    st.markdown(f"✨ {strategy}")
            else:
                # Fallback if the model doesn't follow the format
                st.markdown(coping_text)
        else:
            st.warning("Couldn't generate coping strategies. Please try again.")