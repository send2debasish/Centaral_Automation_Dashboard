import streamlit as st
import gspread
import pandas as pd
import base64
from google.oauth2.service_account import Credentials
#------------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="C&I",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# Session State
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# -----------------------------
# Page Session
# -----------------------------
if "page" not in st.session_state:
    st.session_state.page = "Home"

# -----------------------------
# Hide Streamlit Menu
# -----------------------------
st.markdown("""
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# Load Background Image
# -----------------------------
def get_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()


bg = get_base64("background.png")

# -----------------------------
# CSS
# -----------------------------
if not st.session_state.logged_in:

    st.markdown(f"""
    <style>

    .stApp {{
        background-image: url("data:image/png;base64,{bg}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* Fixed Logo Bottom Right */
.logo-bottom-right {{
    position: fixed;
    top: 120px;
    bottom: 30px;
    left: 500px;
    right: 20px;
    z-index: 999;
}}

.logo-bottom-right img {{
    width: 250px;      /* Change size as required */
    opacity: 0.95;     /* Optional */
}}

    .header-box{{
        width:750px;
        margin:-10px auto 20px auto;
        text-align:center;
    }}

    .header-title{{
        font-size:35px;
        font-weight:bold;
        color:white;
    }}

    .header-subtitle{{
        font-size:20px;
        font-weight:bold;
        color:#FFD700;
    }}

    .login-title {{
        text-align:center;
        font-size:20px;
        color:white;
        font-weight:bold;
    }}

    .stTextInput label {{
        color:white !important;
        font-size:10px !important;
        font-weight:bold !important;
    }}

    .stTextInput input {{
        height:35px !important;
        font-size:15px !important;


    }}

    .stButton>button {{
        width:440%;
        height:30px;
        font-size:52px;
    }}

    </style>
    """, unsafe_allow_html=True)

else:

    st.markdown("""
    <style>

    .stApp{
        background:white !important;
        background-image:none !important;
    }

    </style>
    """, unsafe_allow_html=True)


# -----------------------------
# Load Data from Google Sheet1
# -----------------------------
@st.cache_data(ttl=60)
def load_data():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scopes
)

    client = gspread.authorize(credentials)

    workbook = client.open("inst_list")
    worksheet = workbook.worksheet("Sheet1")

    data = worksheet.get_all_records()

    df = pd.DataFrame(data)

    return df


# -----------------------------
# Load Control Valve Data (Sheet2)
# -----------------------------
@st.cache_data(ttl=60)
def load_valve_data():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scopes
)

    client = gspread.authorize(credentials)

    workbook = client.open("inst_list")

    # Load Sheet2
    worksheet = workbook.worksheet("Sheet2")

    data = worksheet.get_all_records()

    df = pd.DataFrame(data)

    return df


# -----------------------------
# Load PLC checklist Data (Sheet3)
# -----------------------------
@st.cache_data(ttl=60)
def load_plc_data():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scopes
)

    client = gspread.authorize(credentials)

    workbook = client.open("inst_list")

    # Load Sheet2
    worksheet = workbook.worksheet("Sheet3")

    data = worksheet.get_all_records()

    df = pd.DataFrame(data)

    return df


# ============================================
# Load Shift Rota Data (Sheet4)
# ============================================
@st.cache_data(ttl=60)
def load_shift_data():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scopes
)
    client = gspread.authorize(credentials)

    workbook = client.open("inst_list")

    worksheet = workbook.worksheet("Sheet4")

    data = worksheet.get_all_records()

    df = pd.DataFrame(data)

    return df
#==================================================
#LINK PAGES
#==================================================
@st.cache_data(ttl=60)
def load_link_data():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scopes
)

    client = gspread.authorize(credentials)

    workbook = client.open("inst_list")
    worksheet = workbook.worksheet("Sheet5")

    return pd.DataFrame(worksheet.get_all_records())

# =====================================================
# LOGIN PAGE
# =====================================================
if not st.session_state.logged_in:

    st.markdown("""
    <div class="header-box">
        <div class="header-title">
            CENTRAL AUTOMATION DEPARTMENT
        </div>

    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="logo-bottom-right">
        <img src="data:image/png;base64,{}">
    </div>
    """.format(get_base64("jsw_logo.png")), unsafe_allow_html=True)

    left, center, right = st.columns([1.3, 1, 1.3])

    with center:

        st.markdown(
            '<div class="login-title">USER LOGIN</div>',
            unsafe_allow_html=True
        )

        username = st.text_input(
            "USERNAME",
            placeholder="Enter Username"
        )

        password = st.text_input(
            "PASSWORD",
            type="password",
            placeholder="Enter Password"
        )

        if st.button("LOGIN"):

            if username == "admin" and password == "jsw123":
                st.session_state.logged_in = True
                st.rerun()

            else:
                st.error("❌ Invalid Username or Password")

else:

    # ==========================
    # HOME PAGE
    # ==========================
    if st.session_state.page == "Home":

        st.markdown(
            """
            <h1 style='margin-top:-120px; margin-bottom:20px;'>
                🏠 INDEX PAGE
            </h1>
            """,
            unsafe_allow_html=True
        )
        # =============================================
        # Logout button below heading (left side)
        # =============================================
        left, right = st.columns([1, 8])

        with left:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.page = "Home"
                st.rerun()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("📋 INSTRUMENT LIST", use_container_width=True):
                st.session_state.page = "Instrument"
                st.rerun()

            if st.button("📊 INSTRUMENT SUMMERY", use_container_width=True):
                st.session_state.page = "Summary"
                st.rerun()

            if st.button("SHIFT ROTA", use_container_width=True):
                st.session_state.page = "SHIFT ROTA"
                st.rerun()

            if st.button("SHIFT DATA", use_container_width=True):
                st.session_state.page = "SHIFT DATA"
                st.rerun()

        with col2:
            if st.button("⚙ CONTROL VALVE LIST", use_container_width=True):
                st.session_state.page = "Valve"
                st.rerun()

            if st.button("📈 CONTROL VALVE SUMMERY", use_container_width=True):
                st.session_state.page = "ValveSummary"
                st.rerun()

            if st.button("LINK PAGE", use_container_width=True):
                st.session_state.page = "LINK PAGE"
                st.rerun()

        with col3:
            if st.button("PLC AUDIT CHECKLIST", use_container_width=True):
                st.session_state.page = "PLC CHECKLIST"
                st.rerun()

            if st.button("📈 PLC CHECKLIST SUMMER", use_container_width=True):
                st.session_state.page = "PLC SUMMERY"
                st.rerun()

        with col4:
            if st.button("THERMOGRAPHY", use_container_width=True):
                st.session_state.page = "THERMOGRAPHY RECORD"
                st.rerun()

            if st.button("📈 ", use_container_width=True):
                st.session_state.page = "THERMOGRAPHY SUMMERY"
                st.rerun()


    # ==========================
    # INSTRUMENT LIST PAGE
    # ==========================
    elif st.session_state.page == "Instrument":

        st.markdown(
            """
            <h1 style='margin-top:-150px; margin-bottom:15px;'>
                📋 INSTRUMENT LIST
            </h1>
            """,
            unsafe_allow_html=True
        )

        if st.button("⬅ Back to Home"):
            st.session_state.page = "Home"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        df = load_data()

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=700
        )

    # ==========================
    # INSTRUMENT SUMMARY PAGE
    # ==========================
    elif st.session_state.page == "Summary":

        st.markdown(
            """
            <h1 style='margin-top:-150px; margin-bottom:15px;'>
                📋 INSTRUMENT SUMMERY
            </h1>
            """,
            unsafe_allow_html=True
        )

        if st.button("⬅ Back to Home"):
            st.session_state.page = "Home"
            st.rerun()

        # Read Excel
        df = load_data()

        # Ensure Installed Qty is numeric
        df["INSTALLED QTY"] = pd.to_numeric(
            df["INSTALLED QTY"],
            errors="coerce"
        )

        # Summary
        summary = pd.pivot_table(
            df,
            index="AREA",
            columns="INSTRUMENT TYPE",
            values="INSTALLED QTY",
            aggfunc="sum",
            fill_value=0
        )

        st.dataframe(
            summary.reset_index(),
            use_container_width=True,
            hide_index=True,
            height=700
        )

    # ==========================
    # CONTROL VALVE LIST PAGE
    # ==========================

    elif st.session_state.page == "Valve":

        st.markdown(
            """
            <h1 style='margin-top:-150px; margin-bottom:40px;'>
                ⚙ CONTROL VALVE LIST
            </h1>
            """,
            unsafe_allow_html=True
        )

        if st.button("⬅ Back to Home"):
            st.session_state.page = "Home"
            st.rerun()

        # Load Sheet2
        df = load_valve_data()

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=700
        )
    # ==========================
    # CONTROL VALVE SUMMARY PAGE
    # ==========================
    elif st.session_state.page == "ValveSummary":

        st.markdown("""
        <h1 style='margin-top:-150px; margin-bottom:15px;'>
            📈 CONTROL VALVE SUMMARY
        </h1>
        """, unsafe_allow_html=True)

        if st.button("⬅ Back to Home", key="back_valve_summary"):
            st.session_state.page = "Home"
            st.rerun()

        # Load Control Valve Data
        df = load_valve_data()

        # Convert Quantity to numeric
        df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")

        # Area-wise Control Valve Count
        summary = pd.pivot_table(
            df,
            index="Area",
            values="Quantity",
            aggfunc="sum",
            fill_value=0
        ).reset_index()

        summary.rename(columns={"Quantity": "CONTROL VALVE COUNT"}, inplace=True)

        total = summary["CONTROL VALVE COUNT"].sum()

        st.metric("Total Control Valves", int(total))

        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True,
            height=700
        )
    # ==========================
    # PLC AUDIT CHECK LIST PAGE
    # ==========================

    elif st.session_state.page == "PLC CHECKLIST":

        st.markdown(
            """
            <h1 style='margin-top:-150px; margin-bottom:15px;'>
                ⚙ PLC AUDIT CHECKLIST
            </h1>
            """,
            unsafe_allow_html=True
        )

        if st.button("⬅ Back to Home"):
            st.session_state.page = "Home"
            st.rerun()

        # Load Sheet3
        df = load_plc_data()

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=700
        )


    # ==========================
    # SHIFT ROTA PAGE
    # ==========================

    elif st.session_state.page == "SHIFT ROTA":

        st.markdown(
            """
            <h1 style='margin-top:-150px; margin-bottom:15px;'>
                ⚙ SHIFT ROTA LIST
            </h1>
            """,
            unsafe_allow_html=True
        )

        if st.button("⬅ Back to Home"):
            st.session_state.page = "Home"
            st.rerun()

        # Load Sheet4
        df = load_shift_data()

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=700
        )
# ==========================
# LINK PAGE
# ==========================
    elif st.session_state.page == "LINK PAGE":

      st.markdown("""
      <h1 style='margin-top:-150px; margin-bottom:20px; text-align:center;'>
        🔗 TRAINING & APPLICATION LINKS
      </h1>
      """, unsafe_allow_html=True)

      if st.button("⬅ Back to Home", key="back_link"):
        st.session_state.page = "Home"
        st.rerun()

      df = load_link_data()
# Display 3 buttons in each row
      for i in range(0, len(df), 3):

        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]

        for j in range(3):

            if i + j < len(df):

                row = df.iloc[i + j]

                with cols[j]:

                    st.link_button(
                        label="📘 " + row["BUTTON"],
                        url=row["LINK"],
                        use_container_width=True
                    )

