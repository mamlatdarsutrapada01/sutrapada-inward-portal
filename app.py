import io
import sqlite3
import time
from datetime import date
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

# ==========================================
# ૦. પેજ સેટઅપ અને સરકારી બ્લુ થીમ CSS
# ==========================================
st.set_page_config(
    page_title="મામલતદાર કચેરી સુત્રાપાડા - ઈ-ઇનવર્ડ પોર્ટલ",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === લૉગિન સ્ટેટ મેનેજમેન્ટ ===
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""
if 'user_role' not in st.session_state:
    st.session_state.user_role = ""

# Custom CSS for UI & Designer Credit
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Gujarati:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"], div, span, h1, h2, h3, h4, p {
        font-family: 'Noto Sans Gujarati', 'Segoe UI', Tahoma, sans-serif !important;
        color: #0F172A !important;
    }

    .stApp {
        background-color: #F0F4F8;
    }
    
    [data-testid="stSidebar"] {
        background-color: #0A2540 !important;
        border-right: 2px solid #1E3A8A;
    }

    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    .govt-header {
        background: linear-gradient(135deg, #003366 0%, #001A33 100%);
        color: #FFFFFF !important;
        padding: 22px 28px;
        border-radius: 10px;
        box-shadow: 0 4px 14px rgba(0, 51, 102, 0.25);
        border-left: 6px solid #FF9933;
        margin-bottom: 25px;
    }

    .govt-title {
        font-size: 26px;
        font-weight: 700;
        margin: 0;
        color: #FFFFFF !important;
    }

    .govt-subtitle {
        font-size: 14px;
        color: #E2E8F0 !important;
        margin-top: 6px;
    }

    .stat-card {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 10px;
        padding: 18px;
        box-shadow: 0 2px 6px rgba(0, 51, 102, 0.06);
        border-top: 5px solid #003366;
    }

    .stat-title {
        color: #475569 !important;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
    }

    .stat-value {
        color: #003366 !important;
        font-size: 28px;
        font-weight: 700;
        margin-top: 8px;
    }

    .stButton>button {
        background-color: #003366 !important;
        color: #FFFFFF !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 10px 24px !important;
    }

    .stButton>button:hover {
        background-color: #0055A5 !important;
        color: #FFFFFF !important;
    }

    input, select, textarea {
        border-radius: 6px !important;
        border: 1px solid #94A3B8 !important;
        background-color: #FFFFFF !important;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #CBD5E1;
        border-radius: 8px;
        background-color: #FFFFFF;
    }

    .designer-box {
        background: linear-gradient(135deg, #FF9933 0%, #D97706 100%);
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        margin-top: 20px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
    }
    .designer-text {
        font-size: 11px;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: #FFFFFF !important;
        margin-bottom: 2px;
    }
    .designer-name {
        font-size: 16px;
        font-weight: 700;
        color: #FFFFFF !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.4);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔐 લૉગિન પેજ (BRANCH & ADMIN LOGIN)
# ==========================================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div style="text-align: center; background: #FFFFFF; padding: 30px; border-radius: 12px; box-shadow: 0 6px 20px rgba(0,51,102,0.15); border-top: 6px solid #003366;">
                <h2 style="color: #003366; margin-bottom: 5px; font-weight: 700;">મામલતદાર કચેરી - સુત્રાપાડા</h2>
                <p style="color: #D97706; font-weight: 600; font-size: 14px; margin-bottom: 20px;">શાખા અને એડમિન લૉગિન પોર્ટલ</p>
            </div>
        """, unsafe_allow_html=True)

        CREDENTIALS = {
            "mam-sutra": {"pass": "Paras", "role": "admin", "name": "મુખ્ય એડમિન (Mamlatdar)"},
            "land_branch": {"pass": "land123", "role": "branch", "name": "Land"},
            "general_branch": {"pass": "gen123", "role": "branch", "name": "General"},
            "election_branch": {"pass": "elec123", "role": "branch", "name": "Election"},
            "supply_branch": {"pass": "sup123", "role": "branch", "name": "Supply"},
            "revenue_branch": {"pass": "rev123", "role": "branch", "name": "Revenue"},
            "chitnis_branch": {"pass": "chit123", "role": "branch", "name": "Chitnis"},
            "computer_branch": {"pass": "comp123", "role": "branch", "name": "Computer"}
        }

        with st.form("login_form"):
            username = st.text_input("👤 યુઝરનેમ (Username / Branch ID)")
            password = st.text_input("🔑 પાસવર્ડ (Password)", type="password")
            submit_login = st.form_submit_button("🚀 લૉગિન કરો (Login)", use_container_width=True)

            if submit_login:
                if username in CREDENTIALS and CREDENTIALS[username]["pass"] == password:
                    st.session_state.logged_in = True
                    st.session_state.current_user = CREDENTIALS[username]["name"]
                    st.session_state.user_role = CREDENTIALS[username]["role"]
                    st.success(f"🎉 સ્વાગત છે, {st.session_state.current_user}! સિસ્ટમ લોડ થઈ રહી છે...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ ખોટું યુઝરનેમ અથવા પાસવર્ડ! કૃપા કરીને ફરી પ્રયાસ કરો.")

        st.markdown("""
            <div class="designer-box" style="margin-top: 20px;">
                <div class="designer-text">DESIGNED & DEVELOPED BY</div>
                <div class="designer-name">✨ PARAS BHOLA ✨</div>
            </div>
        """, unsafe_allow_html=True)

else:
    # ડેટાબેઝ અને અન્ય મેનૂ સેટઅપ
    conn = sqlite3.connect("sutrapada_inward.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inward (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tappal_no TEXT, ref_no TEXT, subject TEXT, letter_subject TEXT,
        letter_date TEXT, received_from TEXT, from_office TEXT, to_office TEXT,
        branch TEXT, status TEXT, created_by TEXT, created_on TEXT,
        internal_sender TEXT, external_sender TEXT, entry_date TEXT, remark TEXT, is_read INTEGER DEFAULT 0
    )
    """)
    conn.commit()

    branch_list = ["Land", "General", "Election", "Mamlatdar Office", "Supply", "Magistrate", "Revenue", "Chitnis", "Computer"]

    st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 10px 0;">
        <h3 style="margin: 0; color: #FFFFFF;">🏛️ મામલતદાર કચેરી</h3>
        <p style="margin: 0; font-size: 12px; color: #FF9933;">લૉગ્ડ ઇન: {st.session_state.current_user}</p>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.write("---")

    if st.session_state.user_role == "admin":
        menu = ["🏠 ડેશબોર્ડ", "📝 નવી એન્ટ્રી", "📁 એક્સેલ ઇમ્પોર્ટ", "📅 દૈનિક વર્કલિસ્ટ"]
    else:
        menu = ["📥 શાખા ઇનબૉક્સ", "↗️ ટપાલ ફોરવર્ડ કરો", "📅 શાખા વર્કલિસ્ટ"]

    choice = st.sidebar.radio("મુખ્ય મેનૂ", menu)

    if st.sidebar.button("🚪 લૉગઆઉટ", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    # મુખ્ય સ્ક્રીન કంటೆಂಟ್
    if choice == "🏠 ડેશબોર્ડ":
        st.markdown('<div class="govt-header"><div class="govt-title">🏛️ એડમિન ડેશબોર્ડ</div></div>', unsafe_allow_html=True)
        df = pd.read_sql_query("SELECT * FROM inward", conn)
        st.metric("કુલ ટપાલ", len(df))

    elif choice == "📅 શાખા વર્કલિસ્ટ" and st.session_state.user_role == "branch":
        my_branch = st.session_state.current_user
        st.markdown(f"## 📅 {my_branch} શાખા વર્કલિસ્ટ")
        df = pd.read_sql_query(f"SELECT * FROM inward WHERE branch = '{my_branch}'", conn)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("કોઈ ડેટા ઉપલબ્ધ નથી.")
