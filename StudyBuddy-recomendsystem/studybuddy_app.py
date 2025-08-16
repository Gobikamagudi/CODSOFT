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
/* --- WARM LIBRARY BACKGROUND (original) --- */
html, body, .stApp {
    background: 
        linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.7)),
        url('https://images.unsplash.com/photo-1524995997946-a1c2e315a42f') no-repeat center center fixed;
    background-size: cover;
    color: #ffffff;
}

/* --- CLASSIC BOOK-STYLE HEADING --- */
h1 {
    text-align: center;
    font-size: 4.2em;
    font-weight: 700;
    margin: 1rem auto 0.5rem;
    letter-spacing: 2px;
    color: #fff;
    text-shadow: 
        2px 2px 8px rgba(0, 0, 0, 0.9),
        0 0 10px rgba(200, 180, 120, 0.3);
    font-family: 'Georgia', 'Times New Roman', serif;
    animation: fadeInUp 1.4s ease-out;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* --- SUBTITLE STYLE --- */
.subtitle {
    text-align: center;
    font-size: 1.3em;
    color: #e6d5a0 !important;
    font-style: italic;
    margin-bottom: 1.5rem;
    font-weight: 400;
    text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.7);
}

/* --- CLEAN FONT FOR BODY --- */
body, .stMarkdown, .notes, .video-card {
    font-family: 'Segoe UI', Arial, sans-serif;
}

/* --- BUTTONS (Soft Green) --- */
.stButton>button, .stDownloadButton>button {
    background: linear-gradient(90deg, #2ecc71, #27ae60) !important;
    color: white !important;
    border-radius: 12px;
    padding: 0.6rem 1.6rem;
    font-weight: 600;
    border: none;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    transition: all 0.3s ease;
}
.stButton>button:hover, .stDownloadButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 14px rgba(0, 0, 0, 0.3);
}

/* --- VIDEO CARD --- */
.video-card {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 12px;
    padding: 14px;
    margin: 16px auto;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    max-width: 600px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    transition: all 0.3s;
}
.video-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
}
.video-card img {
    border-radius: 10px;
    width: 100%;
    height: auto;
}
.video-card a {
    color: #d1f7c4 !important;
    font-weight: 600;
    font-size: 1.1em;
}

/* --- NOTES BOX --- */
.notes {
    background: rgba(20, 20, 30, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    padding: 18px;
    margin-top: 15px;
    line-height: 1.7;
    font-size: 1.05em;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    max-height: 600px;
    overflow-y: auto;
    color: #e0ffe0;
}

/* --- TEXT STYLING --- */
h2, h3, p, label, .stMarkdown, .stTextInput label {
    color: #ffffff !important;
    text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.7);
}

/* --- INPUT FIELD --- */
.stTextInput > div > div > input {
    background: rgba(255, 255, 255, 0.1);
    color: white;
    border: 1px solid #2ecc71;
    border-radius: 10px;
    padding: 10px 15px;
}
.stTextInput > div > div > input::placeholder {
    color: #ccc;
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

def load_resources_csv():
    try:
        df = pd.read_csv("resources.csv")
        df.columns = [c.strip().lower() for c in df.columns]
        required = {"topic", "type", "title", "link"}
        if not required.issubset(df.columns):
            st.error(f"CSV missing columns. Required: {required}")
            return None
        return df
    except FileNotFoundError:
        st.warning("⚠️ `resources.csv` not found.")
        return None
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return None

# ---------------- DATA ----------------
df = load_resources_csv()

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
st.markdown("<h1>StudyBuddy</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Your calm, focused learning companion 📖</p>", unsafe_allow_html=True)

with st.form("query"):
    topic = st.text_input("🔍 Enter your topic", placeholder="e.g., Python functions, OOPs, DBMS normalization, SQL joins")
    c1, c2 = st.columns(2)
    with c1:
        go = st.form_submit_button("🎯 Recommend")
    with c2:
        clear = st.form_submit_button("🧹 Clear")

if clear:
    st.session_state.recs = []
    st.session_state.topic_input = ""
    # Clear note cache
    for key in list(st.session_state.keys()):
        if key.startswith("notes_"):
            del st.session_state[key]
    st.rerun()

# Update topic input
if go and topic.strip():
    st.session_state.topic_input = topic.strip()

# Add to history
topic_val = st.session_state.get("topic_input", "").strip()
if topic_val and topic_val not in st.session_state.search_history:
    st.session_state.search_history.append(topic_val)
    st.session_state.search_history = st.session_state.search_history[-5:]

# ---------------- SEARCH LOGIC ----------------
if go and topic_val:
    topic_q = topic_val.lower()
    recs = []

    if df is not None:
        for _, row in df.iterrows():
            try:
                row_topic = str(row.get("topic", "")).lower()
                if fuzz.partial_ratio(topic_q, row_topic) >= 70:
                    recs.append({
                        "source": "csv",
                        "type": str(row.get("type", "Resource")).title(),
                        "title": str(row.get("title", "(No Title)")),
                        "url": str(row.get("link", ""))
                    })
            except:
                continue

    yt = get_youtube_videos(topic_q, max_results=3)
    for v in yt:
        recs.append({
            "source": "youtube",
            "type": "YouTube",
            "title": v["title"],
            "url": v["url"],
            "thumb": v["thumb"]
        })

    st.session_state.recs = recs

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
            # Clean title: remove •, emojis, and non-latin chars
            title = r['title'].replace('•', '').replace('●', '').replace('▶', '▶').strip()
            title = title.encode('latin1', 'ignore').decode('latin1')  # Remove unsupported chars

            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, f"- {title}", ln=True)  # Use "-" instead of "•"

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
                            st.success("Saved!")
        else:
            st.info("No matching resources found in your library.")

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
                        f"<a href='{r['url']}' target='_blank' style='color: #c1f7d5; font-weight: 600; font-size: 1.1em;'>▶️ {r['title']}</a>",
                        unsafe_allow_html=True
                    )
                    st.markdown("</div>", unsafe_allow_html=True)
                with col2:
                    if st.button("❤️", key=f"yt_{r['url']}", help="Add to favorites"):
                        if r not in st.session_state.favorites:
                            st.session_state.favorites.append(r)
                            st.success("Video saved!")
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
        st.subheader("⭐ Your Favorite Resources")
        if st.session_state.favorites:
            st.download_button(
                "📄 Export Favorites as PDF",
                create_pdf_favorites(),
                file_name="my_study_favorites.pdf",
                mime="application/pdf"
            )
            st.markdown("<br>", unsafe_allow_html=True)
            for r in st.session_state.favorites:
                icon = "▶️" if r["source"] == "youtube" else "📎"
                st.markdown(f"{icon} [{r['title']}]({r['url']}) <sup style='color:#ccc;'>{r['type']}</sup>", unsafe_allow_html=True)
            if st.button("🗑️ Clear All Favorites"):
                st.session_state.favorites = []
                st.rerun()
        else:
            st.info("No favorites yet. Click ❤️ to save resources.")

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
