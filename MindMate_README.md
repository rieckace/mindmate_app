
# 🧠 MindMate: Your AI Companion for Mental Wellness

**MindMate** is a personalized mental wellness app built with 💻 Streamlit, 🧠 LLMs (via Groq), 🧩 LangChain, and 📊 Plotly — designed to help users track moods, journal emotions, engage with an empathetic AI companion, build healthy routines, and visualize their mental health journey.

---

## 🌟 Features

### ✅ Phase 1: Mood Tracker
- Select your daily mood from intuitive emojis.
- Mood entries are time-stamped and stored locally in session.
- Enables daily emotional awareness.

### ✅ Phase 2: Mood Journal & Coping Tools
- Write down daily reflections and emotional thoughts.
- Access AI-picked coping strategies: breathing exercises, grounding, etc.
- Simple journaling meets supportive self-care.

### ✅ Phase 3: AI Companion Chat 🤖
- Chat with an LLM-powered companion trained to:
  - Offer support
  - Encourage wellness habits
  - Provide comforting responses with emojis 😊
- Uses **Groq API** with **LLaMA 3** or **Mixtral** via LangChain.

### ✅ Phase 4: Daily Wellness Dashboard 📊
- Visualize your weekly mood trends with a beautiful Plotly graph.
- Get daily affirmations and a motivational quote.
- Track progress toward simple wellness goals (e.g., water, mindfulness, gratitude).

### ✅ Phase 5: Daily Routine Builder 🗓️
- Add, edit, delete custom wellness activities.
- Mark tasks as completed with checkboxes.
- Keeps you accountable and organized.

---

## 🧠 Tech Stack & Tools

| Category        | Tools / Models                                     |
|----------------|-----------------------------------------------------|
| UI Framework   | `Streamlit`                                         |
| Charts         | `Plotly`                                            |
| LLM            | `LLaMA 3 8B` or `Mixtral 8x7B` via `Groq API`       |
| LLM Framework  | `LangChain` (`LLMChain`, `PromptTemplate`, `ChatGroq`) |
| Embeddings     | (Planned) `bge-small-en-v1.5`, `all-MiniLM-L6-v2`   |
| State Handling | `st.session_state`                                  |
| Others         | `datetime`, `random`, `HTML/CSS` styling           |

---

## 📁 Project Structure

```
MindMate/
│
├── main.py                        # App entry point
├── mood_tracker.py               # Phase 1
├── mood_journal_and_coping.py    # Phase 2
├── ai_companion.py               # Phase 3
├── wellness_dashboard.py         # Phase 4
├── routine_builder.py            # Phase 5
├── assets/                       # (Optional) future sound files, icons, etc.
├── README.md                     # You are here ✅
```

---

## 🧭 How It Works

1. Launch the app using Streamlit:
   ```bash
   streamlit run main.py
   ```

2. Navigate through tabs for:
   - Logging moods
   - Journaling and coping tools
   - Talking to the AI
   - Viewing progress
   - Creating daily routines

3. All user inputs are stored in `st.session_state`. No database required (yet).

---

## 🔮 Upcoming Features (Planned)

- 🎵 **Mood-to-Music Companion:** AI-generated music based on mood
- 📖 **MindStory Generator:** Weekly emotional recap using LLM summarization
- 🕹️ **Gamified Coping Skill Builder:** Earn badges & levels for consistent habits
- 📬 **AI Letterbox:** Send thoughtful messages to your future self

---

## 💡 Inspiration

Mental health should be **accessible**, **personal**, and **empathetic**.  
MindMate was designed to **empower users to take small, meaningful steps every day** toward emotional resilience — with help from AI.

---

## 📜 License

This project is open-source under the [MIT License](LICENSE).

---

## 👤 Author

**MindMate** by [Your Name]  
*Built with 💙 for mental wellness and tech for good.*

---
