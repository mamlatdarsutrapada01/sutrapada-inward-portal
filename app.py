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

st.set_page_config(
    page_title="મામલતદાર કચેરી સુત્રાપાડા - ઈ-ઇનવર્ડ પોર્ટલ",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""
if 'user_role' not in st.session_state:
    st.session_state.user_role = ""

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

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            '<div style="text-align: center; background: #FFFFFF; padding: 30
