# studybuddy.py - Full AI-Powered StudyBuddy
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
    st.warning("Gemini API key missing. Notes generation disabled.")

# Warn if YouTube key missing
if "REPLACE_ME" in YOUTUBE_API_KEY:
    st.warning("YouTube API key missing. Videos won't load.")

# ---------------- STYLING ----------------
st.markdown("""
<style>
/* --- WARM LIBRARY BACKGROUND --- */
html, body, .stApp {
    background: 
        linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.7)),
        url('https://images.unsplash.com/photo-1524995997946-a1c2e315a42f') no-repeat center center fixed;
    background-size: cover;
    color: #ffffff;
}

/* --- CLEAN CENTERED HEADING --- */
.heading {
    text-align: center;
    font-size: 3.2em;
    font-weight: 700;
    color: white;
    margin: 20px 0;
    padding: 0;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.8);
    font-family: 'Georgia', 'Times New Roman', serif;
    letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HELPERS ----------------
def safe_get(dct, *path, default=None):
    cur = dct
    for key in path:
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            return default
    return cur

def get_youtube_videos(query: str, max_results: int = 3):
    if "REPLACE_ME" in YOUTUBE_API_KEY:
        st.error("YouTube API key missing.")
        return []
    try:
        url = (
            "https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&type=video&maxResults={max_results}"
            f"&q={requests.utils.quote(query)}&key={YOUTUBE_API_KEY}"
        )
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        videos = []
        for item in data.get("items", []):
            vid = safe_get(item, "id", "videoId")
            title = safe_get(item, "snippet", "title", default="(No Title)")
            if not vid:
                continue
            thumb = safe_get(item, "snippet", "thumbnails", "high", "url") or f"https://img.youtube.com/vi/{vid}/0.jpg"
            videos.append({
                "title": title,
                "url": f"https://www.youtube.com/watch?v={vid}",
                "thumb": thumb
            })
        return videos
    except Exception as e:
        st.error(f"YouTube error: {e}")
        return []

def generate_ai_notes(topic: str, video_title: str | None = None):
    if "REPLACE_ME" in GEMINI_API_KEY:
        return "Gemini API key missing. Cannot generate notes."
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        focus = f" based on '{video_title}'" if video_title else ""
        prompt = (
            f"Create short, beginner-friendly study notes on '{topic}'{focus}.\n"
            "- Use ## Headings (3–5)\n"
            "- Bullet points with tiny examples\n"
            "- Max 250 words\n"
            "- End with 3 practice questions (as '❓ Q1:')\n"
            "- Use simple language."
        )
        resp = model.generate_content(prompt)
        return getattr(resp, "text", "No notes generated.")
    except Exception as e:
        return f"Error: {e}"

# ---------------- PDF EXPORT HELPER ----------------
def create_pdf_favorites():
    try:
        from fpdf import FPDF
    except ImportError:
        st.error("Install fpdf: `pip install fpdf`")
        return None

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "My StudyBuddy Favorites", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", "", 12)
    if st.session_state.favorites:
        for r in st.session_state.favorites:
            title = r['title'].replace('•', '').replace('●', '').replace('▶', '▶').strip()
            title = title.encode('latin1', 'ignore').decode('latin1')

            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, f"- {title}", ln=True)

            pdf.set_font("Arial", "I", 11)
            pdf.set_text_color(26, 188, 156)
            type_text = r['type'].encode('latin1', 'ignore').decode('latin1')
            source_text = r['source'].title().encode('latin1', 'ignore').decode('latin1')
            pdf.cell(0, 6, f"Type: {type_text} | Source: {source_text}", ln=True)

            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", "U", 10)
            url = r['url'].encode('latin1', 'ignore').decode('latin1')
            pdf.cell(0, 6, url, ln=True)
            pdf.ln(4)
    else:
        pdf.cell(0, 10, "No favorites yet.", ln=True)

    return pdf.output(dest="S")

# ---------------- LOAD RESOURCES & AI MODEL ----------------
@st.cache_resource
def load_resources_and_model():
    try:
        df = pd.read_csv("resources.csv")
        df.columns = [c.strip().lower() for c in df.columns]
        required = {"topic", "type", "title", "link"}
        if not required.issubset(df.columns):
            st.error(f"CSV missing columns. Required: {required}")
            return None, None, None
        topics = df["topic"].dropna().tolist()
    except FileNotFoundError:
        st.warning("⚠️ `resources.csv` not found.")
        return None, None, None
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return None, None, None

    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        topic_embeddings = model.encode(topics)
        return df, model, topic_embeddings
    except Exception as e:
        st.error("Failed to load AI model. Run: pip install sentence-transformers")
        return df, None, None

df, embedding_model, topic_embeddings = load_resources_and_model()

# Initialize session state
if "topic_input" not in st.session_state:
    st.session_state.topic_input = ""

if "recs" not in st.session_state:
    st.session_state.recs = []

if "search_history" not in st.session_state:
    st.session_state.search_history = []

if "favorites" not in st.session_state:
    st.session_state.favorites = []

# ---------------- UI ----------------
st.markdown('<div class="heading">StudyBuddy</div>', unsafe_allow_html=True)

with st.form("query"):
   topic = st.text_input(
    "Search Topic",
    placeholder="e.g., Python functions...",
    value=st.session_state.topic_input,
    label_visibility="collapsed"
)
   c1, c2 = st.columns([2, 1])
   with c1:
        go = st.form_submit_button("🎯 Recommend", type="primary")
   with c2:
        clear = st.form_submit_button("🧹 Clear")

if clear:
    st.session_state.recs = []
    st.session_state.topic_input = ""
    for key in list(st.session_state.keys()):
        if key.startswith("notes_"):
            del st.session_state[key]
    st.rerun()

if go and topic.strip():
    st.session_state.topic_input = topic.strip()

# Add to history
topic_val = st.session_state.get("topic_input", "").strip()
if topic_val and topic_val not in st.session_state.search_history:
    st.session_state.search_history.append(topic_val)
    st.session_state.search_history = st.session_state.search_history[-5:]

# ---------------- SEARCH LOGIC (AI Semantic Match) ----------------
if go and topic_val and df is not None:
    recs = []

    # AI: Semantic similarity
    if embedding_model is not None and topic_embeddings is not None:
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
            user_embedding = embedding_model.encode([topic_val])
            similarities = cosine_similarity(user_embedding, np.array(topic_embeddings))
            best_idx = similarities.argmax()
            best_score = similarities[0][best_idx]

            if best_score > 0.6:
                row = df.iloc[best_idx]
                recs.append({
                    "source": "csv",
                    "type": str(row["type"]).title(),
                    "title": str(row["title"]),
                    "url": str(row["link"])
                })
        except Exception as e:
            st.error(f"AI matching error: {e}")
    else:
        # Fallback: Fuzzy match
        for _, row in df.iterrows():
            try:
                row_topic = str(row.get("topic", "")).lower()
                if fuzz.partial_ratio(topic_val.lower(), row_topic) >= 70:
                    recs.append({
                        "source": "csv",
                        "type": str(row.get("type", "Resource")).title(),
                        "title": str(row.get("title", "(No Title)")),
                        "url": str(row.get("link", ""))
                    })
            except:
                continue

    # YouTube videos
    yt = get_youtube_videos(topic_val, max_results=3)
    for v in yt:
        recs.append({
            "source": "youtube",
            "type": "YouTube",
            "title": v["title"],
            "url": v["url"],
            "thumb": v["thumb"]
        })

    st.session_state.recs = recs

# ---------------- DISPLAY ----------------
if st.session_state.recs:
    tabs = st.tabs(["📚 Resources", "🎬 YouTube", "📝 AI Notes", "⭐ Favorites", "🕰️ History"])

    # --- TAB 1: RESOURCES ---
    with tabs[0]:
        st.subheader("✅ Recommended Resources")
        csv_items = [r for r in st.session_state.recs if r["source"] == "csv"]
        icons = {"pdf": "📄", "article": "✍️", "quiz": "❓", "book": "📘", "tutorial": "🛠️", "website": "🌐"}
        if csv_items:
            for r in csv_items:
                icon = icons.get(r["type"].lower(), "📎")
                col1, col2 = st.columns([9, 1])
                with col1:
                    st.markdown(f"{icon} **{r['type']}**: [{r['title']}]({r['url']})")
                with col2:
                    if st.button("❤️", key=f"fav_{r['url']}", help="Add to favorites"):
                        if r not in st.session_state.favorites:
                            st.session_state.favorites.append(r)
                            st.success("Saved!", icon="✅")
        else:
            st.info("No matching resources found.")

    # --- TAB 2: YOUTUBE ---
    with tabs[1]:
        st.subheader("🎥 YouTube Videos")
        yt_items = [r for r in st.session_state.recs if r["source"] == "youtube"]
        if yt_items:
            for r in yt_items:
                col1, col2 = st.columns([9, 1])
                with col1:
                    st.markdown("<div style='text-align: center; margin: 20px 0;'>", unsafe_allow_html=True)
                    st.image(r["thumb"], width=320)
                    st.markdown(
                        f"<a href='{r['url']}' target='_blank' style='color: #c1f7c4; font-weight: 600; font-size: 1.1em;'>▶️ {r['title']}</a>",
                        unsafe_allow_html=True
                    )
                    st.markdown("</div>", unsafe_allow_html=True)
                with col2:
                    if st.button("❤️", key=f"yt_{r['url']}", help="Add to favorites"):
                        if r not in st.session_state.favorites:
                            st.session_state.favorites.append(r)
                            st.success("Video saved!", icon="✅")
        else:
            st.info("No YouTube videos found.")

    # --- TAB 3: AI NOTES ---
    with tabs[2]:
        st.subheader("📝 AI-Generated Notes")
        notes_key = f"notes_{topic_val}"
        if notes_key not in st.session_state:
            yt_items = [r for r in st.session_state.recs if r["source"] == "youtube"]
            video_title = yt_items[0]["title"] if yt_items else None
            st.session_state[notes_key] = generate_ai_notes(topic_val, video_title)

        st.markdown(f"<div class='notes'>{st.session_state[notes_key]}</div>", unsafe_allow_html=True)

        st.download_button(
            "📥 Download Notes",
            st.session_state[notes_key],
            file_name=f"{topic_val.replace(' ', '_')}_study_notes.txt",
            mime="text/plain"
        )

    # --- TAB 4: FAVORITES ---
    with tabs[3]:
        st.subheader("⭐ Your Favorites")
        if st.session_state.favorites:
            try:
                pdf_data = create_pdf_favorites()
                if pdf_data:
                    st.download_button(
                        "📄 Export Favorites as PDF",
                        pdf_data,
                        file_name="my_study_favorites.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.info("PDF export not available. Install `fpdf`.")
            except Exception as e:
                st.error(f"PDF generation failed: {e}")

            st.markdown("<br>", unsafe_allow_html=True)
            for r in st.session_state.favorites:
                icon = "▶️" if r["source"] == "youtube" else "📎"
                st.markdown(f"{icon} [{r['title']}]({r['url']}) <sup style='color:#ccc;'>{r['type']}</sup>", unsafe_allow_html=True)
            if st.button("🗑️ Clear All Favorites"):
                st.session_state.favorites = []
                st.rerun()
        else:
            st.info("No favorites yet.")

    # --- TAB 5: HISTORY ---
    with tabs[4]:
        st.subheader("🕰️ Recent Searches")
        if st.session_state.search_history:
            for t in reversed(st.session_state.search_history):
                if st.button(t, key=f"hist_{t}"):
                    st.session_state.topic_input = t
                    st.session_state.recs = []
                    st.rerun()
            if st.button("🗑️ Clear History"):
                st.session_state.search_history = []
                st.rerun()
        else:
            st.info("No recent searches.")

else:
    if 'go' in locals() and go:
        st.info("No results. Try a broader topic like 'Python basics' or 'SQL joins'.")
