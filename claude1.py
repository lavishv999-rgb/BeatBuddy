# ==============================================
# 🎧 BeatBuddy – Mood-Based Music Recommender (app.py)
# ==============================================
# Enhanced version with language selection feature
# Run:
#    pip install streamlit spotipy pandas
#    streamlit run app.py
# ==============================================

import os
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time

# ------------------------------------------------
# 🔐 STEP 1: SPOTIFY CREDENTIALS
# ------------------------------------------------
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "2e0be09b2c5e4f4aaa2965fbbe3f08e1")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "16d3a882fdf84aefac24c0e93fff5e93")

# ------------------------------------------------
# 🎨 STEP 2: SETUP STREAMLIT PAGE + ENHANCED STYLES
# ------------------------------------------------
st.set_page_config(
    page_title="BeatBuddy – AI Music Recommender 🎵", 
    page_icon="🎧", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
    <style>
    /* Modern gradient background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Header styling */
    .app-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        text-align: center;
    }
    
    .app-header h1 {
        margin: 0;
        font-size: 3rem;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Card styling */
    .card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.2);
    }
    
    /* Mood badge */
    .mood-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 25px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 700;
        font-size: 1.1rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    
    /* Language badge */
    .lang-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        font-weight: 600;
        font-size: 0.9rem;
        margin-left: 8px;
        box-shadow: 0 3px 8px rgba(0,0,0,0.2);
    }
    
    /* Chat bubbles */
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 12px;
        max-height: 400px;
        overflow-y: auto;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 15px;
    }
    
    .user-bubble {
        align-self: flex-end;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 18px;
        border-radius: 20px 20px 5px 20px;
        max-width: 70%;
        box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
        font-weight: 500;
    }
    
    .bot-bubble {
        align-self: flex-start;
        background: #ffffff;
        color: #1e3c72;
        padding: 12px 18px;
        border-radius: 20px 20px 20px 5px;
        max-width: 70%;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    /* Track card styling */
    .track-card {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        display: flex;
        gap: 1rem;
        align-items: center;
        transition: all 0.3s ease;
    }
    
    .track-card:hover {
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        transform: scale(1.02);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Quick mood buttons */
    .mood-btn {
        background: white;
        border: 2px solid #667eea;
        color: #667eea;
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .mood-btn:hover {
        background: #667eea;
        color: white;
    }
    
    /* Small text */
    .small-muted {
        color: #6c757d;
        font-size: 0.9rem;
    }
    
    /* Success/Error messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 10px;
        padding: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------
# 🎵 App Header
# ------------------------------------------------
st.markdown(
    """
    <div class="app-header">
      <h1>🎶 BeatBuddy</h1>
      <p style="font-size: 1.2rem; margin-top: 0.5rem;">AI-Powered Mood-Based Music Recommender</p>
      <p style="font-size: 0.9rem; opacity: 0.9;">Tell me how you feel, and I'll find the perfect soundtrack for your mood!</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------
# Defaults
# ------------------------------------------------
DEFAULT_LANGUAGE = "English"
DEFAULT_LATEST = True
DEFAULT_NUM_RESULTS = 10
DEFAULT_MOOD = "chill"

# ------------------------------------------------
# Spotify client helper
# ------------------------------------------------
@st.cache_resource
def get_sp_client():
    if not CLIENT_ID or not CLIENT_SECRET:
        st.error("⚠️ Missing Spotify credentials. Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET")
        return None
    
    try:
        auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        sp = spotipy.Spotify(auth_manager=auth_manager)
        return sp
    except Exception as e:
        st.error(f"❌ Spotify authentication error: {e}")
        return None

# ------------------------------------------------
# Fetch songs from Spotify
# ------------------------------------------------
def fetch_songs(mood, language, latest, limit=10):
    sp = get_sp_client()
    if sp is None:
        return pd.DataFrame()
    
    query = f"{mood} {language} song"
    if latest:
        query += " year:2022-2025"
    
    try:
        results = sp.search(q=query, type="track", limit=limit, market="IN")
        tracks = []
        for item in results.get("tracks", {}).get("items", []):
            album = item.get("album", {})
            images = album.get("images") or []
            track = {
                "title": item.get("name"),
                "artist": (item.get("artists") or [{}])[0].get("name"),
                "album": album.get("name"),
                "release_date": album.get("release_date"),
                "url": item.get("external_urls", {}).get("spotify"),
                "image": images[0].get("url") if images else None,
                "preview_url": item.get("preview_url")
            }
            tracks.append(track)
        return pd.DataFrame(tracks)
    except Exception as e:
        st.error(f"❌ Error fetching tracks: {e}")
        return pd.DataFrame()

# ------------------------------------------------
# Enhanced mood detector with better accuracy
# ------------------------------------------------
def detect_mood_from_text(text: str) -> str:
    if not text or not text.strip():
        return DEFAULT_MOOD
    
    t = text.lower()
    
    # Emoji to mood mapping
    emoji_map = {
        "😊": "happy", "🙂": "happy", "😄": "happy", "😃": "happy", "😂": "happy",
        "😍": "romantic", "❤️": "romantic", "💖": "romantic", "💕": "romantic",
        "😢": "sad", "😭": "sad", "😞": "sad", "💔": "sad",
        "🎉": "party", "🥳": "party", "🍾": "party",
        "🎶": "chill", "🎵": "chill", "😌": "chill",
        "🔥": "energetic", "⚡": "energetic", "💪": "energetic"
    }
    
    # Enhanced keyword mapping
    mood_keywords = {
        "happy": ["happy", "joy", "joyful", "smile", "great", "awesome", "wonderful", "amazing", 
                  "blessed", "cheerful", "excited", "fantastic", "good", "glad", "pleased"],
        "sad": ["sad", "tears", "cry", "lonely", "broken", "hurt", "miss", "pain", "sorrow",
                "depressed", "down", "blue", "heartbroken", "grief", "melancholy"],
        "romantic": ["love", "romance", "romantic", "heart", "darling", "baby", "sweetheart",
                     "forever", "kiss", "beloved", "affection", "passion", "crush"],
        "energetic": ["dance", "party", "pump", "energy", "workout", "gym", "run", "active",
                      "motivated", "powerful", "strong", "intense", "hype", "beast mode"],
        "chill": ["chill", "calm", "relax", "peaceful", "smooth", "easy", "mellow", "laid back",
                  "tranquil", "serene", "comfortable", "cozy"],
        "party": ["party", "club", "celebration", "night out", "shots", "crowd", "festival",
                  "rave", "dance floor", "turn up", "lit"]
    }
    
    scores = {k: 0 for k in mood_keywords}
    
    # Check emojis
    for emoji, mood in emoji_map.items():
        if emoji in text:
            scores[mood] += 3
    
    # Check keywords with context
    for mood, keywords in mood_keywords.items():
        for keyword in keywords:
            if keyword in t:
                # Check for negation
                negations = ["not ", "never ", "no ", "don't ", "can't ", "won't "]
                is_negated = any(
                    neg in t and 
                    t.find(neg) < t.find(keyword) and 
                    t.find(keyword) - t.find(neg) < 15 
                    for neg in negations
                )
                scores[mood] += -2 if is_negated else 2
    
    # If no clear mood detected, use sentiment analysis
    if all(score == 0 for score in scores.values()):
        if any(word in t for word in ["!", "yay", "yeah", "awesome", "great"]):
            return "happy"
        elif any(word in t for word in ["tired", "bored", "whatever"]):
            return "chill"
        return DEFAULT_MOOD
    
    # Return mood with highest score
    best_mood = max(scores.items(), key=lambda x: x[1])[0]
    return best_mood

# ------------------------------------------------
# Detect language from text
# ------------------------------------------------
def detect_language_from_text(text: str) -> str:
    if not text:
        return None
    
    t = text.lower()
    
    # Language keywords
    lang_keywords = {
        "english": ["english", "eng", "angrezi"],
        "hindi": ["hindi", "hin", "hindustani"],
        "punjabi": ["punjabi", "panjabi", "punjab"]
    }
    
    for lang, keywords in lang_keywords.items():
        if any(keyword in t for keyword in keywords):
            return lang.title()
    
    return None

# ------------------------------------------------
# User Management
# ------------------------------------------------
def init_user_store():
    if "users" not in st.session_state:
        st.session_state["users"] = {"demo": "demo"}
    if "saved_tracks" not in st.session_state:
        st.session_state["saved_tracks"] = {}
    if "mood_history" not in st.session_state:
        st.session_state["mood_history"] = {}
    if "user_preferences" not in st.session_state:
        st.session_state["user_preferences"] = {}

def register_user(username: str, password: str) -> bool:
    init_user_store()
    if not username or not password or len(password) < 4:
        return False
    if username in st.session_state["users"]:
        return False
    st.session_state["users"][username] = password
    st.session_state["saved_tracks"][username] = []
    st.session_state["mood_history"][username] = []
    st.session_state["user_preferences"][username] = {"language": None}
    return True

def login_user(username: str, password: str) -> bool:
    init_user_store()
    if st.session_state["users"].get(username) == password:
        st.session_state["user"] = username
        if username not in st.session_state["saved_tracks"]:
            st.session_state["saved_tracks"][username] = []
        if username not in st.session_state["mood_history"]:
            st.session_state["mood_history"][username] = []
        if username not in st.session_state["user_preferences"]:
            st.session_state["user_preferences"][username] = {"language": None}
        return True
    return False

def logout_user():
    if "user" in st.session_state:
        del st.session_state["user"]
    if "current_view" in st.session_state:
        del st.session_state["current_view"]

init_user_store()

# ------------------------------------------------
# Initialize session state for chatbot
# ------------------------------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"from": "bot", "text": "👋 Hey there! I'm BeatBuddy, your personal AI music assistant. How are you feeling today?"}
    ]

if "current_view" not in st.session_state:
    st.session_state["current_view"] = "chat"

if "last_mood" not in st.session_state:
    st.session_state["last_mood"] = DEFAULT_MOOD

if "recommendations" not in st.session_state:
    st.session_state["recommendations"] = None

if "awaiting_language" not in st.session_state:
    st.session_state["awaiting_language"] = False

if "pending_mood" not in st.session_state:
    st.session_state["pending_mood"] = None

# ------------------------------------------------
# Login/Register UI
# ------------------------------------------------
if not st.session_state.get("user"):
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("🔓 Login")
        login_username = st.text_input("Username", key="login_user", placeholder="Enter username")
        login_password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter password")
        
        if st.button("Login", use_container_width=True):
            if login_user(login_username, login_password):
                st.success("✅ Login successful!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Try demo/demo")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("📝 Register")
        reg_username = st.text_input("Username", key="reg_user", placeholder="Choose username")
        reg_password = st.text_input("Password", type="password", key="reg_pass", placeholder="Choose password (min 4 chars)")
        
        if st.button("Register", use_container_width=True):
            if register_user(reg_username, reg_password):
                st.success("✅ Registration successful! You can now login.")
            else:
                st.error("❌ Registration failed. Username may already exist or password too short.")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    # ------------------------------------------------
    # Logged-in User UI
    # ------------------------------------------------
    user = st.session_state.get("user")
    
    # Top navigation
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        st.markdown(f"<div style='padding:10px; background:white; border-radius:10px; box-shadow:0 2px 10px rgba(0,0,0,0.1);'>👤 Welcome back, <strong>{user}</strong>!</div>", unsafe_allow_html=True)
    with col2:
        if st.button("💬 Chat", use_container_width=True):
            st.session_state["current_view"] = "chat"
            st.rerun()
    with col3:
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state["current_view"] = "dashboard"
            st.rerun()
    with col4:
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ------------------------------------------------
    # CHAT VIEW
    # ------------------------------------------------
    if st.session_state.get("current_view") == "chat":
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("💬 Chat with BeatBuddy")
            
            # Chat messages display
            st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
            for msg in st.session_state["messages"]:
                if msg["from"] == "user":
                    st.markdown(f"<div class='user-bubble'>{msg['text']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='bot-bubble'>{msg['text']}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Chat input
            user_input = st.text_input("💭 Type your message...", key="chat_input", placeholder="Tell me how you're feeling...")

            # Persistent language selector (Auto asks the bot; choosing a language uses it immediately)
            lang_options = ["Auto (ask me)", "English", "Hindi", "Punjabi"]
            # Default to user's saved preference if available
            pref_lang = st.session_state.get("user_preferences", {}).get(user, {}).get("language") if user else None
            default_index = 0
            if pref_lang in lang_options:
                default_index = lang_options.index(pref_lang)
            language_choice = st.selectbox("Preferred language for recommendations:", lang_options, index=default_index, key="ui_lang_choice")

            col_send, col_recommend = st.columns([1, 1])
            with col_send:
                send_btn = st.button("Send 📤", use_container_width=True)
            with col_recommend:
                quick_recommend = st.button("🎵 Get Recommendations", use_container_width=True)
            
            if send_btn and user_input:
                # Add user message
                st.session_state["messages"].append({"from": "user", "text": user_input})

                # If the user has chosen a specific language in the selector, use it immediately
                chosen_lang = None
                if language_choice and language_choice != "Auto (ask me)":
                    chosen_lang = language_choice

                # Check if awaiting language selection (older flow) or if user chose Auto
                if st.session_state.get("awaiting_language") and not chosen_lang:
                    detected_lang = detect_language_from_text(user_input)

                    if detected_lang:
                        # Save language preference
                        st.session_state["user_preferences"][user]["language"] = detected_lang
                        st.session_state["awaiting_language"] = False

                        # Get pending mood
                        mood = st.session_state.get("pending_mood", DEFAULT_MOOD)

                        # Add bot response
                        st.session_state["messages"].append({
                            "from": "bot", 
                            "text": f"Perfect! Getting {mood} {detected_lang} songs for you! 🎵"
                        })

                        # Fetch recommendations
                        with st.spinner("Loading..."):
                            recs = fetch_songs(mood, detected_lang, DEFAULT_LATEST, DEFAULT_NUM_RESULTS)
                            st.session_state["recommendations"] = recs
                            st.session_state["recommendations_mood"] = mood
                            st.session_state["recommendations_language"] = detected_lang

                        if not recs.empty:
                            st.session_state["messages"].append({
                                "from": "bot", 
                                "text": f"✨ Found {len(recs)} amazing {mood} {detected_lang} tracks! Check the right panel!"
                            })
                        else:
                            st.session_state["messages"].append({
                                "from": "bot", 
                                "text": "😕 Sorry, couldn't find songs. Try a different mood or language!"
                            })

                        st.session_state["pending_mood"] = None
                    else:
                        st.session_state["messages"].append({
                            "from": "bot", 
                            "text": "I didn't catch that! Please choose: English, Hindi, or Punjabi?"
                        })

                    st.rerun()
                else:
                    # If user selected a language via selector, use it; otherwise run the old flow
                    if chosen_lang:
                        # Detect mood
                        detected_mood = detect_mood_from_text(user_input)
                        st.session_state["last_mood"] = detected_mood

                        # Save to mood history
                        if user in st.session_state["mood_history"]:
                            st.session_state["mood_history"][user].append({
                                "mood": detected_mood,
                                "text": user_input,
                                "timestamp": time.time()
                            })

                        # Directly fetch recommendations using chosen language
                        st.session_state["messages"].append({"from": "bot", "text": f"Searching {detected_mood} {chosen_lang} songs for you... 🎵"})
                        with st.spinner("Loading..."):
                            recs = fetch_songs(detected_mood, chosen_lang, DEFAULT_LATEST, DEFAULT_NUM_RESULTS)
                            st.session_state["recommendations"] = recs
                            st.session_state["recommendations_mood"] = detected_mood
                            st.session_state["recommendations_language"] = chosen_lang

                        if not recs.empty:
                            st.session_state["messages"].append({"from": "bot", "text": f"✨ Found {len(recs)} {detected_mood} {chosen_lang} tracks! Check the right panel."})
                        else:
                            st.session_state["messages"].append({"from": "bot", "text": f"😕 Couldn't find {detected_mood} tracks in {chosen_lang}. Try changing the language or mood."})
                        st.rerun()

                    # Old flow: ask for language explicitly
                    detected_mood = detect_mood_from_text(user_input)
                    st.session_state["last_mood"] = detected_mood
                    
                    # Save to mood history
                    if user in st.session_state["mood_history"]:
                        st.session_state["mood_history"][user].append({
                            "mood": detected_mood,
                            "text": user_input,
                            "timestamp": time.time()
                        })
                    
                    # Ask for language preference
                    st.session_state["awaiting_language"] = True
                    st.session_state["pending_mood"] = detected_mood
                    
                    bot_response = f"I sense you're feeling **{detected_mood}** 🎭! Which language would you like? 🌍\n\n📌 English • Hindi • Punjabi"
                    st.session_state["messages"].append({"from": "bot", "text": bot_response})
                    
                    st.rerun()
            
            if quick_recommend:
                mood = st.session_state.get("last_mood", DEFAULT_MOOD)
                # If user already chose a language in selector, use it
                if language_choice and language_choice != "Auto (ask me)":
                    lang = language_choice
                    st.session_state["messages"].append({"from": "bot", "text": f"Searching {mood} {lang} songs for you... 🎵"})
                    with st.spinner("Loading..."):
                        recs = fetch_songs(mood, lang, DEFAULT_LATEST, DEFAULT_NUM_RESULTS)
                        st.session_state["recommendations"] = recs
                        st.session_state["recommendations_mood"] = mood
                        st.session_state["recommendations_language"] = lang
                    if not recs.empty:
                        st.session_state["messages"].append({"from": "bot", "text": f"✨ Found {len(recs)} {mood} {lang} tracks! Check the right panel."})
                    else:
                        st.session_state["messages"].append({"from": "bot", "text": f"😕 Couldn't find {mood} tracks in {lang}. Try another language."})
                    st.rerun()
                else:
                    st.session_state["pending_mood"] = mood
                    st.session_state["awaiting_language"] = True
                    st.session_state["messages"].append({
                        "from": "bot", 
                        "text": f"🎵 Great! I'll find {mood} songs for you. Which language? 🌍\n\n📌 English • Hindi • Punjabi"
                    })
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Quick mood buttons
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("🎭 Quick Mood Selection")
            moods = ["happy", "sad", "romantic", "energetic", "chill", "party"]
            cols = st.columns(3)
            for i, mood in enumerate(moods):
                with cols[i % 3]:
                    if st.button(f"{mood.title()} {['😊','😢','😍','⚡','😌','🎉'][i]}", key=f"mood_{mood}", use_container_width=True):
                        st.session_state["last_mood"] = mood
                        st.session_state["pending_mood"] = mood
                        st.session_state["awaiting_language"] = True
                        
                        st.session_state["messages"].append({"from": "user", "text": f"I'm feeling {mood}"})
                        st.session_state["messages"].append({
                            "from": "bot", 
                            "text": f"Perfect! Which language would you prefer? 🌍\n\n📌 English • Hindi • Punjabi"
                        })
                        
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Quick language selection (when awaiting)
            if st.session_state.get("awaiting_language"):
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.subheader("🌍 Select Language")
                languages = ["English", "Hindi", "Punjabi"]
                lang_emojis = ["🇬🇧", "🇮🇳", "🇮🇳"]
                
                cols = st.columns(3)
                for i, (lang, emoji) in enumerate(zip(languages, lang_emojis)):
                    with cols[i]:
                        if st.button(f"{emoji} {lang}", key=f"lang_{lang}", use_container_width=True):
                            st.session_state["user_preferences"][user]["language"] = lang
                            st.session_state["awaiting_language"] = False
                            
                            mood = st.session_state.get("pending_mood", DEFAULT_MOOD)
                            
                            st.session_state["messages"].append({"from": "user", "text": lang})
                            st.session_state["messages"].append({
                                "from": "bot", 
                                "text": f"Awesome! Getting {mood} {lang} songs for you! 🎵"
                            })
                            
                            # Fetch recommendations
                            with st.spinner("Loading..."):
                                recs = fetch_songs(mood, lang, DEFAULT_LATEST, DEFAULT_NUM_RESULTS)
                                st.session_state["recommendations"] = recs
                                st.session_state["recommendations_mood"] = mood
                                st.session_state["recommendations_language"] = lang
                            
                            if not recs.empty:
                                st.session_state["messages"].append({
                                    "from": "bot", 
                                    "text": f"✨ Found {len(recs)} amazing {mood} {lang} tracks! Check the right panel!"
                                })
                            
                            st.session_state["pending_mood"] = None
                            st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("🎵 Music Recommendations")
            
            if st.session_state.get("recommendations") is not None and not st.session_state["recommendations"].empty:
                recs = st.session_state["recommendations"]
                mood = st.session_state.get("recommendations_mood", "your mood")
                language = st.session_state.get("recommendations_language", DEFAULT_LANGUAGE)
                
                st.markdown(
                    f"<div style='text-align:center; margin-bottom:1rem;'>"
                    f"<span class='mood-badge'>{mood.upper()}</span>"
                    f"<span class='lang-badge'>🌍 {language}</span>"
                    f"</div>", 
                    unsafe_allow_html=True
                )
                st.markdown(f"<p style='text-align:center; color:#6c757d;'>Found {len(recs)} tracks for you!</p>", unsafe_allow_html=True)
                
                for idx, row in recs.iterrows():
                    with st.container():
                        col_img, col_info = st.columns([1, 3])
                        
                        with col_img:
                            if row.get("image"):
                                st.image(row.get("image"), use_container_width=True)
                        
                        with col_info:
                            st.markdown(f"**{row.get('title')}**")
                            st.markdown(f"🎤 {row.get('artist')}")
                            st.markdown(f"💿 {row.get('album')}")
                            st.markdown(f"📅 {row.get('release_date')}")
                            
                            col_link, col_save = st.columns([1, 1])
                            with col_link:
                                if row.get("url"):
                                    st.markdown(f"[🎧 Listen]({row.get('url')})")
                            with col_save:
                                if st.button("💾 Save", key=f"save_{idx}", use_container_width=True):
                                    st.session_state["saved_tracks"][user].append({
                                        "title": row.get("title"),
                                        "artist": row.get("artist"),
                                        "album": row.get("album"),
                                        "release_date": row.get("release_date"),
                                        "url": row.get("url"),
                                        "image": row.get("image"),
                                        "language": language,
                                        "mood": mood
                                    })
                                    st.success("✅ Saved!")
                        
                        st.markdown("<hr style='margin:1rem 0;'>", unsafe_allow_html=True)
            else:
                st.info("🎵 Chat with me and I'll recommend music based on your mood!")
                st.image("https://media.giphy.com/media/3o7btPCcdNniyf0ArS/giphy.gif", use_container_width=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # ------------------------------------------------
    # DASHBOARD VIEW
    # ------------------------------------------------
    elif st.session_state.get("current_view") == "dashboard":
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("📊 Your Music Dashboard")
        
        tab1, tab2 = st.tabs(["💾 Saved Tracks", "📈 Mood History"])
        
        with tab1:
            saved = st.session_state.get("saved_tracks", {}).get(user, [])
            if not saved:
                st.info("🎵 You haven't saved any tracks yet. Start chatting to get recommendations!")
            else:
                st.success(f"You have {len(saved)} saved tracks!")
                for idx, track in enumerate(saved):
                    col_img, col_info, col_action = st.columns([1, 4, 1])
                    
                    with col_img:
                        if track.get("image"):
                            st.image(track.get("image"), width=100)
                    
                    with col_info:
                        st.markdown(f"**{track.get('title')}**")
                        st.markdown(f"🎤 {track.get('artist')} • 💿 {track.get('album')}")
                        st.markdown(f"📅 {track.get('release_date')}")
                        
                        # Display language and mood badges
                        lang = track.get("language", "Unknown")
                        mood = track.get("mood", "Unknown")
                        st.markdown(f"🌍 {lang} • 🎭 {mood}")
                        
                        if track.get("url"):
                            st.markdown(f"[🎧 Listen on Spotify]({track.get('url')})")
                    
                    with col_action:
                        if st.button("🗑️", key=f"remove_{idx}", help="Remove track"):
                            st.session_state["saved_tracks"][user].pop(idx)
                            st.rerun()
                    
                    st.markdown("<hr style='margin:0.5rem 0;'>", unsafe_allow_html=True)
        
        with tab2:
            mood_hist = st.session_state.get("mood_history", {}).get(user, [])
            if not mood_hist:
                st.info("📈 No mood history yet. Start chatting to track your moods!")
            else:
                st.success(f"You've expressed {len(mood_hist)} moods!")
                
                # Count moods
                mood_counts = {}
                for entry in mood_hist:
                    mood = entry.get("mood", "unknown")
                    mood_counts[mood] = mood_counts.get(mood, 0) + 1
                
                # Display mood distribution
                st.markdown("### 🎭 Your Mood Distribution")
                for mood, count in sorted(mood_counts.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / len(mood_hist)) * 100
                    st.markdown(f"**{mood.title()}**: {count} times ({percentage:.1f}%)")
                    st.progress(percentage / 100)
                
                st.markdown("### 📝 Recent Moods")
                for entry in reversed(mood_hist[-10:]):  # Show last 10
                    st.markdown(f"- **{entry.get('mood').title()}**: \"{entry.get('text')}\"")
        
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------
# Footer
# ------------------------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    """
    <div style='text-align:center; color:#6c757d; padding:2rem; background:white; border-radius:15px; box-shadow:0 4px 15px rgba(0,0,0,0.1);'>
        <p><strong>BeatBuddy v2.1</strong> - AI-Powered Music Recommendation System with Multi-Language Support</p>
        <p>Made with ❤️ by Code Avengers | Powered by Spotify API</p>
        <p>🎵 English • Hindi • Punjabi Songs</p>
    </div>
    """,
    unsafe_allow_html=True
)