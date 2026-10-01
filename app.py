import io
import sqlite3
import time
from datetime import date

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# ==========================================
# ૦. પેજ સેટઅપ અને સરકારી બ્લુ થીમ CSS
# ==========================================
st.set_page_config(
    page_title="મામલતદાર કચેરી સુત્રાપાડા - ઈ-ઇનવર્ડ પોર્ટલ",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# === લૉગિન સ્ટેટ મેનેજમેન્ટ ===
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = ""  # 'admin' અથવા 'branch'

# Custom CSS for UI & Designer Credit
st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)

# ==========================================
# 🔐 લૉગિન પેજ (BRANCH & ADMIN LOGIN)
# ==========================================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="text-align: center; background: #FFFFFF; padding: 30px; border-radius: 12px; box-shadow: 0 6px 20px rgba(0,51,102,0.15); border-top: 6px solid #003366;">
                <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" width="90" style="margin-bottom: 10px;">
                <h2 style="color: #003366; margin-bottom: 5px; font-weight: 700;">મામલતદાર કચેરી - સુત્રાપાડા</h2>
                <p style="color: #D97706; font-weight: 600; font-size: 14px; margin-bottom: 20px;">શાખા અને એડમિન લૉગિન પોર્ટલ</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

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
                    st.session_state.branch_username = username
                    st.success(f"🎉 સ્વાગત છે, {st.session_state.current_user}! સિસ્ટમ લોડ થઈ રહી છે...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ ખોટું યુઝરનેમ અથવા પાસવર્ડ! કૃપા કરીને ફરી પ્રયાસ કરો.")

        st.markdown(
            """
            <div class="designer-box" style="margin-top: 20px;">
                <div class="designer-text">DESIGNED & DEVELOPED BY</div>
                <div class="designer-name">✨ PARAS BHOLA ✨</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

else:
    if "first_load" not in st.session_state:
        st.session_state.first_load = True

    if st.session_state.first_load:
        placeholder = st.empty()
        with placeholder.container():
            st.markdown(
                f"""
                <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 85vh; text-align: center; background: linear-gradient(135deg, #F0F4F8 0%, #D9E2EC 100%); border-radius: 15px; padding: 20px;">
                    <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" width="130" style="margin-bottom: 15px;">
                    <h1 style="color: #003366; font-size: 34px; font-weight: 700; margin-bottom: 5px;">🏛️ મામલતદાર કચેરી - સુત્રાપાડા</h1>
                    <h3 style="color: #D97706; font-size: 20px; font-weight: 600; margin-top: 0;">લોગ્ડ ઇન યુઝર: {st.session_state.current_user}</h3>
                    <div style="margin: 20px 0;"><img src="https://i.gifer.com/ZZ5H.gif" width="55"></div>
                    <p style="color: #475569; font-size: 15px;">ડેશબોર્ડ તૈયાર થઈ રહ્યું છે...</p>
                </div>
            """,
                unsafe_allow_html=True,
            )
            time.sleep(2)
        placeholder.empty()
        st.session_state.first_load = False

    # ૦. ડેટાબેઝ સેટઅપ અને ઓટો-માઈગ્રેશન
    conn = sqlite3.connect("sutrapada_inward.db", check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inward (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tappal_no TEXT,
        ref_no TEXT,
        subject TEXT,
        letter_subject TEXT,
        letter_date TEXT,
        received_from TEXT,
        from_office TEXT,
        to_office TEXT,
        branch TEXT,
        status TEXT,
        created_by TEXT,
        created_on TEXT,
        internal_sender TEXT,
        external_sender TEXT,
        entry_date TEXT,
        remark TEXT,
        is_read INTEGER DEFAULT 0
    )
    """)

    # ઓટો-માઈગ્રેશન: જો ખૂટતી કૉલમ હોય તો ઉમેરો
    try:
        cursor.execute("ALTER TABLE inward ADD COLUMN ref_no TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE inward ADD COLUMN external_sender TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE inward ADD COLUMN is_read INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    conn.commit()

    # અધિકૃત શાખાઓની યાદી
    branch_list = [
        "Land",
        "General",
        "Election",
        "Mamlatdar Office",
        "Supply",
        "Magistrate",
        "Revenue",
        "Jamin",
        "Aakani",
        "Chitnis",
        "Scheme",
        "Computer",
        "Election Branch",
    ]

    # PDF જનરેશન ફંકશન
    def generate_pdf(dataframe, title_text):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=10, leftMargin=10, topMargin=10, bottomMargin=10)
        elements = []
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"], fontSize=12, alignment=1, spaceAfter=8, textColor=colors.HexColor("#003366"))
        cell_style = ParagraphStyle("CellStyle", parent=styles["Normal"], fontSize=7, leading=9)

        elements.append(Paragraph(title_text, title_style))
        elements.append(Spacer(1, 6))

        data = [[Paragraph(f"<b>{col}</b>", cell_style) for col in dataframe.columns]]
        for _, row in dataframe.iterrows():
            data.append([Paragraph(str(val if pd.notna(val) else ""), cell_style) for val in row])

        col_widths = [30, 30, 60, 160, 60, 60, 60, 80, 65, 230]
        table = Table(data, colWidths=col_widths, repeatRows=1, rowHeights=[20] + [40] * (len(data) - 1))
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#003366")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ]))

        elements.append(table)
        doc.build(elements)
        buffer.seek(0)
        return buffer

    # સાઈડબાર મેનૂ
    st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 10px 0;">
        <h3 style="margin: 0; color: #FFFFFF;">🏛️ મામલતદાર કચેરી</h3>
        <p style="margin: 0; font-size: 12px; color: #FF9933;">લૉગ્ડ ઇન: {st.session_state.current_user}</p>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.write("---")

    if st.session_state.user_role == "admin":
        menu = [
            "🏠 મુખ્ય ડેશબોર્ડ (Dashboard)",
            "📝 નવી એન્ટ્રી નોંધણી (New Entry)",
            "📁 એક્સેલ ફાઈલ અપલોડ (Excel Import)",
            "📅 દૈનિક વર્કલિસ્ટ (Daily Worklist)",
        ]
    else:
        menu = [
            "📥 મારી શાખાની ટપાલ / પોપ-અપ (Branch Inbox)",
            "↗️ ટપાલ અન્ય શાખામાં ફોરવર્ડ કરો (Forward Tappal)",
            "📅 શાખા વર્કલિસ્ટ (Branch Worklist)"
        ]

    choice = st.sidebar.radio("મુખ્ય મેનૂ", menu)

    st.sidebar.write("---")
    if st.sidebar.button("🚪 લૉગઆઉટ (Logout)", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.session_state.user_role = ""
        st.rerun()

    st.sidebar.markdown(
        """
    <div class="designer-box">
        <div class="designer-text">💻 DESIGNED & DEVELOPED BY</div>
        <div class="designer-name">✨ PARAS BHOLA ✨</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ==========================================
    # 🏠 ૧. એડમિન ડેશબોર્ડ (ADMIN DASHBOARD)
    # ==========================================
    if choice == "🏠 મુખ્ય ડેશબોર્ડ (Dashboard)" and st.session_state.user_role == "admin":
        st.markdown(
            """
        <div class="govt-header">
            <div class="govt-title">🏛️ મામલતદાર કચેરી - સુત્રાપાડા (એડમિન ડેશબોર્ડ)</div>
            <div class="govt-subtitle">કેન્દ્રીય ટપાલ વ્યવસ્થાપન સિસ્ટમ</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        df_all = pd.read_sql_query("SELECT * FROM inward", conn)
        today_str = str(date.today())

        total_inward = len(df_all)
        today_inward = len(df_all[df_all["entry_date"] == today_str]) if not df_all.empty else 0
        pending_count = len(df_all[df_all["status"].str.lower() == "pending"]) if not df_all.empty else 0
        disposed_count = len(df_all[df_all["status"].str.lower() == "disposed"]) if not df_all.empty else 0

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="stat-card"><div class="stat-title">કુલ ઇનવર્ડ ટપાલ</div><div class="stat-value">{total_inward}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-card" style="border-top-color: #0284C7;"><div class="stat-title">આજની નવી આવક</div><div class="stat-value" style="color: #0284C7 !important;">{today_inward}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="stat-card" style="border-top-color: #D97706;"><div class="stat-title">પેન્ડિંગ કાર્યવાહી</div><div class="stat-value" style="color: #D97706 !important;">{pending_count}</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="stat-card" style="border-top-color: #16A34A;"><div class="stat-title">નિકાલ થયેલ ટપાલ</div><div class="stat-value" style="color: #16A34A !important;">{disposed_count}</div></div>', unsafe_allow_html=True)

        st.write("<br>", unsafe_allow_html=True)
        col_chart, col_recent = st.columns([1.2, 1])
        with col_chart:
            st.subheader("📊 શાખા વાઈઝ ટપાલ વર્ગીકરણ")
            if not df_all.empty and "branch" in df_all.columns:
                st.bar_chart(df_all["branch"].value_counts(), color="#003366")
            else:
                st.info("ડેટાબેઝમાં કોઈ રેકોર્ડ નથી.")
        with col_recent:
            st.subheader("🕒 છેલ્લી ૫ નોંધાયેલી એન્ટ્રીઓ")
            if not df_all.empty:
                df_recent = df_all.tail(5)[["id", "tappal_no", "letter_subject", "branch", "entry_date"]].sort_values(by="id", ascending=False)
                df_recent.columns = ["ID", "તપાલ નં.", "વિષય", "શાખા", "તારીખ"]
                st.dataframe(df_recent, use_container_width=True, hide_index=True)

    # ==========================================
    # 📝 ૨. નવી એન્ટ્રી નોંધણી (NEW ENTRY) + POPUP TRIGGER
    # ==========================================
    elif choice == "📝 નવી એન્ટ્રી નોંધણી (New Entry)" and st.session_state.user_role == "admin":
        st.markdown("<h2 style='color: #003366;'>📝 નવી તપાલ/અરજી નોંધણી અને શાખા ફાળવણી</h2>", unsafe_allow_html=True)
        st.write("---")

        with st.form("manual_entry_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                tappal_no = st.text_input("ટપાલ નંબર (Tappal No)*")
                ref_no = st.text_input("સંદર્ભ નંબર / ઈ-સરકાર નંબર (Ref No / e-Sarkar No)")
                entry_date = st.date_input("આવક તારીખ", date.today())
                branch = st.selectbox("કઈ શાખાને મોકલવાની છે? (Target Branch)*", branch_list)
            with col2:
                internal_sender = st.text_input("આંતરિક મોકલનાર (Internal Sender)")
                external_sender = st.text_input("બાહ્ય મોકલનાર (External Sender)")
                created_by = st.text_input("બનાવનારનું નામ (Created By)", "Paras Bhola")
                status = st.selectbox("સ્થિતિ (Status)", ["Pending", "Disposed"])
            with col3:
                received_from = st.text_input("ક્યાંથી મળેલ છે (Received From)")
                from_office = st.text_input("કઈ કચેરીથી (From Office)")
                to_office = st.text_input("કઈ કચેરીને (To Office)", "Sutrapada Mamlatdar Office")

            subject = st.text_input("વિષય (Subject)")
            letter_subject = st.text_area("પત્રનો વિગતવાર વિષય (Letter Subject)*")
            remark = st.text_area("રીમાર્ક (Remark)")

            submit = st.form_submit_button("💾 સેવ કરો અને શાખાને મોકલો (Save & Notify Branch)")

            if submit:
                if tappal_no or letter_subject:
                    cursor.execute("""
                    INSERT INTO inward (
                        tappal_no, ref_no, subject, letter_subject, letter_date, 
                        received_from, from_office, to_office, branch, status, 
                        created_by, created_on, internal_sender, external_sender, entry_date, remark, is_read
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                    """, (
                        tappal_no, ref_no, subject, letter_subject, str(entry_date), 
                        received_from, from_office, to_office, branch, status, 
                        created_by, str(entry_date), internal_sender, external_sender, str(entry_date), remark
                    ))
                    conn.commit()
                    st.success(f"✅ ટપાલ સફળતાપૂર્વક નોંધીને **[{branch}]** શાખાને મોકલી દેવામાં આવી છે! તે શાખાના લૉગિનમાં પોપ-અપ નોટિફિકેશન દેખાશે.")
                else:
                    st.error("⚠️ મહેરબાની કરીને ટપાલ નંબર અથવા વિષય દાખલ કરો.")

    # ==========================================
    # 📁 ૩. એક્સેલ ફાઈલ અપલોડ (EXCEL IMPORT)
    # ==========================================
    elif choice == "📁 એક્સેલ ફાઈલ અપલોડ (Excel Import)" and st.session_state.user_role == "admin":
        st.markdown("<h2 style='color: #003366;'>📁 એક્સેલ (Excel) ફાઈલમાંથી બલ્ક ઇમ્પોર્ટ</h2>", unsafe_allow_html=True)
        st.write("---")
        uploaded_file = st.file_uploader("એક્સેલ ફાઈલ અપલોડ કરો (.xlsx, .xls)", type=["xlsx", "xls"])

        if uploaded_file is not None:
            df_upload = pd.read_excel(uploaded_file)
            st.dataframe(df_upload.head(5), use_container_width=True)
            import_date = st.date_input("🗓️ ઇમ્પોર્ટ તારીખ:", date.today())

            if st.button("🚀 ડેટાબેઝમાં સાચવો (Import Data)"):
                total_imported = 0
                for _, row in df_upload.iterrows():
                    tappal_no = str(row.get("tappalnumber", row.get("tappal_no", "T-00")))
                    branch = str(row.get("To Branch", row.get("branch", "General")))
                    letter_subject = str(row.get("Letter Subject", row.get("letter_subject", "No Subject")))
                    ref_no = str(row.get("ref_no", ""))
                    sender = str(row.get("external_sender", row.get("Received From", "")))
                    
                    cursor.execute("""
                    INSERT INTO inward (
                        tappal_no, ref_no, letter_subject, branch, status, entry_date, external_sender, is_read
                    ) VALUES (?, ?, ?, ?, 'Pending', ?, ?, 0)
                    """, (tappal_no, ref_no, letter_subject, branch, str(import_date), sender))
                    total_imported += 1
                conn.commit()
                st.success(f"🎉 કુલ {total_imported} રેકોર્ડ્સ સફળતાપૂર્વક ઇમ્પોર્ટ થઈ ગયા છે અને સંબંધિત શાખાઓને મોકલી દેવાયા છે!")

    # ==========================================
    # 📅 ૪. દૈનિક વર્કલિસ્ટ (DAILY WORKLIST - ADMIN)
    # ==========================================
    elif choice == "📅 દૈનિક વર્કલિસ્ટ (Daily Worklist)" and st.session_state.user_role == "admin":
        st.markdown("<h2 style='color: #003366;'>📅 દૈનિક ટપાલ વર્કલિસ્ટ અને પ્રિન્ટ</h2>", unsafe_allow_html=True)
        st.write("---")
        df_all = pd.read_sql_query("SELECT * FROM inward ORDER BY id ASC", conn)

        if df_all.empty:
            st.warning("કોઈ રેકોર્ડ ઉપલબ્ધ નથી.")
        else:
            df_all["office_sr_no"] = df_all["id"]
            selected_date = st.date_input("🗓️ તારીખ પસંદ કરો:", date.today())
            df_filtered = df_all[df_all["entry_date"] == str(selected_date)]

            if df_filtered.empty:
                st.info("આ તારીખ માટે કોઈ ટપાલ નથી.")
            else:
                st.dataframe(df_filtered[["id", "tappal_no", "branch", "letter_subject", "status"]], use_container_width=True)

    # ==========================================
    # 📥 ૫. શાખા માટે ઇનબૉક્સ અને પોપ-અપ નોટિફિકેશન (BRANCH INBOX)
    # ==========================================
    elif st.session_state.user_role == "branch":
        my_branch = st.session_state.current_user

        if choice == "📥 મારી શાખાની ટપાલ / પોપ-અપ (Branch Inbox)":
            st.markdown(f"<h2 style='color: #003366;'>📥 {my_branch} શાખાનું ઇનબૉક્સ અને નવી ટપાલ એલર્ટ</h2>", unsafe_allow_html=True)
            st.write("---")

            cursor.execute("SELECT id, tappal_no, letter_subject, entry_date, external_sender FROM inward WHERE branch = ? AND is_read = 0", (my_branch,))
            unread_tappals = cursor.fetchall()

            if unread_tappals:
                st.markdown(f"""
                <div style="background-color: #FEF3C7; border: 2px solid #D97706; padding: 20px; border-radius: 10px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(217,119,6,0.3);">
                    <h3 style="color: #92400E; margin-top: 0; display: flex; align-items: center;">
                        🚨 એલર્ટ: તમને નવી ટપાલ પ્રાપ્ત થઈ છે! ({len(unread_tappals)} નવી ટપાલ)
                    </h3>
                    <p style="color: #B45309; font-weight: 600;">કચેરીમાંથી અથવા અન્ય શાખામાંથી આપની શાખા માટે નીચે મુજબની નવી ટપાલો મોકલવામાં આવી છે:</p>
                </div>
                """, unsafe_allow_html=True)

                for t_id, t_no, t_sub, t_date, t_sender in unread_tappals:
                    st.info(f"📌 **ટપાલ નં:** {t_no} | **તારીખ:** {t_date} | **મોકલનાર:** {t_sender} \n\n 📝 **વિષય:** {t_sub}")

                if st.button("✅ બધી નવી ટપાલો વાંચી લીધી છે (Mark as Read)"):
                    cursor.execute("UPDATE inward SET is_read = 1 WHERE branch = ? AND is_read = 0", (my_branch,))
                    conn.commit()
                    st.success("તમામ નવી ટપાલો વાંચેલી તરીકે નોંધી લેવામાં આવી છે!")
                    time.sleep(1)
                    st.rerun()

            st.write("---")
            st.subheader(f"📋 {my_branch} શાખાની તમામ ટપાલોની યાદી")
            df_branch = pd.read_sql_query(f"SELECT * FROM inward WHERE branch = '{my_branch}' ORDER BY id DESC", conn)

            if df_branch.empty:
                st.info("હજુ સુધી આપની શાખામાં કોઈ ટપાલ આવી નથી.")
            else:
                st.dataframe(df_branch[["id", "tappal_no", "letter_subject", "entry_date", "status", "remark"]], use_container_width=True)

        # ==========================================
        # ↗️️ ૬. શાખામાંથી અન્ય શાખામાં ટપાલ ફોરવર્ડ કરો
        # ==========================================
        elif choice == "↗️ ટપાલ અન્ય શાખામાં ફોરવર્ડ કરો (Forward Tappal)":
            st.markdown(f"<h2 style='color: #003366;'>↗️ ટપાલ અન્ય શાખામાં ફોરવર્ડ કરો ({my_branch} Branch)</h2>", unsafe_allow_html=True)
            st.write("---")

            df_branch = pd.read_sql_query(f"SELECT * FROM inward WHERE branch = '{my_branch}' ORDER BY id DESC", conn)

            if df_branch.empty:
                st.warning("તમારી શાખામાં ફોરવર્ડ કરવા માટે કોઈ ટપાલ ઉપલબ્ધ નથી.")
            else:
                tappal_options = {f"ટપાલ નં: {row['tappal_no']} - {row['letter_subject'][:40]}... (ID: {row['id']})": row['id'] for _, row in df_branch.iterrows()}
                
                selected_tappal_label = st.selectbox("ફોરવર્ડ કરવા માટેની ટપાલ પસંદ કરો (Select Tappal):", list(tappal_options.keys()))
                selected_tappal_id = tappal_options[selected_tappal_label]

                other_branches = [b for b in branch_list if b != my_branch]
                target_branch = st.selectbox("કઈ શાખામાં ફોરવર્ડ કરવી છે? (Target Branch):", other_branches)
                
                forward_remark = st.text_area("ફોરવર્ડ કરવાનું કારણ / રીમાર્ક (Forwarding Remark):", f"Forwarded from {my_branch} branch.")

                if st.button("🚀 ટપાલ ફોરવર્ડ કરો (Forward Now)"):
                    cursor.execute("""
                    UPDATE inward 
                    SET branch = ?, remark = ?, is_read = 0 
                    WHERE id = ?
                    """, (target_branch, forward_remark, selected_tappal_id))
                    conn.commit()
                    
                    st.success(f"✅ ટપાલ સફળતાપૂર્વક **[{target_branch}]** શાખામાં ફોરવર્ડ કરી દેવામાં આવી છે! હવે તે શાખાના લૉગિનમાં એલર્ટ દેખાશે.")
                    time.sleep(1.5)
                    st.rerun()

        elif choice == "📅 શાખા વર્કલિસ્ટ (Branch Worklist)":
            st.markdown(f"<h2 style='color: #003366;'>📅 {my_branch} શાખાનું દૈનિક વર્કલિસ્ટ અને પ્રિન્ટ</h2>", unsafe_allow_html=True)
            st.write("---")
            df_branch = pd.read_sql_query(f"SELECT * FROM inward WHERE branch = '{my_branch}' ORDER BY id DESC", conn)
            
            if not df_branch.empty:
                selected_date = st.date_input("🗓️ તારીખ પસંદ કરો:", date.today())
                df_filtered = df_branch[df_branch["entry_date"] == str(selected_date)]
                if not df_filtered.empty:
                    st.dataframe(df_filtered[["id", "tappal_no", "letter_subject", "status"]], use_container_width=True)
                    
                    pdf_buffer = generate_pdf(df_filtered[["id", "tappal_no", "letter_subject", "status"]], f"{my_branch} Branch Worklist")
                    st.download_button(
                        label="📥 PDF ડાઉનલોડ કરો",
                        data=pdf_buffer,
                        file_name=f"{my_branch}_Worklist.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.info("આ તારીખે કોઈ ટપાલ નથી.")
            else:
                st.info("કોઈ રેકોર્ડ નથી.")
