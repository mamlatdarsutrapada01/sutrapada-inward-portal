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

    /* Paras Bhola Branding Box */
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
# 🔐 લૉગિન પેજ (LOGIN PAGE)
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
                <p style="color: #D97706; font-weight: 600; font-size: 14px; margin-bottom: 20px;">ઈ-ઇનવર્ડ અને ટપાલ મેનેજમેન્ટ પોર્ટલ</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            username = st.text_input("👤 યુઝરનેમ (Username)")
            password = st.text_input("🔑 પાસવર્ડ (Password)", type="password")
            submit_login = st.form_submit_button(
                "🚀 લૉગિન કરો (Login)", use_container_width=True
            )

            if submit_login:
                if username == "mam-sutra" and password == "Paras":
                    st.session_state.logged_in = True
                    st.success("🎉 લૉગિન સફળ! સિસ્ટમ લોડ થઈ રહી છે...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(
                        "❌ ખોટું યુઝરનેમ અથવા પાસવર્ડ! કૃપા કરીને ફરી પ્રયાસ કરો."
                    )

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
                """
                <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 85vh; text-align: center; background: linear-gradient(135deg, #F0F4F8 0%, #D9E2EC 100%); border-radius: 15px; padding: 20px;">
                    <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" width="130" style="animation: bounce 1.8s infinite; margin-bottom: 15px; filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.2));">
                    <h1 style="color: #003366; font-family: 'Noto Sans Gujarati', sans-serif; font-size: 34px; font-weight: 700; margin-bottom: 5px;">🏛️ મામલતદાર કચેરી - સુત્રાપાડા</h1>
                    <h3 style="color: #D97706; font-family: 'Noto Sans Gujarati', sans-serif; font-size: 20px; font-weight: 600; margin-top: 0;">ઇ-ઇનવર્ડ અને ટપાલ મેનેજમેન્ટ પોર્ટલ</h3>
                    <div style="margin: 20px 0;">
                        <img src="https://i.gifer.com/ZZ5H.gif" width="55">
                    </div>
                    <p style="color: #475569; font-size: 15px; font-weight: 500; letter-spacing: 0.5px;">સિસ્ટમ લોડ થઈ રહી છે, કૃપા કરીને રાહ જુઓ...</p>
                    <div style="margin-top: 30px; background: linear-gradient(135deg, #FF9933 0%, #D97706 100%); padding: 10px 25px; border-radius: 30px; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
                        <span style="color: #FFFFFF; font-size: 12px; letter-spacing: 1px; text-transform: uppercase; display: block;">Designed & Developed By</span>
                        <span style="color: #FFFFFF; font-size: 16px; font-weight: 700; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">✨ PARAS BHOLA ✨</span>
                    </div>
                </div>
                <style>
                    @keyframes bounce {
                        0%, 20%, 50%, 80%, 100% {transform: translateY(0);}
                        40% {transform: translateY(-12px);}
                        60% {transform: translateY(-6px);}
                    }
                </style>
            """,
                unsafe_allow_html=True,
            )
            time.sleep(2.5)
        placeholder.empty()
        st.session_state.first_load = False

    # ૦. ડેટાબેઝ સેટઅપ
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
        remark TEXT
    )
    """)
    conn.commit()

    # અધિકૃત શાખાઓની યાદી (ડ્રોપડાઉન માટે)
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
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=10,
            leftMargin=10,
            topMargin=10,
            bottomMargin=10,
        )
        elements = []

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Heading1"],
            fontSize=12,
            alignment=1,
            spaceAfter=8,
            textColor=colors.HexColor("#003366"),
        )
        cell_style = ParagraphStyle(
            "CellStyle", parent=styles["Normal"], fontSize=7, leading=9
        )

        elements.append(Paragraph(title_text, title_style))
        elements.append(Spacer(1, 6))

        data = [
            [
                Paragraph(f"<b>{col}</b>", cell_style)
                for col in dataframe.columns
            ]
        ]
        for _, row in dataframe.iterrows():
            data.append([
                Paragraph(str(val if pd.notna(val) else ""), cell_style)
                for val in row
            ])

        col_widths = [30, 30, 60, 160, 60, 60, 60, 80, 65, 230]

        table = Table(
            data,
            colWidths=col_widths,
            repeatRows=1,
            rowHeights=[20] + [40] * (len(data) - 1),
        )
        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#003366")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ])
        )

        elements.append(table)
        doc.build(elements)
        buffer.seek(0)
        return buffer

    # સાઈડબાર મેનૂ
    st.sidebar.markdown(
        """
    <div style="text-align: center; padding: 10px 0;">
        <h3 style="margin: 0; color: #FFFFFF;">🏛️ મામલતદાર કચેરી</h3>
        <p style="margin: 0; font-size: 13px; color: #FF9933;">સુતરાપાડા - ઈ-ઇનવર્ડ પોર્ટલ</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.sidebar.write("---")

    menu = [
        "🏠 મુખ્ય ડેશબોર્ડ (Dashboard)",
        "📝 નવી એન્ટ્રી નોંધણી (New Entry)",
        "📁 એક્સેલ ફાઈલ અપલોડ (Excel Import)",
        "📅 દૈનિક વર્કલિસ્ટ (Daily Worklist)",
    ]
    choice = st.sidebar.radio("મુખ્ય મેનૂ", menu)

    st.sidebar.write("---")

    if st.sidebar.button("🚪 લૉગઆઉટ (Logout)", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    st.sidebar.markdown(
        """
    <div class="designer-box">
        <div class="designer-text">💻 DESIGNED & DEVELOPED BY</div>
        <div class="designer-name">✨ PARAS BHOLA ✨</div>
    </div>
    <p style="text-align: center; font-size: 11px; color: #94A3B8; margin-top: 10px;">
        © 2026 મામલતદાર કચેરી, સુતરાપાડા
    </p>
    """,
        unsafe_allow_html=True,
    )

    # ==========================================
    # ૦. મુખ્ય ડેશબોર્ડ (DASHBOARD)
    # ==========================================
    if choice == "🏠 મુખ્ય ડેશબોર્ડ (Dashboard)":
        st.markdown(
            """
        <div class="govt-header">
            <div class="govt-title">🏛️ મામલતદાર કચેરી - સુત્રાપાડા</div>
            <div class="govt-subtitle">ટપાલ વ્યવસ્થાપન સિસ્ટમ</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        df_all = pd.read_sql_query("SELECT * FROM inward", conn)
        today_str = str(date.today())

        total_inward = len(df_all)
        today_inward = (
            len(df_all[df_all["entry_date"] == today_str])
            if not df_all.empty
            else 0
        )
        pending_count = (
            len(df_all[df_all["status"].str.lower() == "pending"])
            if not df_all.empty
            else 0
        )
        disposed_count = (
            len(df_all[df_all["status"].str.lower() == "disposed"])
            if not df_all.empty
            else 0
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown(
                f"""
            <div class="stat-card">
                <div class="stat-title">કુલ ઇનવર્ડ ટપાલ</div>
                <div class="stat-value">{total_inward}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with c2:
            st.markdown(
                f"""
            <div class="stat-card" style="border-top-color: #0284C7;">
                <div class="stat-title">આજની નવી આવક</div>
                <div class="stat-value" style="color: #0284C7 !important;">{today_inward}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with c3:
            st.markdown(
                f"""
            <div class="stat-card" style="border-top-color: #D97706;">
                <div class="stat-title">પેન્ડિંગ કાર્યવાહી</div>
                <div class="stat-value" style="color: #D97706 !important;">{pending_count}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with c4:
            st.markdown(
                f"""
            <div class="stat-card" style="border-top-color: #16A34A;">
                <div class="stat-title">નિકાલ થયેલ ટપાલ</div>
                <div class="stat-value" style="color: #16A34A !important;">{disposed_count}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.write("<br>", unsafe_allow_html=True)

        col_chart, col_recent = st.columns([1.2, 1])

        with col_chart:
            st.subheader("📊 શાખા વાઈઝ ટપાલ વર્ગીકરણ")
            if not df_all.empty and "branch" in df_all.columns:
                branch_counts = df_all["branch"].value_counts()
                st.bar_chart(branch_counts, color="#003366")
            else:
                st.info("ડેટાબેઝમાં હજુ સુધી કોઈ રેકોર્ડ ઉપલબ્ધ નથી.")

        with col_recent:
            st.subheader("🕒 છેલ્લી ૫ નોંધાયેલી એન્ટ્રીઓ")
            if not df_all.empty:
                df_recent = df_all.tail(5)[
                    [
                        "id",
                        "tappal_no",
                        "letter_subject",
                        "branch",
                        "entry_date",
                    ]
                ].sort_values(by="id", ascending=False)
                df_recent.columns = ["ID", "તપાલ નં.", "વિષય", "શાખા", "તારીખ"]
                st.dataframe(df_recent, use_container_width=True, hide_index=True)
            else:
                st.info("કોઈ તાજેતરની એન્ટ્રીઓ નથી.")

    # ==========================================
    # ૧. નવી એન્ટ્રી નોંધણી (શાખા ડ્રોપડાઉન સાથે)
    # ==========================================
    elif choice == "📝 નવી એન્ટ્રી નોંધણી (New Entry)":
        st.markdown(
            "<h2 style='color: #003366;'>📝 નવી તપાલ/અરજી નોંધણી ફોર્મ</h2>",
            unsafe_allow_html=True,
        )
        st.write("---")

        with st.form("manual_entry_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                tappal_no = st.text_input("ટપાલ નંબર (Tappal No)*")
                ref_no = st.text_input("સંદર્ભ નંબર / ઈ-સરકાર નંબર (Ref No)")
                entry_date = st.date_input("આવક તારીખ", date.today())
                branch = st.selectbox("શાખા (Branch)", branch_list)
            with col2:
                internal_sender = st.text_input(
                    "આંતરિક મોકલનાર (Internal Sender)"
                )
                external_sender = st.text_input(
                    "બાહ્ય મોકલનાર (External Sender)"
                )
                created_by = st.text_input(
                    "બનાવનારનું નામ (Created By)", "Paras Bhola"
                )
                status = st.selectbox(
                    "સ્થિતિ (Status)", ["Pending", "Disposed", "Add"]
                )
            with col3:
                received_from = st.text_input("ક્યાંથી મળેલ છે (Received From)")
                from_office = st.text_input("કઈ કચેરીથી (From Office)")
                to_office = st.text_input(
                    "કઈ કચેરીને (To Office)", "Sutrapada Mamlatdar Office"
                )

            subject = st.text_input("વિષય (Subject)")
            letter_subject = st.text_area(
                "પત્રનો વિગતવાર વિષય (Letter Subject)*"
            )
            remark = st.text_area("રીમાર્ક (Remark)")

            submit = st.form_submit_button("💾 સેવ કરો (Save Entry)")

            if submit:
                if tappal_no or letter_subject:
                    # ચકાસો કે આ ટપાલ નંબર કે રેફરન્સ નંબર પહેલેથી અજ્ઞાત છે કે નહીં
                    cursor.execute(
                        "SELECT status FROM inward WHERE tappal_no = ? OR ref_no = ?",
                        (tappal_no, ref_no),
                    )
                    existing = cursor.fetchone()

                    if existing:
                        st.warning(
                            f"⚠️ આ ટપાલ / ઈ-સરકાર નંબર પહેલેથી ડેટાબેઝમાં નોંધાયેલ છે! તેની વર્તમાન સ્થિતિ (Status): **{existing[0]}** છે."
                        )
                    else:
                        cursor.execute(
                            """
                        INSERT INTO inward (
                            tappal_no, ref_no, subject, letter_subject, letter_date, 
                            received_from, from_office, to_office, branch, status, 
                            created_by, created_on, internal_sender, external_sender, entry_date, remark
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                            (
                                tappal_no,
                                ref_no,
                                subject,
                                letter_subject,
                                str(entry_date),
                                received_from,
                                from_office,
                                to_office,
                                branch,
                                status,
                                created_by,
                                str(entry_date),
                                internal_sender,
                                external_sender,
                                str(entry_date),
                                remark,
                            ),
                        )
                        conn.commit()
                        st.success(
                            f"✅ ટપાલ નંબર '{tappal_no}' રેકોર્ડમાં સફળતાપૂર્વક ઉમેરાઈ ગઈ છે!"
                        )
                else:
                    st.error(
                        "⚠️ મહેરબાની કરીને ટપાલ નંબર અથવા પત્રનો વિષય દાખલ કરો."
                    )

    # ==========================================
    # ૨. EXCEL ફાઈલ અપલોડ (डुપ્લિકેટ અને સ્ટેટસ ચેકિંગ સાથે)
    # ==========================================
    elif choice == "📁 એક્સેલ ફાઈલ અપલોડ (Excel Import)":
        st.markdown(
            "<h2 style='color: #003366;'>📁 એક્સેલ (Excel) ફાઈલમાંથી બલ્ક ઇમ્પોર્ટ</h2>",
            unsafe_allow_html=True,
        )
        st.write("---")

        uploaded_file = st.file_uploader(
            "એક્સેલ ફાઈલ અપલોડ કરો (.xlsx, .xls)", type=["xlsx", "xls"]
        )

        if uploaded_file is not None:
            try:
                df_upload = pd.read_excel(uploaded_file)
                st.write("📋 **અપલોડ ડેટા પૂર્વાવલોકન (Preview):**")
                st.dataframe(df_upload.head(5), use_container_width=True)

                import_date = st.date_input("🗓️ ઇમ્પોર્ટ તારીખ:", date.today())

                if st.button("🚀 ડેટાબેઝમાં સાચવો (Import Data)"):
                    new_count = 0
                    duplicate_count = 0
                    today_str = str(import_date)

                    for _, row in df_upload.iterrows():
                        created_on_val = (
                            str(row.get("Created On", ""))
                            if pd.notna(row.get("Created On"))
                            else ""
                        )

                        tappal_no = (
                            str(row.get("tappalnumber", ""))
                            if pd.notna(row.get("tappalnumber"))
                            else ""
                        )
                        ref_no = (
                            str(row.get("Reference Number", ""))
                            if pd.notna(row.get("Reference Number"))
                            else ""
                        )
                        subject = (
                            str(row.get("subject", ""))
                            if pd.notna(row.get("subject"))
                            else ""
                        )
                        letter_subject = (
                            str(row.get("Letter Subject", ""))
                            if pd.notna(row.get("Letter Subject"))
                            else ""
                        )
                        letter_date = (
                            str(row.get("Letter Date", ""))
                            if pd.notna(row.get("Letter Date"))
                            else ""
                        )
                        received_from = (
                            str(row.get("Tappal Received From", ""))
                            if pd.notna(row.get("Tappal Received From"))
                            else ""
                        )
                        from_office = (
                            str(row.get("From Office", ""))
                            if pd.notna(row.get("From Office"))
                            else ""
                        )
                        to_office = (
                            str(row.get("To Office", ""))
                            if pd.notna(row.get("To Office"))
                            else ""
                        )
                        branch = (
                            str(row.get("To Branch", ""))
                            if pd.notna(row.get("To Branch"))
                            else "General"
                        )
                        status = (
                            str(row.get("status", ""))
                            if pd.notna(row.get("status"))
                            else "Pending"
                        )
                        created_by = (
                            str(row.get("Created By", ""))
                            if pd.notna(row.get("Created By"))
                            else "Paras Bhola"
                        )
                        created_on = created_on_val
                        internal_sender = (
                            str(row.get("Internal Sender Name", ""))
                            if pd.notna(row.get("Internal Sender Name"))
                            else ""
                        )
                        external_sender = (
                            str(row.get("External Sender Name", ""))
                            if pd.notna(row.get("External Sender Name"))
                            else ""
                        )
                        remark = (
                            str(row.get("REMARK", ""))
                            if pd.notna(row.get("REMARK"))
                            else ""
                        )

                        # ચકાસો કે આ ટપાલ અથવા ઈ-સરકાર રેફરન્સ નંબર પહેલેથી છે કે નહીં
                        cursor.execute(
                            "SELECT status FROM inward WHERE tappal_no = ? OR ref_no = ?",
                            (tappal_no, ref_no),
                        )
                        existing_rec = cursor.fetchone()

                        if existing_rec:
                            duplicate_count += 1
                            # જો ડુપ્લિકેટ હોય તો રિમાર્ક અથવા સ્ટેટસ અપડેટ કરી શકાય અથવા અલગથી નોંધી શકાય
                            st.info(
                                f"ℹ️ ટપાલ નં: {tappal_no} / Ref: {ref_no} પહેલેથી હાજર છે. (Status: {existing_rec[0]})"
                            )
                        else:
                            cursor.execute(
                                """
                            INSERT INTO inward (
                                tappal_no, ref_no, subject, letter_subject, letter_date, 
                                received_from, from_office, to_office, branch, status, 
                                created_by, created_on, internal_sender, external_sender, entry_date, remark
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                                (
                                    tappal_no,
                                    ref_no,
                                    subject,
                                    letter_subject,
                                    letter_date,
                                    received_from,
                                    from_office,
                                    to_office,
                                    branch,
                                    status,
                                    created_by,
                                    created_on,
                                    internal_sender,
                                    external_sender,
                                    today_str,
                                    remark,
                                ),
                            )
                            new_count += 1

                    conn.commit()
                    st.success(
                        f"🎉 અપલોડ પૂર્ણ! નવા ઉમેરાયેલા: {new_count}, પહેલેથી હાજર (Duplicate/Existing): {duplicate_count}"
                    )

            except Exception as e:
                st.error(f"❌ પ્રોસેસમાં ક્ષતિ આવી: {e}")

    # ==========================================
    # ૩. DAILY WORKLIST
    # ==========================================
    elif choice == "📅 દૈનિક વર્કલિસ્ટ (Daily Worklist)":
        st.markdown(
            "<h2 style='color: #003366;'>📅 દૈનિક ટપાલ વર્કલિસ્ટ, ડાઉનલોડ અને પ્રિન્ટ</h2>",
            unsafe_allow_html=True,
        )
        st.write("---")

        df_all = pd.read_sql_query("SELECT * FROM inward ORDER BY id ASC", conn)

        if df_all.empty:
            st.warning("હજુ સુધી કોઈ રેકોર્ડ ઉપલબ્ધ નથી.")
        else:
            df_all["office_sr_no"] = df_all["id"]

            df_all["date_created"] = pd.to_datetime(
                df_all["created_on"], errors="coerce"
            ).dt.strftime("%Y-%m-%d")
            df_all["date_created"] = df_all["date_created"].fillna(
                pd.to_datetime(
                    df_all["entry_date"], errors="coerce"
                ).dt.strftime("%Y-%m-%d")
            )
            df_all["date_entry_clean"] = pd.to_datetime(
                df_all["entry_date"], errors="coerce"
            ).dt.strftime("%Y-%m-%d")

            c1, c2, c3 = st.columns([1.5, 1.2, 1.5])

            with c1:
                search_type = st.radio(
                    "સર્ચનો પ્રકાર:",
                    ["તારીખ (Entry Date)", "ઈ-સરકાર તારીખ (Created On)"],
                    horizontal=True,
                )

                if search_type == "તારીખ (Entry Date)":
                    selected_date = st.date_input(
                        "🗓️ તારીખ પસંદ કરો:", date.today()
                    )
                    selected_date_str = str(selected_date)
                    df_filtered = df_all[
                        df_all["date_entry_clean"] == selected_date_str
                    ]
                    date_display = f"{selected_date_str} (તારીખ વાઈઝ)"
                else:
                    available_created_dates = sorted(
                        [
                            d
                            for d in df_all["date_created"].unique()
                            if d and str(d) != "nan"
                        ],
                        reverse=True,
                    )

                    if available_created_dates:
                        selected_created_date = st.selectbox(
                            "📌 બનાવ્યા તારીખ પસંદ કરો:",
                            available_created_dates,
                        )
                        df_filtered = df_all[
                            df_all["date_created"] == selected_created_date
                        ]
                        date_display = (
                            f"{selected_created_date} (બનાવ્યા તારીખ વાઈઝ)"
                        )
                    else:
                        st.info("કોઈ બનાવ્યા તારીખ મળી નથી.")
                        df_filtered = pd.DataFrame()
                        date_display = "N/A"

            with c2:
                branches = ["બધી શાખાઓ (All Branches)"] + [
                    b for b in df_all["branch"].unique() if b
                ]
                selected_branch = st.selectbox(
                    "📌 શાખા વાઈઝ પસંદ કરો:", branches
                )

            with c3:
                search_subject = st.text_input(
                    "🔍 વિષય શોધો (Subject Search):",
                    placeholder="વિષયના શબ્દો લખો...",
                )

            if selected_branch != "બધી શાખાઓ (All Branches)":
                df_filtered = df_filtered[
                    df_filtered["branch"] == selected_branch
                ]

            if search_subject.strip():
                df_filtered = df_filtered[
                    df_filtered["letter_subject"]
                    .fillna("")
                    .str.contains(search_subject, case=False, regex=False)
                    | df_filtered["subject"]
                    .fillna("")
                    .str.contains(search_subject, case=False, regex=False)
                ]

            if df_filtered.empty:
                st.info("ℹ️ દર્શાવેલ ફિલ્ટર મુજબ કોઈ ડેટા મળ્યો નથી.")
            else:
                df_filtered = df_filtered.reset_index(drop=True)
                df_filtered["branch_sr_no"] = (
                    df_filtered.groupby("branch").cumcount() + 1
                )
                df_filtered["handwritten_date"] = ""

                print_columns = {
                    "branch_sr_no": "શાખા ક્રમ",
                    "office_sr_no": "ઓફિસ ક્રમ",
                    "tappal_no": "ટપાલ નંબર",
                    "letter_subject": "પત્રનો વિષય",
                    "branch": "શાખા",
                    "created_on": "ઈ-સરકાર તારીખ",
                    "entry_date": "તારીખ",
                    "external_sender": "મોકલનાર",
                    "handwritten_date": "તારીખ (ખાલી)",
                    "remark": "રીમાર્ક",
                }

                df_print = df_filtered[list(print_columns.keys())].rename(
                    columns=print_columns
                )

                st.write(
                    f"### 📄 **વર્કલિસ્ટ - {date_display} (કુલ ટપાલ: {len(df_print)})**"
                )
                st.dataframe(df_print, use_container_width=True)

                st.write("---")
                st.subheader("🖨️ ડાઉનલોડ અને પ્રિન્ટ વિકલ્પો")

                col_btn1, col_btn2 = st.columns(2)

                with col_btn1:
                    pdf_buffer = generate_pdf(
                        df_print,
                        f"Mamlatdar Office Sutrapada - Worklist ({date_display})",
                    )
                    st.download_button(
                        label="📥 PDF ફાઈલ ડાઉનલોડ કરો (Download PDF)",
                        data=pdf_buffer,
                        file_name=f"Worklist_{date_display}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

                with col_btn2:
                    html_table = df_print.to_html(
                        classes="styled-table", index=False
                    )
                    
                    print_html_code = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                    <title>મામલતદાર કચેરી સુત્રાપાડા - ટપાલ વર્કલિસ્ટ</title>
                    <style>
                        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Gujarati:wght@400;600;700&display=swap');
                        
                        @page {{
                            size: landscape;
                            margin: 10mm;
                        }}
                        
                        body {{
                            font-family: 'Noto Sans Gujarati', sans-serif;
                            margin: 20px;
                            color: #000;
                            text-align: center;
                        }}
                        h2 {{
                            color: #003366;
                            margin-bottom: 2px;
                            font-size: 20px;
                        }}
                        p {{
                            font-size: 14px;
                            margin-top: 0;
                            color: #555;
                            margin-bottom: 20px;
                        }}
                        table {{
                            width: 100%;
                            border-collapse: collapse;
                            margin-top: 10px;
                            font-size: 11px;
                            text-align: left;
                        }}
                        th, td {{
                            border: 1px solid #003366;
                            padding: 8px;
                            vertical-align: middle;
                        }}
                        th {{
                            background-color: #003366 !important;
                            color: white !important;
                            font-weight: 600;
                            -webkit-print-color-adjust: exact;
                        }}
                        
                        /* રીમાર્ક કૉલમ મોટી અને પહોળી કરવા માટે */
                        td:nth-child(10), th:nth-child(10) {{
                            min-width: 250px;
                            width: 28%;
                            word-break: break-word;
                            white-space: pre-wrap;
                            height: 60px;
                        }}
                        
                        .print-btn {{
                            background-color: #16A34A;
                            color: white;
                            padding: 12px 30px;
                            font-size: 16px;
                            font-weight: 600;
                            border: none;
                            border-radius: 6px;
                            cursor: pointer;
                            font-family: 'Noto Sans Gujarati', sans-serif;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                            margin-bottom: 20px;
                        }}
                        .print-btn:hover {{
                            background-color: #15803D;
                        }}
                        
                        @media print {{
                            .print-btn {{
                                display: none;
                            }}
                        }}
                    </style>
                    </head>
                    <body>
                        <button class="print-btn" onclick="window.print();">🖨️ અહીં ક્લિક કરીને પ્રિન્ટ કાઢો (Print)</button>
                        
                        <h2>મામલતદાર કચેરી - સુત્રાપાડા</h2>
                        <p><b>ટપાલ વર્કલિસ્ટ / દૈનિક રિપોર્ટ ({date_display})</b></p>
                        
                        {html_table}
                    </body>
                    </html>
                    """
                    
                    components.html(print_html_code, height=120)
