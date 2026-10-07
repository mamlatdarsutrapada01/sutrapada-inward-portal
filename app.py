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
        is_read INTEGER DEFAULT 0,
        javak_no TEXT,
        dispatch_date TEXT
    )
    """)

    for col_name in ["ref_no", "external_sender", "is_read", "javak_no", "dispatch_date"]:
        try:
            cursor.execute(f"ALTER TABLE inward ADD COLUMN {col_name} TEXT")
        except sqlite3.OperationalError:
            pass

    conn.commit()

    branch_list = [
        "Land", "General", "Election", "Mamlatdar Office", 
        "Supply", "Magistrate", "Revenue", "Jamin", 
        "Aakani", "Chitnis", "Scheme", "Computer", "Election Branch"
    ]

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

        col_widths = [30, 30, 50, 50, 140, 60, 60, 60, 80, 65, 180]
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
            "↗️ એડમિન ટપાલ ફોરવર્ડ અને જાવક નંબર (Admin Dispatch/Forward)",
            "📅 દૈનિક વર્કલિસ્ટ (Daily Worklist)"
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

    st.sidebar.markdown("""
    <div class="designer-box">
        <div class="designer-text">💻 DESIGNED & DEVELOPED BY</div>
        <div class="designer-name">✨ PARAS BHOLA ✨</div>
    </div>
    """, unsafe_allow_html=True)

    if choice == "🏠 મુખ્ય ડેશબોર્ડ (Dashboard)" and st.session_state.user_role == "admin":
        st.markdown("""
        <div class="govt-header">
            <div class="govt-title">🏛️ મામલતદાર કચેરી - સુત્રાપાડા (એડમિન ડેશબોર્ડ)</div>
            <div class="govt-subtitle">કેન્દ્રીય ટપાલ વ્યવસ્થાપન સિસ્ટમ</div>
        </div>
        """, unsafe_allow_html=True)

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
                status = st.selectbox("સ્થિતિ (Status)", ["Pending", "Working", "Disposed"])
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
                    st.success(f"✅ ટપાલ સફળતાપૂર્વક નોંધીને **[{branch}]** શાખાને મોકલી દેવામાં આવી છે!")
                else:
                    st.error("⚠️ મહેરબાની કરીને ટપાલ નંબર અથવા વિષય દાખલ કરો.")

    elif choice == "📁 એક્સેલ ફાઈલ અપલોડ (Excel Import)" and st.session_state.user_role == "admin":
        st.markdown("<h2 style='color: #003366;'>📁 એક્સેલ (Excel) ફાઈલમાંથી બલ્ક ઇમ્પોર્ટ</h2>", unsafe_allow_html=True)
        st.write("---")
        uploaded_file = st.file_uploader("એક્સેલ ફાઈલ અપલોડ કરો (.xlsx, .xls)", type=["xlsx", "xls"])

        if uploaded_file is not None:
            df_upload = pd.read_excel(uploaded_file)
            st.dataframe(df_upload.head(5), use_container_width=True)
            import_date = st.date_input("🗓 ઇમ્પોર્ટ તારીખ:", date.today())

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
                st.success(f"🎉 કુલ {total_imported} રેકોર્ડ્સ સફળતાપૂર્વક ઇમ્પોર્ટ થઈ ગયા છે!")

    elif choice == "↗️ એડમિન ટપાલ ફોરવર્ડ અને જાવક નંબર (Admin Dispatch/Forward)" and st.session_state.user_role == "admin":
        st.markdown("<h2 style='color: #003366;'>↗️ એડમિન દ્વારા ટપાલ અન્ય શાખામાં ફોરવર્ડ અને જાવક નંબર આપો</h2>", unsafe_allow_html=True)
        st.write("---")

        df_all_tappal = pd.read_sql_query("SELECT * FROM inward ORDER BY id DESC", conn)

        if df_all_tappal.empty:
            st.warning("કોઈ ટપાલ ઉપલબ્ધ નથી.")
        else:
            tappal_options = {f"ID: {row['id']} | ટપાલ નં: {row['tappal_no']} | Ref: {row.get('ref_no','')} | વર્તમાન શાખા: {row['branch']} | વિષય: {str(row['letter_subject'])[:30]}...": row['id'] for _, row in df_all_tappal.iterrows()}
            
            selected_label = st.selectbox("ફોરવર્ડ કરવા માટેની ટપાલ પસંદ કરો:", list(tappal_options.keys()))
            selected_id = tappal_options[selected_label]

            current_tappal_row = df_all_tappal[df_all_tappal["id"] ==
