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
        
        login_box_html = """
        <div style="text-align: center; background: #FFFFFF; padding: 30px; border-radius: 12px; box-shadow: 0 6px 20px rgba(0,51,102,0.15); border-top: 6px solid #003366;">
            <h2 style="color: #003366; margin-bottom: 5px; font-weight: 700;">મામલતદાર કચેરી - સુત્રાપાડા</h2>
            <p style="color: #D97706; font-weight: 600; font-size: 14px; margin-bottom: 20px;">શાખા અને એડમિન લૉગિન પોર્ટલ</p>
        </div>
        """
        st.markdown(login_box_html, unsafe_allow_html=True)

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

        designer_html = """
        <div class="designer-box" style="margin-top: 20px;">
            <div class="designer-text">DESIGNED & DEVELOPED BY</div>
            <div class="designer-name">✨ PARAS BHOLA ✨</div>
        </div>
        """
        st.markdown(designer_html, unsafe_allow_html=True)

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

    sidebar_header = f"""
    <div style="text-align: center; padding: 10px 0;">
        <h3 style="margin: 0; color: #FFFFFF;">🏛️ મામલતદાર કચેરી</h3>
        <p style="margin: 0; font-size: 12px; color: #FF9933;">લૉગ્ડ ઇન: {st.session_state.current_user}</p>
    </div>
    """
    st.sidebar.markdown(sidebar_header, unsafe_allow_html=True)
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

    sidebar_designer = """
    <div class="designer-box">
        <div class="designer-text">💻 DESIGNED & DEVELOPED BY</div>
        <div class="designer-name">✨ PARAS BHOLA ✨</div>
    </div>
    """
    st.sidebar.markdown(sidebar_designer, unsafe_allow_html=True)

    if choice == "🏠 મુખ્ય ડેશબોર્ડ (Dashboard)" and st.session_state.user_role == "admin":
        dashboard_header = """
        <div class="govt-header">
            <div class="govt-title">🏛️ મામલતદાર કચેરી - સુત્રાપાડા (એડમિન ડેશબોર્ડ)</div>
            <div class="govt-subtitle">કેન્દ્રીય ટપાલ વ્યવસ્થાપન સિસ્ટમ</div>
        </div>
        """
        st.markdown(dashboard_header, unsafe_allow_html=True)

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
        st.markdown("<h2 style='color: #003366;'>📁 એક્સેલ ફાઈલ દ્વારા બલ્ક એન્ટ્રી (Excel Import)</h2>", unsafe_allow_html=True)
        st.write("---")
        
        uploaded_file = st.file_uploader("એક્સેલ ફાઈલ અપલોડ કરો (.xlsx / .csv)", type=["xlsx", "csv"])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df_import = pd.read_csv(uploaded_file)
                else:
                    df_import = pd.read_excel(uploaded_file)
                
                st.write("ફાઈલનો ડેટા પૂર્વાવલોકન (Preview):")
                st.dataframe(df_import.head(), use_container_width=True)
                
                if st.button("📥 ડેટા ડેટાબેઝમાં સેવ કરો"):
                    for _, row in df_import.iterrows():
                        cursor.execute("""
                        INSERT INTO inward (
                            tappal_no, ref_no, subject, letter_subject, letter_date, 
                            received_from, from_office, to_office, branch, status, 
                            created_by, created_on, entry_date, remark, is_read
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                        """, (
                            str(row.get("tappal_no", "")),
                            str(row.get("ref_no", "")),
                            str(row.get("subject", "")),
                            str(row.get("letter_subject", "")),
                            str(row.get("letter_date", date.today())),
                            str(row.get("received_from", "")),
                            str(row.get("from_office", "")),
                            str(row.get("to_office", "")),
                            str(row.get("branch", "General")),
                            str(row.get("status", "Pending")),
                            "Paras Bhola",
                            str(date.today()),
                            str(date.today()),
                            str(row.get("remark", ""))
                        ))
                    conn.commit()
                    st.success("🎉 એક્સેલ ફાઈલનો તમામ ડેટા સફળતાપૂર્વક ઇનપુટ થઈ ગયો છે!")
            except Exception as e:
                st.error(f"⚠️ ફાઈલ વાંચવામાં ભૂલ આવી: {e}")

    elif choice == "↗️ એડમિન ટપાલ ફોરવર્ડ અને જાવક નંબર (Admin Dispatch/Forward)" and st.session_state.user_role == "admin":
        st.markdown("<h2 style='color: #003366;'>↗️ ટપાલ ફોરવર્ડ, સ્ટેટસ અપડેટ અને જાવક નંબર ફાળવણી</h2>", unsafe_allow_html=True)
        st.write("---")

        df_all = pd.read_sql_query("SELECT * FROM inward ORDER BY id DESC", conn)
        if df_all.empty:
            st.info("કોઈ ટપાલ ઉપલબ્ધ નથી.")
        else:
            selected_tappal_id = st.selectbox(
                "ટપાલ પસંદ કરો (ID - Tappal No - Subject):",
                df_all["id"],
                format_func=lambda x: f"ID: {x} | Tappal No: {df_all[df_all['id'] == x]['tappal_no'].values[0]} | Subject: {df_all[df_all['id'] == x]['letter_subject'].values[0][:40]}"
            )

            current_row = df_all[df_all["id"] == selected_tappal_id].iloc[0]

            with st.form("admin_action_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_branch = st.selectbox("શાખા બદલો (Change Branch):", branch_list, index=branch_list.index(current_row["branch"]) if current_row["branch"] in branch_list else 0)
                    new_status = st.selectbox("સ્થિતિ બદલો (Status):", ["Pending", "Working", "Disposed"], index=["Pending", "Working", "Disposed"].index(current_row["status"]) if current_row["status"] in ["Pending", "Working", "Disposed"] else 0)
                with col2:
                    new_javak = st.text_input("જાવક નંબર (Javak No):", value=str(current_row["javak_no"]) if pd.notna(current_row["javak_no"]) else "")
                    dispatch_date = st.date_input("જાવક તારીખ (Dispatch Date)", date.today())

                new_remark = st.text_area("નવો રીમાર્ક / શેરો (Remark):", value=str(current_row["remark"]) if pd.notna(current_row["remark"]) else "")
                
                submit_update = st.form_submit_button("💾 ફેરફારો સેવ કરો")

                if submit_update:
                    cursor.execute("""
                    UPDATE inward SET branch = ?, status = ?, javak_no = ?, dispatch_date = ?, remark = ? WHERE id = ?
                    """, (new_branch, new_status, new_javak, str(dispatch_date), new_remark, selected_tappal_id))
                    conn.commit()
                    st.success("✅ ટપાલની માહિતી સફળતાપૂર્વક અપડેટ થઈ ગઈ છે!")
                    st.rerun()

    elif choice == "📅 દૈનિક વર્કલિસ્ટ (Daily Worklist)" and st.session_state.user_role == "admin":
        st.markdown("<h2 style='color: #003366;'>📅 દૈનિક ટપાલ વર્કલિસ્ટ, સર્ચ અને પ્રિન્ટ</h2>", unsafe_allow_html=True)
        st.write("---")
        
        df_all = pd.read_sql_query("SELECT * FROM inward ORDER BY id DESC", conn)

        if df_all.empty:
            st.warning("કોઈ રેકોર્ડ ઉપલબ્ધ નથી.")
        else:
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                selected_branch = st.selectbox("શાખા પસંદ કરો (Select Branch):", ["બધી શાખાઓ (All)"] + branch_list)
            with col_f2:
                selected_date = st.date_input("🗓️ તારીખ પસંદ કરો:", date.today())
            with col_f3:
                search_query = st.text_input("🔍 સર્ચ કરો (ટપાલ નં / વિષય / Ref No):")

            df_filtered = df_all.copy()
            
            if selected_date:
                df_filtered = df_filtered[df_filtered["entry_date"] == str(selected_date)]
            
            if selected_branch != "બધી શાખાઓ (All)":
                df_filtered = df_filtered[df_filtered["branch"] == selected_branch]
                
            if search_query.strip():
                q = search_query.strip().lower()
                df_filtered = df_filtered[
                    df_filtered["tappal_no"].str.lower().str.contains(q, na=False) |
                    df_filtered["letter_subject"].str.lower().str.contains(q, na=False) |
                    df_filtered["ref_no"].str.lower().str.contains(q, na=False)
                ]

            if df_filtered.empty:
                st.info("આ ફિલ્ટર મુજબ કોઈ ટપાલ મળી નથી.")
            else:
                st.subheader(f"📋 મળેલ ટપાલોની યાદી (કુલ: {len(df_filtered)})")
                
                display_df = df_filtered[["id", "tappal_no", "ref_no", "javak_no", "branch", "letter_subject", "status", "entry_date"]]
                display_df.columns = ["ID", "ટપાલ નં.", "Ref No", "જાવક નં.", "શાખા", "પત્રનો વિષય", "સ્ટેટસ", "તારીખ"]
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)

                st.write("---")
                st.subheader("🖨️ રિપોર્ટ ડાઉનલોડ અને પ્રિન્ટ વિકલ્પો")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    pdf_buffer = generate_pdf(display_df, f"Mamlatdar Office Sutrapada - Daily Worklist ({selected_date})")
                    st.download_button(
                        label="📥 PDF ફાઈલ ડાઉનલોડ કરો (Download PDF)",
                        data=pdf_buffer,
                        file_name=f"Worklist_{selected_date}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                with col_btn2:
                    html_table = display_df.to_html(classes="styled-table", index=False)
                    print_html_code = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                    <title>દૈનિક ટપાલ વર્કલિસ્ટ</title>
                    <style>
                        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Gujarati:wght@400;600;700&display=swap');
                        @page {{ size: landscape; margin: 10mm; }}
                        body {{ font-family: 'Noto Sans Gujarati', sans-serif; margin: 20px; color: #000; text-align: center; }}
                        h2 {{ color: #003366; margin-bottom: 2px; font-size: 20px; }}
                        p {{ font-size: 14px; margin-top: 0; color: #555; margin-bottom: 20px; }}
                        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 11px; text-align: left; }}
                        th, td {{ border: 1px solid #003366; padding: 6px; vertical-align: middle; }}
                        th {{ background-color: #003366 !important; color: white !important; font-weight: 600; -webkit-print-color-adjust: exact; }}
                        .print-btn {{ background-color: #16A34A; color: white; padding: 12px 30px; font-size: 16px; font-weight: 600; border: none; border-radius: 6px; cursor: pointer; font-family: 'Noto Sans Gujarati', sans-serif; margin-bottom: 20px; }}
                        @media print {{ .print-btn {{ display: none; }} }}
                    </style>
                    </head>
                    <body>
                        <button class="print-btn" onclick="window.print();">🖨️ અહીં ક્લિક કરીને પ્રિન્ટ કાઢો (Print)</button>
                        <h2>મામલતદાર કચેરી - સુત્રાપાડા</h2>
                        <p><b>દૈનિક ટપાલ વર્કલિસ્ટ રિપોર્ટ (તારીખ: {selected_date})</b></p>
                        {html_table}
                    </body>
                    </html>
                    """
                    components.html(print_html_code, height=100)

    elif choice == "📥 મારી શાખાની ટપાલ / પોપ-અપ (Branch Inbox)" and st.session_state.user_role == "branch":
        branch_name = st.session_state.current_user
        st.markdown(f"<h2 style='color: #003366;'>📥 {branch_name} શાખાનું ઇનબોક્સ (Inbox)</h2>", unsafe_allow_html=True)
        st.write("---")

        df_branch = pd.read_sql_query(f"SELECT * FROM inward WHERE branch = '{branch_name}' ORDER BY id DESC", conn)

        if df_branch.empty:
            st.info(f"તમારી શાખા ({branch_name}) માટે હાલમાં કોઈ ટપાલ ઉપલબ્ધ નથી.")
        else:
            display_df = df_branch[["id", "tappal_no", "ref_no", "letter_subject", "received_from", "status", "entry_date"]]
            display_df.columns = ["ID", "ટપાલ નં.", "Ref No", "પત્રનો વિષય", "ક્યાંથી મળેલ", "સ્ટેટસ", "તારીખ"]
            st.dataframe(display_df, use_container_width=True, hide_index=True)

    elif choice == "↗️ ટપાલ અન્ય શાખામાં ફોરવર્ડ કરો (Forward Tappal)" and st.session_state.user_role == "branch":
        branch_name = st.session_state.current_user
        st.markdown(f"<h2 style='color: #003366;'>↗️ ટપાલ અન્ય શાખામાં મોકલો - {branch_name}</h2>", unsafe_allow_html=True)
        st.write("---")

        df_branch = pd.read_sql_query(f"SELECT * FROM inward WHERE branch = '{branch_name}' ORDER BY id DESC", conn)
        if df_branch.empty:
            st.info("ફોરવર્ડ કરવા માટે કોઈ ટપાલ નથી.")
        else:
            selected_id = st.selectbox(
                "ટપાલ પસંદ કરો:",
                df_branch["id"],
                format_func=lambda x: f"ID: {x} | Tappal No: {df_branch[df_branch['id'] == x]['tappal_no'].values[0]}"
            )
            target_branch = st.selectbox("કઈ શાખામાં મોકલવી છે?", [b for b in branch_list if b != branch_name])
            branch_remark = st.text_area("શાખાનો શેરો / રીમાર્ક:")

            if st.button("🚀 અન્ય શાખામાં મોકલો"):
                cursor.execute("UPDATE inward SET branch = ?, remark = ? WHERE id = ?", (target_branch, branch_remark, selected_id))
                conn.commit()
                st.success(f"✅ ટપાલ સફળતાપૂર્વક **{target_branch}** શાખામાં મોકલી દેવામાં આવી છે!")
                st.rerun()

    elif choice == "📅 શાખા વર્કલિસ્ટ (Branch Worklist)" and st.session_state.user_role == "branch":
        branch_name = st.session_state.current_user
        st.markdown(f"<h2 style='color: #003366;'>📅 {branch_name} શાખાનું વર્કલિસ્ટ</h2>", unsafe_allow_html=True)
        st.write("---")

        df_branch = pd.read_sql_query(f"SELECT * FROM inward WHERE branch = '{branch_name}' ORDER BY id DESC", conn)
        if df_branch.empty:
            st.info("કોઈ રેકોર્ડ ઉપલબ્ધ નથી.")
        else:
            display_df = df_branch[["id", "tappal_no", "ref_no", "javak_no", "letter_subject", "status", "entry_date"]]
            display_df.columns = ["ID", "ટપાલ નં.", "Ref No", "જાવક નં.", "પત્રનો વિષય", "સ્ટેટસ", "તારીખ"]
            st.dataframe(display_df, use_container_width=True, hide_index=True)

    conn.close()
