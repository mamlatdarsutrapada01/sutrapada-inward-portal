# ડેટાબેઝ કનેક્શન
    conn = sqlite3.connect("sutrapada_inward.db", check_same_thread=False)
    cursor = conn.cursor()

    # ૧. મુખ્ય ટેબલ બનાવો
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
    
    # ၂. ઓટો-માઈગ્રેશન: જો જૂના ટેબલમાં નવી કૉલમ ન હોય તો તેને ઉમેરો
    try:
        cursor.execute("ALTER TABLE inward ADD COLUMN ref_no TEXT")
    except sqlite3.OperationalError:
        pass  # જો કૉલમ પહેલેથી જ હશે તો એરર નહીં આવે અને આગળ ચાલશે

    try:
        cursor.execute("ALTER TABLE inward ADD COLUMN external_sender TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE inward ADD COLUMN is_read INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    conn.commit()
