# StudyBuddy 📚

An AI-powered study resource recommender built for **CODSOFT Internship**.

Find YouTube videos, AI-generated notes, and curated resources in seconds — all in one place.

![StudyBuddy Screenshot](https://i.imgur.com/your-screenshot-link.jpg)  
*(Replace with your app screenshot)*

---

## 🔍 Features

- ✅ **Smart Topic Search** – Enter any topic (e.g., "Python functions")
- 🎥 **YouTube Video Recommendations**
- 🤖 **AI-Generated Notes** using Google Gemini
- ❤️ **Save Favorite Resources**
- 📥 Export favorites as TXT
- 📚 Clean, library-themed UI

---

## 🔐 How to Run (For Reviewer)

Since this app uses **API keys**, you need to set up secrets:

### 1. Get Free API Keys
- **YouTube API Key**: [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
- **Gemini API Key**: [Google AI Studio](https://aistudio.google.com/app/apikey)

### 2. Deploy on Streamlit Cloud
1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Connect your GitHub
3. Deploy this repo: `Gobikamagudi/CODSOFT`
4. Set **Main file path**: `StudyBuddy-recomendsystem/studybuddy_app.py`

### 3. Add Secrets
In **Settings → Secrets**, add:
```toml
YOUTUBE_API_KEY = "your_youtube_key_here"
GEMINI_API_KEY = "your_gemini_key_here"
