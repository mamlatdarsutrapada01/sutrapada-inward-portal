import streamlit as st

st.set_page_config(
    page_title="Sutrapada Inward Portal",
    page_icon="📄",
    layout="wide"
)

st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #2563EB;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">Sutrapada Inward Portal</div>', unsafe_allow_html=True)

# sidebar navigation or main content setup
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home / Inward Entry", "View Records", "Search"])

if page == "Home / Inward Entry":
    st.subheader("Add New Inward Entry")
    
    with st.form("inward_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            inward_no = st.text_input("Inward Number")
            date = st.date_input("Date")
            sender = st.text_input("Sender Name / Department")
            
        with col2:
            subject = st.text_input("Subject / Description")
            receiver = st.text_input("Receiver Name")
            status = st.selectbox("Status", ["Pending", "In Progress", "Completed"])
            
        remarks = st.text_area("Remarks")
        
        submitted = st.form_submit_button("Submit Inward")
        
        if submitted:
            if inward_no and sender:
                st.success(f"Inward {inward_no} successfully saved!")
            else:
                st.error("Please fill in the required fields (Inward Number and Sender Name).")

elif page == "View Records":
    st.subheader("Inward Records")
    st.info("Here you can view all the submitted inward records.")
    # Add your database or dataframe display logic here

else:
    st.subheader("Search Records")
    search_query = st.text_input("Enter Inward Number or Sender Name to search:")
    if search_query:
        st.write(f"Searching for: {search_query}")
