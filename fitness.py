import os
import sqlite3
import hashlib
import streamlit as st
import google.generativeai as genai
import pycountry
from datetime import datetime

# ======================================================================
# 1. ENTERPRISE COG DATABASE & SECURE IDENTITY VAULT
# ======================================================================
def init_db():
    conn = sqlite3.connect("fitness_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            username TEXT PRIMARY KEY,
            password_hash TEXT,
            country TEXT,
            tier TEXT,
            workout_streak INTEGER,
            scripture_streak INTEGER,
            m1 INTEGER, m2 INTEGER, m3 INTEGER, m4 INTEGER, m5 INTEGER,
            capital_received REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workout_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            date_logged TEXT,
            workout_title TEXT,
            duration_mins INTEGER,
            calories_burned INTEGER,
            status_tag TEXT,
            notes TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            category TEXT,
            message TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, country):
    conn = sqlite3.connect("fitness_data.db")
    cursor = conn.cursor()
    try:
        p_hash = hash_password(password)
        cursor.execute("INSERT INTO accounts VALUES (?, ?, ?, 'Basic Plan (Free Core)', 27, 14, 0, 0, 0, 0, 0, 0.0)", (username, p_hash, country))
        cursor.execute("INSERT INTO workout_logs (username, date_logged, workout_title, duration_mins, calories_burned, status_tag, notes) VALUES (?, 'Saturday, June 27', '🔥 Chest & Triceps Blast', 78, 612, '✅ Completed', 'Hit a new baseline volume threshold.')", (username,))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def verify_user(username, password):
    conn = sqlite3.connect("fitness_data.db")
    cursor = conn.cursor()
    p_hash = hash_password(password)
    cursor.execute("SELECT username, tier, country FROM accounts WHERE username=? AND password_hash=?", (username, p_hash))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_data(username):
    conn = sqlite3.connect("fitness_data.db")
    cursor = conn.cursor()
    clean_username = username if isinstance(username, tuple) else username
    cursor.execute("SELECT workout_streak, scripture_streak, m1, m2, m3, m4, m5, tier, country, capital_received FROM accounts WHERE username=?", (clean_username,))
    data = cursor.fetchone()
    conn.close()
    return data

