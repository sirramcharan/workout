# app.py

import streamlit as st

import pandas as pd
import datetime
import time
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# app.py — add this near the top with other imports
import datetime
import pytz  # add this import

# IST Timezone
IST = pytz.timezone("Asia/Kolkata")

def get_now_ist():
    """Get current datetime in IST."""
    return datetime.datetime.now(IST)

def get_today():
    """Get today's date in IST."""
    return get_now_ist().date()

from github_utils import (
    load_data_from_github,
    append_and_save,
    save_data_to_github,
    get_empty_dataframe,
    delete_todays_rest_day,
)

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="FitTracker Pro",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# DARK OCEAN GLASS MORPHISM CSS
# ─────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    /* ── Import Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

    /* ── Root Variables ── */
    :root {
        --ocean-deep:    #020b18;
        --ocean-dark:    #041428;
        --ocean-mid:     #062040;
        --ocean-teal:    #0a3d62;
        --neon-cyan:     #00d4ff;
        --neon-blue:     #0099cc;
        --neon-green:    #00ff9d;
        --neon-orange:   #ff6b35;
        --neon-purple:   #8b5cf6;
        --glass-bg:      rgba(6, 32, 64, 0.55);
        --glass-border:  rgba(0, 212, 255, 0.18);
        --glass-shadow:  rgba(0, 212, 255, 0.08);
        --text-primary:  #e0f7ff;
        --text-muted:    #7fb3c8;
    }

    /* ── Global Background ── */
    .stApp {
        background: linear-gradient(135deg,
            #020b18 0%,
            #041428 25%,
            #062040 50%,
            #041428 75%,
            #020b18 100%
        ) !important;
        background-attachment: fixed !important;
        font-family: 'Rajdhani', sans-serif;
        color: var(--text-primary);
    }

    /* Animated background particles effect */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background:
            radial-gradient(ellipse at 20% 50%, rgba(0, 153, 204, 0.06) 0%, transparent 60%),
            radial-gradient(ellipse at 80% 20%, rgba(0, 212, 255, 0.04) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 80%, rgba(0, 255, 157, 0.03) 0%, transparent 60%);
        pointer-events: none;
        z-index: 0;
    }

    /* ── Hide Streamlit Branding ── */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container {
        padding-top: 1rem !important;
        max-width: 1400px !important;
    }

    /* ── Glass Card ── */
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        padding: 24px;
        box-shadow:
            0 8px 32px var(--glass-shadow),
            inset 0 1px 0 rgba(255,255,255,0.05);
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }

    .glass-card:hover {
        border-color: rgba(0, 212, 255, 0.35);
        box-shadow:
            0 12px 40px rgba(0, 212, 255, 0.12),
            inset 0 1px 0 rgba(255,255,255,0.08);
        transform: translateY(-2px);
    }

    /* ── Title Styling ── */
    .app-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00d4ff, #00ff9d, #0099cc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.2rem;
        letter-spacing: 3px;
        text-shadow: none;
    }

    .app-subtitle {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1rem;
        color: var(--text-muted);
        text-align: center;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-bottom: 1.5rem;
    }

    /* ── Date/Time Display ── */
    .datetime-display {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.1rem;
        color: var(--neon-cyan);
        text-align: center;
        letter-spacing: 2px;
        padding: 10px 20px;
        background: rgba(0, 212, 255, 0.05);
        border: 1px solid rgba(0, 212, 255, 0.15);
        border-radius: 12px;
        display: inline-block;
        width: 100%;
        margin-bottom: 1rem;
    }

    /* ── Mode Cards ── */
    .mode-card {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        padding: 30px 20px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        height: 180px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .mode-card.full-body {
        border-color: rgba(0, 212, 255, 0.3);
    }
    .mode-card.abs {
        border-color: rgba(0, 255, 157, 0.3);
    }
    .mode-card.both {
        border-color: rgba(139, 92, 246, 0.3);
    }
    .mode-card.rest {
        border-color: rgba(255, 107, 53, 0.3);
    }

    .mode-emoji {
        font-size: 3rem;
        margin-bottom: 10px;
    }

    .mode-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 0.9rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* ── Section Headers ── */
    .section-header {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.2rem;
        font-weight: 700;
        color: var(--neon-cyan);
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 15px;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(0, 212, 255, 0.2);
    }

    /* ── Exercise Cards ── */
    .exercise-header {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--neon-cyan);
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .set-badge {
        background: rgba(0, 212, 255, 0.15);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 8px;
        padding: 2px 10px;
        font-size: 0.85rem;
        color: var(--neon-cyan);
        font-family: 'Orbitron', sans-serif;
    }

    .completed-badge {
        background: rgba(0, 255, 157, 0.15);
        border: 1px solid rgba(0, 255, 157, 0.3);
        border-radius: 8px;
        padding: 2px 10px;
        font-size: 0.85rem;
        color: var(--neon-green);
        font-family: 'Orbitron', sans-serif;
    }

    /* ── Timer Display ── */
    .timer-container {
        background: rgba(0, 212, 255, 0.05);
        border: 2px solid rgba(0, 212, 255, 0.3);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        margin: 20px 0;
    }

    .timer-label {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-bottom: 10px;
    }

    .timer-display {
        font-family: 'Orbitron', sans-serif;
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00d4ff, #00ff9d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1;
    }

    /* ── Streamlit Element Overrides ── */
    .stButton > button {
        background: linear-gradient(135deg,
            rgba(0, 212, 255, 0.15),
            rgba(0, 153, 204, 0.10)
        ) !important;
        color: var(--neon-cyan) !important;
        border: 1px solid rgba(0, 212, 255, 0.4) !important;
        border-radius: 12px !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        backdrop-filter: blur(10px) !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg,
            rgba(0, 212, 255, 0.30),
            rgba(0, 153, 204, 0.25)
        ) !important;
        border-color: rgba(0, 212, 255, 0.8) !important;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.25) !important;
        transform: translateY(-1px) !important;
    }

    /* Primary / Green buttons */
    .stButton.primary-btn > button,
    div[data-testid="stButton"].primary-btn > button {
        background: linear-gradient(135deg,
            rgba(0, 255, 157, 0.20),
            rgba(0, 204, 120, 0.15)
        ) !important;
        color: var(--neon-green) !important;
        border-color: rgba(0, 255, 157, 0.5) !important;
    }

    /* ── Selectbox & Number Input ── */
    .stSelectbox > div > div,
    .stNumberInput > div > div > input {
        background: rgba(6, 32, 64, 0.8) !important;
        border: 1px solid rgba(0, 212, 255, 0.25) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
        font-family: 'Rajdhani', sans-serif !important;
    }

    .stSlider > div > div > div {
        background: rgba(0, 212, 255, 0.3) !important;
    }

    /* ── Progress Bar ── */
    .stProgress > div > div {
        background: linear-gradient(90deg, #00d4ff, #00ff9d) !important;
        border-radius: 10px !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(6, 32, 64, 0.6) !important;
        border-radius: 15px !important;
        padding: 5px !important;
        border: 1px solid rgba(0, 212, 255, 0.15) !important;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-muted) !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        border-radius: 10px !important;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(0, 212, 255, 0.15) !important;
        color: var(--neon-cyan) !important;
        border-bottom: 2px solid var(--neon-cyan) !important;
    }

    /* ── Metric Cards ── */
    .metric-card {
        background: var(--glass-bg);
        backdrop-filter: blur(15px);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
    }

    .metric-value {
        font-family: 'Orbitron', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: var(--neon-cyan);
    }

    .metric-label {
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.85rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 5px;
    }

    /* ── Success / Info / Warning Messages ── */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 12px !important;
        backdrop-filter: blur(10px) !important;
    }

    /* ── Divider ── */
    hr {
        border-color: rgba(0, 212, 255, 0.15) !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: var(--ocean-deep); }
    ::-webkit-scrollbar-thumb {
        background: var(--ocean-teal);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: var(--neon-blue); }

    /* ── Workout Done Banner ── */
    .done-banner {
        background: linear-gradient(135deg,
            rgba(0, 255, 157, 0.15),
            rgba(0, 212, 255, 0.10)
        );
        border: 1px solid rgba(0, 255, 157, 0.4);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        color: var(--neon-green);
        font-size: 1.1rem;
        letter-spacing: 2px;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        font-family: 'Rajdhani', sans-serif !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
FULL_BODY_EXERCISES = [
    ("🚶 Walking",      "Walking"),
    ("💪 Pushups",      "Pushups"),
    ("🔝 Pullups",      "Pullups"),
    ("🤸 Dips",         "Dips"),
    ("🦵 Squats",       "Squats"),
    ("🏋️ Rows",         "Rows"),
]

ABS_EXERCISES = [
    ("✝️ Crucifix Crunches",  "Crucifix Crunches"),
    ("🔒 Hold Series",        "Hold Series"),
    ("🧘 Side Plank Raises",  "Side Plank Raises"),
]

REST_TIMER_SECONDS   = 4 * 60   # 4 minutes
HOLD_SECONDS         = 30       # 30s each hold
SIDE_PLANK_SECONDS   = 60       # 1 min each side
CRUCIFIX_SETS        = 3

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
def init_session_state():
    defaults = {
        # Navigation
        "page":              "home",       # "home" | "dashboard"

        # Today's modes selected
        "selected_modes":    [],           # list: ["Full Body", "Abs"]
        "mode_confirmed":    False,

        # Full Body state
        "fb_num_sets":       2,
        "fb_sets_log":       {},           # {exercise: {set_num: {"reps": X, "saved": bool}}}
        "fb_walking_done":   False,
        "fb_walking_mins":   0,
        "fb_walking_km":     0.0,

        # Abs state
        "abs_sets_log":      {},           # {exercise: {set_num: {"reps": X, "saved": bool}}}

        # Timer state
        "timer_active":      False,
        "timer_end_time":    None,
        "timer_label":       "",
        "timer_phase":       None,         # "rest" | "hold1" | "hold2" | "sideL" | "sideR"

        # Hold series phase tracking
        "hold_phase":        0,            # 0=not started, 1=leg hold, 2=both up, 3=done

        # Side plank phase
        "side_phase":        0,            # 0=not started, 1=left, 2=right, 3=done

        # Data cache
        "data_loaded":       False,
        "df":                None,

        # Today's saved flag
        "rest_day_saved":    False,

        # Save confirmation flags
        "save_messages":     [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ─────────────────────────────────────────────
# DATA HELPERS
# ─────────────────────────────────────────────
def get_today():
    return datetime.date.today()

def load_df():
    if not st.session_state.data_loaded:
        st.session_state.df = load_data_from_github()
        st.session_state.data_loaded = True
    return st.session_state.df

def refresh_df():
    st.session_state.data_loaded = False
    return load_df()

def today_has_entry(exercise_name=None):
    df = load_df()
    if df.empty:
        return False
    today = get_today()
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    mask = df["Date"] == today
    if exercise_name:
        mask &= df["Exercise"] == exercise_name
    return mask.any()

def save_entry(mode, exercise, set_num, reps, duration_mins=0.0, distance_km=0.0, notes=""):
    today = get_today()
    row = {
        "Date":             today,
        "Mode":             mode,
        "Exercise":         exercise,
        "Set_Number":       set_num,
        "Reps":             reps,
        "Duration_Minutes": duration_mins,
        "Distance_KM":      distance_km,
        "Notes":            notes,
    }
    success, df_updated = append_and_save([row])
    if success:
        st.session_state.df = df_updated
        st.session_state.data_loaded = True
    return success

# ─────────────────────────────────────────────
# TIMER COMPONENT
# ─────────────────────────────────────────────
def render_timer():
    """Render a JavaScript countdown timer."""
    if not st.session_state.timer_active:
        return False

    now        = time.time()
    end_time   = st.session_state.timer_end_time
    remaining  = max(0, int(end_time - now))

    if remaining == 0:
        st.session_state.timer_active = False
        return True   # Timer finished

    mins = remaining // 60
    secs = remaining % 60

    # Progress
    total = {
        "rest":   REST_TIMER_SECONDS,
        "hold1":  HOLD_SECONDS,
        "hold2":  HOLD_SECONDS,
        "sideL":  SIDE_PLANK_SECONDS,
        "sideR":  SIDE_PLANK_SECONDS,
    }.get(st.session_state.timer_phase, REST_TIMER_SECONDS)

    progress_pct = (total - remaining) / total

    # Label colours
    color_map = {
        "rest":  "#00d4ff",
        "hold1": "#00ff9d",
        "hold2": "#8b5cf6",
        "sideL": "#ff6b35",
        "sideR": "#ff6b35",
    }
    color = color_map.get(st.session_state.timer_phase, "#00d4ff")

    st.markdown(f"""
    <div class="timer-container" style="border-color: {color}44;">
        <div class="timer-label">⏱️ {st.session_state.timer_label}</div>
        <div class="timer-display" style="
            background: linear-gradient(135deg, {color}, #00ff9d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        ">{mins:02d}:{secs:02d}</div>
    </div>
    """, unsafe_allow_html=True)

    st.progress(progress_pct)

    col_skip, col_space = st.columns([1, 3])
    with col_skip:
        if st.button("⏭️ Skip Timer", key="skip_timer"):
            st.session_state.timer_active = False
            st.rerun()

    # Auto-rerun every second while timer is running
    time.sleep(1)
    st.rerun()
    return False

def start_timer(phase: str, label: str, duration: int):
    st.session_state.timer_active   = True
    st.session_state.timer_end_time = time.time() + duration
    st.session_state.timer_phase    = phase
    st.session_state.timer_label    = label

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
def render_header():
    st.markdown('<div class="app-title">⚡ FITTRACKER PRO</div>', 
                unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Your Daily Fitness Command Center</div>',
                unsafe_allow_html=True)

    # ✅ Live IST date/time
    now_ist = get_now_ist()
    now_str = now_ist.strftime("%A, %B %d %Y  |  %I:%M:%S %p")
    st.markdown(
        f'<div class="datetime-display">🗓️ {now_str} IST 🇮🇳</div>',
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────
# NAV BAR
# ─────────────────────────────────────────────
def render_nav():
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🏋️ Today's Workout"):
            st.session_state.page = "home"
            st.rerun()
    with col2:
        if st.button("📊 Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
    st.markdown("---")

# ─────────────────────────────────────────────
# MODE SELECTION
# ─────────────────────────────────────────────
def render_mode_selection():
    st.markdown('<div class="section-header">SELECT TODAY\'S WORKOUT MODE</div>',
                unsafe_allow_html=True)

    # Suggest based on last workout
    df   = load_df()
    suggestion = _get_suggestion(df)
    if suggestion:
        st.info(f"💡 **Suggested today:** {suggestion}  _(based on your last workout)_")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="mode-card full-body">
            <div class="mode-emoji">🏋️</div>
            <div class="mode-title" style="color:#00d4ff;">Full Body</div>
        </div>""", unsafe_allow_html=True)
        if st.button("SELECT  Full Body", key="btn_fb"):
            _set_modes(["Full Body"])

    with col2:
        st.markdown("""
        <div class="mode-card abs">
            <div class="mode-emoji">🔥</div>
            <div class="mode-title" style="color:#00ff9d;">Abs</div>
        </div>""", unsafe_allow_html=True)
        if st.button("SELECT  Abs", key="btn_abs"):
            _set_modes(["Abs"])

    with col3:
        st.markdown("""
        <div class="mode-card both">
            <div class="mode-emoji">⚡</div>
            <div class="mode-title" style="color:#8b5cf6;">Both</div>
        </div>""", unsafe_allow_html=True)
        if st.button("SELECT  Both", key="btn_both"):
            _set_modes(["Full Body", "Abs"])

    with col4:
        st.markdown("""
        <div class="mode-card rest">
            <div class="mode-emoji">😴</div>
            <div class="mode-title" style="color:#ff6b35;">Rest Day</div>
        </div>""", unsafe_allow_html=True)
        if st.button("REST DAY TODAY", key="btn_rest"):
            _set_modes(["Rest"])

def _get_suggestion(df):
    if df.empty:
        return None
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    today = get_today()
    recent = df[df["Date"] < today].sort_values("Date", ascending=False)
    if recent.empty:
        return None
    last_mode = recent.iloc[0]["Mode"]
    if last_mode == "Full Body":
        return "Abs"
    elif last_mode == "Abs":
        return "Full Body"
    elif last_mode == "Rest":
        return "Full Body or Abs (you rested yesterday!)"
    return None

def _set_modes(modes):
    st.session_state.selected_modes  = modes
    st.session_state.mode_confirmed   = True
    # Reset workout state
    st.session_state.fb_sets_log      = {}
    st.session_state.abs_sets_log     = {}
    st.session_state.fb_walking_done  = False
    st.session_state.timer_active     = False
    st.session_state.hold_phase       = 0
    st.session_state.side_phase       = 0
    st.session_state.rest_day_saved   = False
    st.rerun()

# ─────────────────────────────────────────────
# REST DAY
# ─────────────────────────────────────────────
def render_rest_day():
    st.markdown("""
    <div class="done-banner" style="border-color: rgba(255,107,53,0.4);
         background: linear-gradient(135deg, rgba(255,107,53,0.12), rgba(255,100,0,0.06));
         color: #ff6b35; font-size:1.4rem; padding: 40px;">
        😴 REST DAY<br>
        <span style="font-size:0.9rem; color:#7fb3c8; font-family:'Rajdhani',sans-serif;">
        Recovery is part of the grind. You've earned it!
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not st.session_state.rest_day_saved:
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("✅ Confirm Rest Day", key="confirm_rest"):
                success = save_entry("Rest", "Rest Day", 0, 0, notes="Rest Day")
                if success:
                    st.session_state.rest_day_saved = True
                    st.success("😴 Rest day logged successfully!")
                    st.rerun()
    else:
        st.success("✅ Rest day already logged for today!")

    col_back, _ = st.columns([1, 3])
    with col_back:
        if st.button("🔄 Change Mode", key="rest_back"):
            st.session_state.mode_confirmed = False
            st.rerun()

# ─────────────────────────────────────────────
# FULL BODY WORKOUT
# ─────────────────────────────────────────────
def render_full_body():
    st.markdown('<div class="section-header">🏋️ FULL BODY WORKOUT</div>',
                unsafe_allow_html=True)

    # ── Number of sets selector ──
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    col_sets, col_info = st.columns([2, 4])
    with col_sets:
        num_sets = st.number_input(
            "🔢 Sets per Exercise",
            min_value=0, max_value=10,
            value=st.session_state.fb_num_sets,
            step=1, key="fb_sets_input"
        )
        st.session_state.fb_num_sets = num_sets
    with col_info:
        st.markdown(f"""
        <div style="padding-top:30px; color: #7fb3c8; font-family:'Rajdhani',sans-serif; font-size:1rem;">
        ℹ️ You've selected <strong style="color:#00d4ff">{num_sets} set(s)</strong> per exercise.
        Complete them in any order you like!
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Active Timer (if running) ──
    if st.session_state.timer_active and st.session_state.timer_phase == "rest":
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        render_timer()
        st.markdown('</div>', unsafe_allow_html=True)
        return   # Block UI while resting

    # ── Walking Section ──
    _render_walking_section()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Exercise Sections ──
    if num_sets > 0:
        st.markdown('<div class="section-header">💪 EXERCISES</div>', unsafe_allow_html=True)
        for emoji_name, ex_key in FULL_BODY_EXERCISES[1:]:   # Skip walking
            _render_exercise_block(emoji_name, ex_key, num_sets, "Full Body")
    else:
        st.info("ℹ️ Set the number of sets above to start logging exercises.")

    # ── Overall progress ──
    _render_fb_progress(num_sets)

def _render_walking_section():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="exercise-header">🚶 Walking</div>', unsafe_allow_html=True)

    if st.session_state.fb_walking_done:
        st.markdown(f"""
        <div class="completed-badge" style="display:inline-block; margin-top:8px;">
        ✅ Logged — {st.session_state.fb_walking_mins} mins | 
        {st.session_state.fb_walking_km:.2f} km
        </div>""", unsafe_allow_html=True)
    else:
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            walk_mins = st.number_input("⏱️ Minutes walked", min_value=0, max_value=300,
                                        value=0, step=1, key="walk_mins")
        with col2:
            walk_km   = st.number_input("📏 Distance (km)", min_value=0.0, max_value=50.0,
                                        value=0.0, step=0.1, key="walk_km",
                                        format="%.2f")
        with col3:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("✅ Log Walk", key="log_walk"):
                if walk_mins > 0:
                    success = save_entry(
                        mode="Full Body", exercise="Walking",
                        set_num=1, reps=0,
                        duration_mins=float(walk_mins),
                        distance_km=float(walk_km),
                    )
                    if success:
                        st.session_state.fb_walking_done = True
                        st.session_state.fb_walking_mins = walk_mins
                        st.session_state.fb_walking_km   = walk_km
                        st.success("🚶 Walk logged!")
                        st.rerun()
                else:
                    st.warning("Enter minutes walked first!")
    st.markdown('</div>', unsafe_allow_html=True)

def _render_exercise_block(emoji_name, ex_key, num_sets, mode):
    """Render a collapsible exercise block with set tracking."""
    if ex_key not in st.session_state.fb_sets_log:
        st.session_state.fb_sets_log[ex_key] = {}

    sets_done = len([
        s for s, v in st.session_state.fb_sets_log[ex_key].items()
        if v.get("saved", False)
    ])

    with st.expander(f"{emoji_name}  —  {sets_done}/{num_sets} sets done", expanded=False):
        for set_num in range(1, num_sets + 1):
            set_data = st.session_state.fb_sets_log[ex_key].get(set_num, {})
            saved    = set_data.get("saved", False)

            col_label, col_input, col_btn = st.columns([2, 3, 2])
            with col_label:
                if saved:
                    st.markdown(
                        f'<span class="completed-badge">✅ Set {set_num} — {set_data["reps"]} reps</span>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<span class="set-badge">Set {set_num}</span>',
                        unsafe_allow_html=True
                    )

            if not saved:
                with col_input:
                    reps_val = st.number_input(
                        f"Reps", min_value=0, max_value=500, value=0, step=1,
                        key=f"reps_{ex_key}_{set_num}"
                    )
                with col_btn:
                    if st.button(f"✅ Set {set_num} Done", key=f"done_{ex_key}_{set_num}"):
                        if reps_val > 0:
                            success = save_entry(
                                mode=mode, exercise=ex_key,
                                set_num=set_num, reps=reps_val,
                            )
                            if success:
                                st.session_state.fb_sets_log[ex_key][set_num] = {
                                    "reps":  reps_val,
                                    "saved": True,
                                }
                                # Start rest timer if not last set
                                remaining_sets = [
                                    s for s in range(1, num_sets + 1)
                                    if not st.session_state.fb_sets_log[ex_key]
                                       .get(s, {}).get("saved", False)
                                ]
                                if remaining_sets:
                                    start_timer(
                                        phase="rest",
                                        label="REST BETWEEN SETS — 4 MINUTES",
                                        duration=REST_TIMER_SECONDS,
                                    )
                                st.success(f"💪 {ex_key} Set {set_num} — {reps_val} reps logged!")
                                st.rerun()
                        else:
                            st.warning("Enter reps before marking set done!")

def _render_fb_progress(num_sets):
    """Show overall Full Body completion progress."""
    if num_sets == 0:
        return
    exercises = [ex for _, ex in FULL_BODY_EXERCISES[1:]]
    total_sets = len(exercises) * num_sets
    done_sets  = sum(
        len([s for s, v in st.session_state.fb_sets_log.get(ex, {}).items()
             if v.get("saved", False)])
        for ex in exercises
    )
    pct = done_sets / total_sets if total_sets > 0 else 0

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="section-header">📊 FULL BODY PROGRESS — {done_sets}/{total_sets} sets</div>',
        unsafe_allow_html=True
    )
    st.progress(pct)
    if done_sets == total_sets:
        st.markdown("""
        <div class="done-banner">🎉 FULL BODY WORKOUT COMPLETE! CRUSHING IT! 🎉</div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ABS WORKOUT
# ─────────────────────────────────────────────
def render_abs():
    st.markdown('<div class="section-header">🔥 ABS WORKOUT</div>', unsafe_allow_html=True)

    # ── Active Timer ──
    if st.session_state.timer_active:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        finished = render_timer()
        st.markdown('</div>', unsafe_allow_html=True)
        if finished:
            # Post-timer actions
            if st.session_state.timer_phase == "hold1":
                st.session_state.hold_phase = 2
                start_timer("hold2", "BOTH HANDS & LEGS UP — 30 SECONDS", HOLD_SECONDS)
                st.rerun()
            elif st.session_state.timer_phase == "hold2":
                st.session_state.hold_phase = 3
                # Start 4-min rest after hold series
                start_timer("rest", "REST AFTER HOLD SERIES — 4 MINUTES", REST_TIMER_SECONDS)
                st.rerun()
            elif st.session_state.timer_phase == "sideL":
                st.session_state.side_phase = 2
                start_timer("sideR", "RIGHT SIDE PLANK — 1 MINUTE", SIDE_PLANK_SECONDS)
                st.rerun()
            elif st.session_state.timer_phase == "sideR":
                st.session_state.side_phase = 3
                st.rerun()
        else:
            return   # Block UI while timer runs

    # ── Crucifix Crunches ──
    _render_crucifix_section()
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Hold Series ──
    _render_hold_series()
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Side Plank Raises ──
    _render_side_plank()

    # ── Abs Progress ──
    _render_abs_progress()

def _render_crucifix_section():
    if "Crucifix Crunches" not in st.session_state.abs_sets_log:
        st.session_state.abs_sets_log["Crucifix Crunches"] = {}

    sets_done = len([
        s for s, v in st.session_state.abs_sets_log["Crucifix Crunches"].items()
        if v.get("saved", False)
    ])

    with st.expander(
        f"✝️ Crucifix Crunches  —  {sets_done}/{CRUCIFIX_SETS} sets done",
        expanded=True
    ):
        for set_num in range(1, CRUCIFIX_SETS + 1):
            set_data = st.session_state.abs_sets_log["Crucifix Crunches"].get(set_num, {})
            saved    = set_data.get("saved", False)

            col_label, col_input, col_btn = st.columns([2, 3, 2])
            with col_label:
                badge = (
                    f'<span class="completed-badge">✅ Set {set_num} — {set_data["reps"]} reps</span>'
                    if saved else
                    f'<span class="set-badge">Set {set_num}</span>'
                )
                st.markdown(badge, unsafe_allow_html=True)

            if not saved:
                with col_input:
                    reps_val = st.number_input(
                        "Reps", min_value=0, max_value=500, value=0, step=1,
                        key=f"reps_crucifx_{set_num}"
                    )
                with col_btn:
                    if st.button(f"✅ Set {set_num} Done", key=f"done_crucifx_{set_num}"):
                        if reps_val > 0:
                            success = save_entry(
                                mode="Abs", exercise="Crucifix Crunches",
                                set_num=set_num, reps=reps_val,
                            )
                            if success:
                                st.session_state.abs_sets_log["Crucifix Crunches"][set_num] = {
                                    "reps": reps_val, "saved": True
                                }
                                if set_num < CRUCIFIX_SETS:
                                    start_timer(
                                        "rest",
                                        "REST AFTER CRUCIFIX CRUNCHES — 4 MINUTES",
                                        REST_TIMER_SECONDS,
                                    )
                                st.success(f"✝️ Crucifix Crunches Set {set_num} — {reps_val} reps!")
                                st.rerun()
                        else:
                            st.warning("Enter reps!")

def _render_hold_series():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="exercise-header">🔒 Hold Series</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="color:#7fb3c8; font-size:0.9rem; margin:8px 0;">1️⃣ Leg Hold (30s) → 2️⃣ Both Hands & Legs Up (30s) → ⏱️ 4 min rest</div>',
        unsafe_allow_html=True
    )

    phase = st.session_state.hold_phase

    if phase == 0:
        # Not started
        if "Hold Series" not in st.session_state.abs_sets_log:
            st.session_state.abs_sets_log["Hold Series"] = {}
        if st.button("▶️ Start Leg Hold (30s)", key="start_hold1"):
            start_timer("hold1", "LEG HOLD — 30 SECONDS", HOLD_SECONDS)
            st.session_state.hold_phase = 1
            st.rerun()

    elif phase == 1:
        st.info("🦵 Lift your legs up and hold! Timer is running...")

    elif phase == 2:
        st.info("💪 Now raise both hands & legs! Timer is running...")

    elif phase == 3:
        # Completed — save entry
        if "Hold Series" not in st.session_state.abs_sets_log:
            st.session_state.abs_sets_log["Hold Series"] = {}
        if not st.session_state.abs_sets_log.get("Hold Series", {}).get(1, {}).get("saved"):
            success = save_entry(
                mode="Abs", exercise="Hold Series", set_num=1,
                reps=0, duration_mins=1.0,
                notes="30s leg hold + 30s both up"
            )
            if success:
                st.session_state.abs_sets_log["Hold Series"] = {
                    1: {"reps": 0, "saved": True}
                }
        st.markdown(
            '<span class="completed-badge">✅ Hold Series Complete!</span>',
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)

def _render_side_plank():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="exercise-header">🧘 Side Plank Raises</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="color:#7fb3c8; font-size:0.9rem; margin:8px 0;">⬅️ Left Side (1 min) → ➡️ Right Side (1 min)</div>',
        unsafe_allow_html=True
    )

    phase = st.session_state.side_phase

    if phase == 0:
        if st.button("▶️ Start Left Side Plank (1 min)", key="start_side_l"):
            start_timer("sideL", "LEFT SIDE PLANK — 1 MINUTE", SIDE_PLANK_SECONDS)
            st.session_state.side_phase = 1
            st.rerun()

    elif phase == 1:
        st.info("⬅️ Hold your left side plank! Timer running...")

    elif phase == 2:
        st.info("➡️ Now switch to right side! Timer running...")

    elif phase == 3:
        if "Side Plank Raises" not in st.session_state.abs_sets_log:
            st.session_state.abs_sets_log["Side Plank Raises"] = {}
        if not st.session_state.abs_sets_log.get("Side Plank Raises", {}).get(1, {}).get("saved"):
            success = save_entry(
                mode="Abs", exercise="Side Plank Raises", set_num=1,
                reps=0, duration_mins=2.0,
                notes="1 min left + 1 min right"
            )
            if success:
                st.session_state.abs_sets_log["Side Plank Raises"] = {
                    1: {"reps": 0, "saved": True}
                }
        st.markdown(
            '<span class="completed-badge">✅ Side Planks Complete!</span>',
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)

def _render_abs_progress():
    total = 3   # Crucifix (3 sets) + Hold Series + Side Plank = 5 trackable items
    done  = 0

    cc_sets = len([s for s, v in
                   st.session_state.abs_sets_log.get("Crucifix Crunches", {}).items()
                   if v.get("saved")])
    done += cc_sets

    if st.session_state.abs_sets_log.get("Hold Series", {}).get(1, {}).get("saved"):
        done += 1
    if st.session_state.abs_sets_log.get("Side Plank Raises", {}).get(1, {}).get("saved"):
        done += 1

    total_items = CRUCIFIX_SETS + 2
    pct = done / total_items

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="section-header">📊 ABS PROGRESS — {done}/{total_items} items</div>',
        unsafe_allow_html=True
    )
    st.progress(pct)
    if done == total_items:
        st.markdown(
            '<div class="done-banner">🔥 ABS WORKOUT COMPLETE! BEAST MODE! 🔥</div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────
def render_dashboard():
    st.markdown('<div class="section-header">📊 FITNESS DASHBOARD</div>',
                unsafe_allow_html=True)

    # Reload fresh data
    df = refresh_df()

    if df.empty:
        st.info("📭 No workout data yet! Complete some workouts to see your dashboard.")
        return

    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    today       = get_today()
    week_start  = today - datetime.timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    df_week     = df[df["Date"] >= week_start]
    df_month    = df[df["Date"] >= month_start]

    # ── Top KPI Cards ──
    _render_kpi_cards(df, df_week, df_month, today)

    st.markdown("---")

    # ── Tabs ──
    tab_weekly, tab_monthly, tab_insights = st.tabs([
        "📅 This Week", "🗓️ This Month", "🔍 Deep Insights"
    ])

    with tab_weekly:
        _render_weekly_charts(df_week, df)

    with tab_monthly:
        _render_monthly_charts(df_month)

    with tab_insights:
        _render_insights(df)

def _render_kpi_cards(df, df_week, df_month, today):
    df["Date"] = pd.to_datetime(df["Date"]).dt.date

    # Workout streak
    streak = _calc_streak(df, today)

    # Total workouts this week (unique days, non-rest)
    active_days_week = df_week[df_week["Exercise"] != "Rest Day"]["Date"].nunique()

    # Total reps this month (exercises only)
    df_ex = df_month[~df_month["Exercise"].isin(["Rest Day", "Walking", "Hold Series", "Side Plank Raises"])]
    total_reps_month = int(df_ex["Reps"].sum())

    # Total walking km
    total_km = df[df["Exercise"] == "Walking"]["Distance_KM"].sum()

    # Total walking mins
    total_walk_mins = df[df["Exercise"] == "Walking"]["Duration_Minutes"].sum()

    cols = st.columns(5)
    kpis = [
        ("🔥 Streak",           f"{streak} days",          "#ff6b35"),
        ("🏋️ Days This Week",   f"{active_days_week} / 7", "#00d4ff"),
        ("💪 Reps This Month",  f"{total_reps_month:,}",   "#00ff9d"),
        ("🚶 Total KM Walked",  f"{total_km:.1f} km",      "#8b5cf6"),
        ("⏱️ Walking Minutes",  f"{int(total_walk_mins)} min", "#f59e0b"),
    ]
    for col, (label, value, color) in zip(cols, kpis):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color:{color};">{value}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

def _calc_streak(df, today):
    if df.empty:
        return 0
    active_dates = sorted(
        df[df["Exercise"] != "Rest Day"]["Date"].unique(), reverse=True
    )
    streak = 0
    check  = today
    for d in active_dates:
        if d == check or d == check - datetime.timedelta(days=1):
            streak += 1
            check   = d
        else:
            break
    return streak

def _render_weekly_charts(df_week, df_all):
    if df_week.empty:
        st.info("💤 No workouts logged this week yet.")
        return

    plotly_theme = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
        font_color   ="#e0f7ff",
        font_family  ="Rajdhani",
    )

    # ── Reps per exercise this week ──
    df_ex = df_week[~df_week["Exercise"].isin(
        ["Rest Day", "Walking", "Hold Series", "Side Plank Raises"]
    )]

    if not df_ex.empty:
        fig_reps = px.bar(
            df_ex.groupby("Exercise")["Reps"].sum().reset_index(),
            x="Exercise", y="Reps",
            title="💪 Total Reps This Week by Exercise",
            color="Reps",
            color_continuous_scale=["#0a3d62", "#00d4ff", "#00ff9d"],
        )
        fig_reps.update_layout(**plotly_theme, title_font_size=16)
        fig_reps.update_traces(marker_line_color="rgba(0,212,255,0.3)",
                               marker_line_width=1)
        st.plotly_chart(fig_reps, use_container_width=True)

    # ── Day by day reps breakdown ──
    col1, col2 = st.columns(2)

    with col1:
        if not df_ex.empty:
            df_ex2 = df_ex.copy()
            df_ex2["Date"] = df_ex2["Date"].astype(str)
            fig_daily = px.bar(
                df_ex2.groupby(["Date", "Exercise"])["Reps"].sum().reset_index(),
                x="Date", y="Reps", color="Exercise",
                title="📅 Daily Reps Breakdown",
                color_discrete_sequence=px.colors.sequential.Tealgrn,
                barmode="stack",
            )
            fig_daily.update_layout(**plotly_theme, title_font_size=14)
            st.plotly_chart(fig_daily, use_container_width=True)

    with col2:
        # Walking this week
        df_walk = df_week[df_week["Exercise"] == "Walking"]
        if not df_walk.empty:
            df_walk2 = df_walk.copy()
            df_walk2["Date"] = df_walk2["Date"].astype(str)
            fig_walk = px.bar(
                df_walk2,
                x="Date", y="Duration_Minutes",
                title="🚶 Walking Minutes This Week",
                color_discrete_sequence=["#8b5cf6"],
                text="Distance_KM",
            )
            fig_walk.update_traces(texttemplate="%{text:.1f} km",
                                   textposition="outside")
            fig_walk.update_layout(**plotly_theme, title_font_size=14)
            st.plotly_chart(fig_walk, use_container_width=True)
        else:
            st.info("🚶 No walking data this week.")

    # ── Mode split pie ──
    mode_counts = df_week["Mode"].value_counts().reset_index()
    mode_counts.columns = ["Mode", "Count"]
    if not mode_counts.empty:
        fig_pie = px.pie(
            mode_counts, names="Mode", values="Count",
            title="🎯 Workout Mode Distribution This Week",
            color_discrete_sequence=["#00d4ff", "#00ff9d", "#8b5cf6", "#ff6b35"],
            hole=0.4,
        )
        fig_pie.update_layout(**plotly_theme, title_font_size=14)
        st.plotly_chart(fig_pie, use_container_width=True)

def _render_monthly_charts(df_month):
    if df_month.empty:
        st.info("💤 No workouts logged this month yet.")
        return

    plotly_theme = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
        font_color   ="#e0f7ff",
        font_family  ="Rajdhani",
    )

    df_month = df_month.copy()
    df_month["Date_str"] = df_month["Date"].astype(str)

    # ── Volume over time per exercise ──
    df_ex = df_month[~df_month["Exercise"].isin(
        ["Rest Day", "Walking", "Hold Series", "Side Plank Raises"]
    )]

    if not df_ex.empty:
        fig_trend = px.line(
            df_ex.groupby(["Date_str", "Exercise"])["Reps"].sum().reset_index(),
            x="Date_str", y="Reps", color="Exercise",
            title="📈 Reps Trend This Month",
            markers=True,
            color_discrete_sequence=px.colors.sequential.Tealgrn,
        )
        fig_trend.update_layout(**plotly_theme, title_font_size=16)
        st.plotly_chart(fig_trend, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        # Total sets per exercise
        if not df_ex.empty:
            sets_df = df_ex.groupby("Exercise")["Set_Number"].count().reset_index()
            sets_df.columns = ["Exercise", "Total Sets"]
            fig_sets = px.bar(
                sets_df, x="Exercise", y="Total Sets",
                title="🔢 Total Sets Per Exercise (Month)",
                color="Total Sets",
                color_continuous_scale=["#041428", "#0099cc", "#00d4ff"],
            )
            fig_sets.update_layout(**plotly_theme, title_font_size=14)
            st.plotly_chart(fig_sets, use_container_width=True)

    with col2:
        # Walking KM over time
        df_walk = df_month[df_month["Exercise"] == "Walking"].copy()
        if not df_walk.empty:
            fig_km = px.area(
                df_walk,
                x="Date_str", y="Distance_KM",
                title="🚶 Walking Distance This Month (KM)",
                color_discrete_sequence=["#8b5cf6"],
            )
            fig_km.update_traces(fillcolor="rgba(139,92,246,0.15)")
            fig_km.update_layout(**plotly_theme, title_font_size=14)
            st.plotly_chart(fig_km, use_container_width=True)
        else:
            st.info("🚶 No walking data this month.")

    # ── Activity Calendar Heatmap ──
    _render_activity_heatmap(df_month, plotly_theme)

def _render_activity_heatmap(df_month, plotly_theme):
    df_active = df_month[df_month["Exercise"] != "Rest Day"].copy()
    if df_active.empty:
        return

    daily_reps = df_active.groupby("Date")["Reps"].sum().reset_index()
    daily_reps["Week"]    = daily_reps["Date"].apply(
        lambda d: (d - d.replace(day=1)).days // 7
    )
    daily_reps["Weekday"] = daily_reps["Date"].apply(lambda d: d.weekday())
    daily_reps["Day"]     = daily_reps["Date"].apply(
        lambda d: d.strftime("%b %d")
    )

    fig_heat = go.Figure(go.Scatter(
        x=daily_reps["Date"].astype(str),
        y=daily_reps["Reps"],
        mode="markers+lines",
        marker=dict(
            size=12,
            color=daily_reps["Reps"],
            colorscale=[[0, "#041428"], [0.5, "#00d4ff"], [1, "#00ff9d"]],
            showscale=True,
            colorbar=dict(title="Reps"),
            line=dict(color="rgba(0,212,255,0.4)", width=1)
        ),
        line=dict(color="rgba(0,212,255,0.3)"),
        text=daily_reps["Day"],
        hovertemplate="<b>%{text}</b><br>Total Reps: %{y}<extra></extra>",
    ))
    fig_heat.update_layout(
        **plotly_theme,
        title="🗓️ Daily Activity — Reps This Month",
        title_font_size=14,
        xaxis_title="Date",
        yaxis_title="Total Reps",
    )
    st.plotly_chart(fig_heat, use_container_width=True)

def _render_insights(df):
    if df.empty:
        st.info("No data for insights yet.")
        return

    plotly_theme = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
        font_color   ="#e0f7ff",
        font_family  ="Rajdhani",
    )

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    df_ex = df[~df["Exercise"].isin(
        ["Rest Day", "Walking", "Hold Series", "Side Plank Raises"]
    )]

    col1, col2 = st.columns(2)

    with col1:
        # Personal bests
        if not df_ex.empty:
            st.markdown('<div class="section-header">🏆 PERSONAL BESTS (MAX REPS IN A SET)</div>',
                        unsafe_allow_html=True)
            pb_df = df_ex.groupby("Exercise")["Reps"].max().reset_index()
            pb_df.columns = ["Exercise", "Max Reps"]
            pb_df = pb_df.sort_values("Max Reps", ascending=False)

            fig_pb = px.bar(
                pb_df, x="Max Reps", y="Exercise",
                orientation="h",
                title="🏆 Personal Bests",
                color="Max Reps",
                color_continuous_scale=["#041428", "#ff6b35", "#ffcc00"],
            )
            fig_pb.update_layout(**plotly_theme, title_font_size=14)
            st.plotly_chart(fig_pb, use_container_width=True)

    with col2:
        # Rest vs Active days
        total_days = df["Date"].nunique()
        rest_days  = df[df["Exercise"] == "Rest Day"]["Date"].nunique()
        active_days = total_days - rest_days

        fig_donut = go.Figure(go.Pie(
            labels=["Active Days 💪", "Rest Days 😴"],
            values=[active_days, rest_days],
            hole=0.55,
            marker_colors=["#00ff9d", "#ff6b35"],
            textfont_size=14,
        ))
        fig_donut.update_layout(
            **plotly_theme,
            title="😴 Active vs Rest Days (All Time)",
            title_font_size=14,
            annotations=[dict(
                text=f"{active_days}<br>Active",
                font_size=16, font_color="#00ff9d",
                showarrow=False
            )]
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    # ── Volume progression ──
    if not df_ex.empty:
        df_ex2 = df_ex.copy()
        df_ex2["Date_str"] = df_ex2["Date"].astype(str)
        df_ex2["Volume"]   = df_ex2["Reps"] * df_ex2["Set_Number"]  # Volume proxy

        fig_vol = px.area(
            df_ex2.groupby(["Date_str"])["Reps"].sum().reset_index(),
            x="Date_str", y="Reps",
            title="📈 Total Reps Volume — All Time",
            color_discrete_sequence=["#00d4ff"],
        )
        fig_vol.update_traces(fillcolor="rgba(0,212,255,0.10)")
        fig_vol.update_layout(
            **plotly_theme, title_font_size=14,
            xaxis_title="Date", yaxis_title="Total Reps"
        )
        st.plotly_chart(fig_vol, use_container_width=True)

    # ── Most consistent exercise ──
    if not df_ex.empty:
        consistency = df_ex.groupby("Exercise")["Date"].nunique().reset_index()
        consistency.columns = ["Exercise", "Days Performed"]
        consistency = consistency.sort_values("Days Performed", ascending=False)

        fig_consist = px.bar(
            consistency, x="Exercise", y="Days Performed",
            title="📅 Consistency — Days Each Exercise Was Performed",
            color="Days Performed",
            color_continuous_scale=["#041428", "#8b5cf6", "#00d4ff"],
        )
        fig_consist.update_layout(**plotly_theme, title_font_size=14)
        st.plotly_chart(fig_consist, use_container_width=True)

    # ── Raw data table ──
    with st.expander("📋 View Raw Workout Log"):
        st.dataframe(
            df.sort_values("Date", ascending=False),
            use_container_width=True,
            hide_index=True,
        )

# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
def main():
    inject_css()
    init_session_state()
    render_header()
    render_nav()

    if st.session_state.page == "dashboard":
        render_dashboard()
        return

    # ── HOME PAGE ──
    if not st.session_state.mode_confirmed:
        render_mode_selection()
        return

    modes = st.session_state.selected_modes

    # ── Change Mode button ──
    col_chg, _ = st.columns([1, 5])
    with col_chg:
        if st.button("🔄 Change Mode", key="change_mode_top"):
            st.session_state.mode_confirmed = False
            st.rerun()

    # ── Render selected modes ──
    if "Rest" in modes:
        render_rest_day()
        return

    if "Full Body" in modes and "Abs" in modes:
        tab_fb, tab_abs = st.tabs(["🏋️ Full Body", "🔥 Abs"])
        with tab_fb:
            render_full_body()
        with tab_abs:
            render_abs()

    elif "Full Body" in modes:
        render_full_body()

    elif "Abs" in modes:
        render_abs()

if __name__ == "__main__":
    main()
