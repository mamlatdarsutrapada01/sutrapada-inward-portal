elif choice == "📅 દૈનિક વર્કલિસ્ટ (Daily Worklist)" and st.session_state.user_role == "admin":
        st.markdown("<h2 style='color: #003366;'>📅 દૈનિક ટપાલ વર્કલિસ્ટ, સર્ચ અને પ્રિન્ટ</h2>", unsafe_allow_html=True)
        st.write("---")
        
        df_all = pd.read_sql_query("SELECT * FROM inward ORDER BY id DESC", conn)

        if df_all.empty:
            st.warning("કોઈ રેકોર્ડ ઉપલબ્ધ નથી.")
        else:
            # ફિલ્ટર માટેના ઓપ્શન્સ (શાખા, તારીખ અને સર્ચ)
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                selected_branch = st.selectbox("શાખા પસંદ કરો (Select Branch):", ["બધી શાખાઓ (All)"] + branch_list)
            with col_f2:
                selected_date = st.date_input("🗓️ તારીખ પસંદ કરો:", date.today())
            with col_f3:
                search_query = st.text_input("🔍 સર્ચ કરો (ટપાલ નં / વિષય / Ref No):")

            # ડેટા ફિલ્ટરિંગ લોજિક
            df_filtered = df_all.copy()
            
            # તારીખ મુજબ ફિલ્ટર
            if selected_date:
                df_filtered = df_filtered[df_filtered["entry_date"] == str(selected_date)]
            
            # શાખા મુજબ ફિલ્ટર
            if selected_branch != "બધી શાખાઓ (All)":
                df_filtered = df_filtered[df_filtered["branch"] == selected_branch]
                
            # સર્ચ ક્વેરી મુજબ ફિલ્ટર (ટપાલ નંબર, વિષય અથવા રેફરન્સ નંબર)
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
                
                # પ્રિન્ટ/વર્કલિસ્ટ માટેના કોલમ્સ ગોઠવવા
                display_df = df_filtered[["id", "tappal_no", "ref_no", "javak_no", "branch", "letter_subject", "status", "entry_date"]]
                display_df.columns = ["ID", "ટપાલ નં.", "Ref No", "જાવક નં.", "શાખા", "પત્રનો વિષય", "સ્ટેટસ", "તારીખ"]
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)

                # PDF અને પ્રિન્ટ ડાઉનલોડ બટન
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