def get_user_logs(username):
    conn = sqlite3.connect("fitness_data.db")
    cursor = conn.cursor()
    clean_username = username if isinstance(username, tuple) else username
    cursor.execute("SELECT date_logged, workout_title, duration_mins, calories_burned, status_tag, notes FROM workout_logs WHERE username=? ORDER BY id DESC", (clean_username,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_workout_log(username, date, title, duration, calories, status, notes):
    conn = sqlite3.connect("fitness_data.db")
    cursor = conn.cursor()
    clean_username = username if isinstance(username, tuple) else username
    cursor.execute("INSERT INTO workout_logs (username, date_logged, workout_title, duration_mins, calories_burned, status_tag, notes) VALUES (?, ?, ?, ?, ?, ?, ?)", (clean_username, date, title, duration, calories, status, notes))
    conn.commit()
    conn.close()

def add_support_ticket(username, category, message):
    conn = sqlite3.connect("fitness_data.db")
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    clean_username = username if isinstance(username, tuple) else username
    cursor.execute("INSERT INTO support_tickets (username, category, message, timestamp) VALUES (?, ?, ?, ?)", (clean_username, category, message, now_str))
    conn.commit()
    conn.close()

def get_all_support_tickets():
    conn = sqlite3.connect("fitness_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, category, message, timestamp FROM support_tickets ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_user_db(username, w_streak, s_streak, m1, m2, m3, m4, m5, tier, capital):
    conn = sqlite3.connect("fitness_data.db")
    cursor = conn.cursor()
    clean_username = username if isinstance(username, tuple) else username
    cursor.execute("""
        UPDATE accounts 
        SET workout_streak=?, scripture_streak=?, m1=?, m2=?, m3=?, m4=?, m5=?, tier=?, capital_received=?
        WHERE username=?
    """, (w_streak, s_streak, int(m1), int(m2), int(m3), int(m4), int(m5), tier, capital, clean_username))
    conn.commit()
    conn.close()

def delete_user_account(username):
    conn = sqlite3.connect("fitness_data.db")
    cursor = conn.cursor()
    clean_username = username if isinstance(username, tuple) else username
    cursor.execute("DELETE FROM accounts WHERE username=?", (clean_username,))
    cursor.execute("DELETE FROM workout_logs WHERE username=?", (clean_username,))
    conn.commit()
    conn.close()

init_db()

# ======================================================================
# 2. AUTOMATED CIRCADIAN THEME ENGINE & VISUAL LUXURY CSS
# ======================================================================
GOOGLE_API_KEY = "AQ.Ab8RN6KGCzbCIEAlsquS4Kjjax-NIG4TGfkY8t-UeS2MoCf_PA"
os.environ["GRPC_DEFAULT_SSL_ROOTS_FILE_PATH"] = ""
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

current_hour = datetime.now().hour
if current_hour < 12:
    time_greeting = "Good morning"
    theme_color = "#FFD700"  
    skin_title = "SUNRISE GOLD"
elif 12 <= current_hour < 17:
    time_greeting = "Good afternoon"
    theme_color = "#E0E0E0"  
    skin_title = "TITANIUM WHITE"
else:
    time_greeting = "Good evening"
    theme_color = "#FF4500"  
    skin_title = "STEALTH CRIMSON"

st.set_page_config(page_title="Strike Fit", page_icon="⚡", layout="wide")
st.markdown(f"""
    <style>
        .stApp {{ background-color: #0E1117; color: #E0E0E0; }}
        h1, h2, h3 {{ color: {theme_color} !important; font-family: 'Helvetica Neue', sans-serif; }}
        .stButton>button {{ background-color: {theme_color} !important; color: #0E1117 !important; font-weight: bold; border-radius: 8px; }}
        .stProgress>div>div>div>div {{ background-color: {theme_color} !important; }}
    </style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

global_countries = sorted([country.name for country in pycountry.countries])
priority_markets = ["Nigeria", "Sweden", "United States", "Netherlands"]
for market in reversed(priority_markets):
    if market in global_countries:
        global_countries.remove(market)
        global_countries.insert(0, market)

# ======================================================================
# 3. CINEMATIC SPORTS VIDEO SPLIT ACCESS CHECKPOINT (LOGIN / REGISTER)
# ======================================================================
if not st.session_state.logged_in:
    screen_left, screen_right = st.columns([1.2, 1.0])
    
    with screen_left:
        st.markdown(f"### ⚡ STRIKE FIT // PERFORMANCE LAB")
        st.video("https://w3schools.com", format="video/mp4", start_time=0)
        sc1, sc2, sc3 = st.columns(3)
        with sc1: st.metric("🪢 Peak Cadence", "182 JPM", "Rope Skip")
        with sc2: st.metric("🏃‍♂️ Target Pace", "4.35 m/km", "Zone 2 Run")
        with sc3: st.metric("🔥 Metabolic Burn", "11.4 kcal/m", "Incline Hike")
        st.info("💡 **Novice Shield Active:** Unexperienced profiles automatically receive pain-prevention guidance tracks natively.")
        
    with screen_right:
        st.title("🔐 SECURITY PORTAL")
        st.caption("🔒 ACCESS LOCKED // IDENTITY HANDSHAKE REQUIRED TO DEPLOY APP LAYERS")
        sec_tab1, sec_tab2 = st.tabs(["🔐 Identity Login Gateway", "📝 Create New Secure Profile"])
        
        with sec_tab1:
            l_user = st.text_input("Username Profile ID:", key="login_user")
            l_pass = st.text_input("Secure Vault Password:", type="password", key="login_pass")
            if st.button("AUTHORIZE CONNECTION & LOGIN", use_container_width=True):
                user_auth = verify_user(l_user, l_pass)
                if user_auth:
                    st.session_state.logged_in = True
                    st.session_state.username = l_user  
                    st.rerun()
                else: st.error("❌ Identity Connection Refused. Invalid credentials.")
                    
        with sec_tab2:
            r_user = st.text_input("Choose Unique Username ID:", key="reg_user")
            r_pass = st.text_input("Create Encrypted Password Code:", type="password", key="reg_pass")
            r_country = st.selectbox("Set Home Country Coordinate:", global_countries)
            if st.button("INITIALIZE RETENTION ACCOUNT ENGINE", use_container_width=True):
                if r_user and r_pass:
                    if register_user(r_user, r_pass, r_country): 
                        st.success("✅ Secure profile compiled! Move back to Login tab.")
                    else: 
                        st.error("❌ ID already claimed inside active servers.")
    st.stop()

user_profile = get_user_data(st.session_state.username)