import os
import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz
import requests
import google.generativeai as genai

# ---------------- CONFIG ----------------
st.set_page_config(page_title="StudyBuddy", page_icon="📚", layout="centered")

# Read API keys
YOUTUBE_API_KEY = st.secrets.get("YOUTUBE_API_KEY", os.getenv("YOUTUBE_API_KEY", "REPLACE_ME_YT"))
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", "REPLACE_ME_GEMINI"))

# Configure Gemini
if "REPLACE_ME" not in GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    st.warning("Gemini API key missing. Notes disabled.")

# Warn if YouTube key missing
if "REPLACE_ME" in YOUTUBE_API_KEY:
    st.warning("YouTube API key missing.")

# ---------------- UI ----------------
st.markdown("<h1 style='text-align: center; color: white;'>StudyBuddy</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #e6d5a0;'>Your AI study companion</p>", unsafe_allow_html=True)

topic = st.text_input("🔍 Enter your topic", placeholder="e.g., Python functions, OOPs")

if st.button("🎯 Recommend"):
    if not topic.strip():
        st.info("Please enter a topic.")
    else:
        # --- GET YOUTUBE VIDEOS ---
        try:
            url = (
                "https://www.googleapis.com/youtube/v3/search"
                f"?part=snippet&type=video&maxResults=3&q={requests.utils.quote(topic)}&key={YOUTUBE_API_KEY}"
            )
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            data = r.json()
            videos = []
            for item in data.get("items", []):
                vid = item["id"]["videoId"]
                title = item["snippet"]["title"]
                thumb = item["snippet"]["thumbnails"]["high"]["url"]
                videos.append({"title": title, "url": f"https://www.youtube.com/watch?v={vid}", "thumb": thumb})
        except:
            videos = []

        # --- GENERATE AI NOTES ---
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"Create 4-5 bullet points on {topic}. Simple language, tiny examples."
            response = model.generate_content(prompt)
            notes = response.text or "No notes generated."
        except:
            notes = "Gemini API error."

        # --- DISPLAY ---
        st.subheader("🎥 YouTube Videos")
        if videos:
            for v in videos:
                st.image(v["thumb"], width=320)
                st.markdown(f"[{v['title']}]({v['url']})")
        else:
            st.info("No videos found.")

        st.subheader("📝 AI Notes")
        st.markdown(f"<div style='background: rgba(0,0,0,0.3); padding: 15px; border-radius: 10px;'>{notes}</div>", unsafe_allow_html=True)