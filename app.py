import streamlit as st
import gspread
import pandas as pd
import base64
from datetime import datetime
from zoneinfo import ZoneInfo
from streamlit_autorefresh import st_autorefresh
from google.oauth2.service_account import Credentials


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="C&I",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# SESSION
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "Home"


# =========================================================
# HIDE STREAMLIT DEFAULT UI
# =========================================================

st.markdown("""
<style>

#MainMenu,
footer,
header {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# IMAGE FUNCTION
# =========================================================

def get_base64(file):

    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()


bg = get_base64("background.png")
logo = get_base64("jsw_logo.png")


# =========================================================
# LOGIN CSS
# =========================================================

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

    .header-title {{
        text-align: center;
        font-size: 40px;
        font-weight: bold;
        color: white;
        margin-top: -20px;
        margin-bottom: 35px;
    }}

    .logo {{
        position: fixed;
        top: 150px;
        left: 550px;
        z-index: 9999;
    }}

    .logo img {{
        width: 200px;
    }}

    .login-title {{
        text-align: center;
        font-size: 20px;
        font-weight: bold;
        color: white;
        margin-bottom: 15px;
    }}

    .stTextInput label {{
        color: white !important;
        font-size: 20px !important;
        font-weight: bold !important;
    }}

    div[data-testid="stTextInput"] input {{
        width: 100%;
        height: 55px;
        font-size: 18px;
        text-align: left;
        padding: 5px 15px 12px;
        border-radius: 12px;
    }}

    </style>
    """, unsafe_allow_html=True)


# =========================================================
# OTHER PAGES - WHITE BACKGROUND
# =========================================================

else:

    st.markdown("""
    <style>

    .stApp {
        background: white !important;
        background-image: none !important;
    }

    </style>
    """, unsafe_allow_html=True)


# =========================================================
# COMMON GOOGLE SHEET FUNCTION
# =========================================================

@st.cache_data(ttl=60)
def load_sheet(sheet_name):

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )

    client = gspread.authorize(credentials)

    worksheet = (
        client
        .open("inst_list")
        .worksheet(sheet_name)
    )

    return pd.DataFrame(
        worksheet.get_all_records()
    )


# =========================================================
# LOGIN PAGE
# =========================================================

if not st.session_state.logged_in:

    st.markdown(
        '<div class="header-title">CENTRAL AUTOMATION DEPARTMENT</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'''
        <div class="logo">
            <img src="data:image/png;base64,{logo}">
        </div>
        ''',
        unsafe_allow_html=True
    )

    left, center, right = st.columns([1.3, 1, 1.3])

    with center:

        st.markdown(
            '<div class="login-title">USER LOGIN</div>',
            unsafe_allow_html=True
        )

        username = st.text_input(
            "USERNAME",
            placeholder="Enter Username",
            key="username"
        )

        password = st.text_input(
            "PASSWORD",
            type="password",
            placeholder="Enter Password",
            key="password"
        )

        if st.button(
            "LOGIN",
            use_container_width=True
        ):

            if username == "admin" and password == "jsw123":

                st.session_state.logged_in = True
                st.session_state.page = "Home"

                st.rerun()

            else:

                st.error(
                    "❌ Invalid Username or Password"
                )


# =========================================================
# AFTER LOGIN
# =========================================================

else:

    # =====================================================
    # HOME / INDEX PAGE
    # =====================================================

    if st.session_state.page == "Home":

        # =================================================
        # INDEX PAGE CSS
        # =================================================

        st.markdown("""
        <style>
        
        /* =================================================
           FIX HOME DASHBOARD SCREEN
          ================================================= */

        html,
        body,
        [data-testid="stAppViewContainer"] {
              overflow: hidden !important;
        }

        [data-testid="stAppViewContainer"] {
        height: 100vh !important;
        }

        [data-testid="stAppViewContainer"] > .main {
              overflow: hidden !important;
        }

        [data-testid="stMainBlockContainer"] {
              overflow: hidden !important;
        }

        /* =================================================
           3D INDEX BUTTONS
           ================================================= */

        .stButton {
            width: 100%;
            transform: translateY(0px);
        }

        .stButton > button {

            height: 82px !important;
            width: 100% !important;
            min-width: 0 !important;

            border-radius: 10px !important;

            background:
                linear-gradient(
                    145deg,
                    #315f89,
                    #204d75,
                    #12395f,
                    #082641
                ) !important;

            color: white !important;

            border: 1px solid #6c9ec5 !important;

            font-size: 56px !important;

            font-weight: 800 !important;

            letter-spacing: 0.8px !important;

            box-shadow:

                0 7px 0 #041522,

                0 12px 20px
                rgba(0,0,0,0.30),

                0 0 10px
                rgba(30,140,220,0.25),

                inset 0 2px 2px
                rgba(255,255,255,0.35),

                inset 0 -5px 8px
                rgba(0,0,0,0.30) !important;

            transition: all 0.18s ease !important;
        }


        /* =================================================
           BUTTON HOVER
           ================================================= */

        .stButton > button:hover {

            transform: translateY(-5px) !important;

            border-color: #83c5ef !important;

            background:
                linear-gradient(
                    145deg,
                    #3c76a5,
                    #28618e,
                    #174b73,
                    #0a2c49
                ) !important;

            box-shadow:

                0 12px 0 #041522,

                0 18px 30px
                rgba(0,0,0,0.35),

                0 0 15px
                rgba(30,160,240,0.60),

                0 0 30px
                rgba(30,150,230,0.30),

                inset 0 2px 3px
                rgba(255,255,255,0.45) !important;
        }


        /* =================================================
           BUTTON PRESS
           ================================================= */

        .stButton > button:active {

            transform: translateY(5px) !important;

            box-shadow:

                0 2px 0 #041522,

                0 5px 10px
                rgba(0,0,0,0.25),

                inset 0 4px 8px
                rgba(0,0,0,0.35) !important;
        }


        /* =================================================
           DASHBOARD HEADER
           ================================================= */

        .dashboard-header {

    width: 100vw;
    height: 100px;

    margin-left: calc(50% - 50vw);
    margin-right: calc(50% - 50vw);

    background:
        linear-gradient(
            90deg,
            #061426,
            #0b2038,
            #07182b
        );

    border: 1px solid #315b7d;
    border-radius: 6px;

    display: flex;
    align-items: center;

    padding: 5px 10px;
    box-sizing: border-box;

    box-shadow:
        0 4px 12px
        rgba(0,0,0,0.35);

    margin-top: -200px;
    margin-bottom: 15px;
    }


        /* =================================================
           JSW LOGO
        ================================================= */

        .dashboard-logo {

            width: 210px;
            height: 72px;

            background: white;

            border-radius: 5px;

            display: flex;

            align-items: center;

            justify-content: center;

            flex-shrink: 0;

        }

        .dashboard-logo img {

            width: 195px;

            height: auto;

        }

        /* =================================================
           CENTER HEADER
           ================================================= */

        .dashboard-center {

            flex: 1;

            text-align: center;

            padding: 0 15px;

        }

        .dashboard-main-title {

            color: white;

            font-size: 18px;

            font-weight: 800;

            margin: 0;

        }

        .dashboard-sub-title {

            color: #ffd900;

            font-size: 22px;

            font-weight: 900;

            margin: 2px 0;

        }

        .dashboard-description {

            color: white;

            font-size: 11px;

            margin: 0;

        }

        .plant-status {

            color: #4cff00;

            font-size: 12px;

            font-weight: bold;

            margin-top: 2px;

        }

        /* =================================================
           RIGHT HEADER INFORMATION
           ================================================= */

        .header-info {

            display: flex;

            height: 70px;

            flex-shrink: 0;

        }

        .info-box {

            min-width: 75px;

            padding: 5px;

            border-left:
                1px solid #52677d;

            color: white;

            text-align: center;

            display: flex;

            flex-direction: column;

            justify-content: center;

        }

        .info-label {

            font-size: 8px;

            font-weight: bold;

            color: #d7e2ec;

            margin-bottom: 3px;

        }

        .info-value {

            font-size: 15px;

            font-weight: bold;

            color: white;

        }


        /* =================================================
           LOGOUT FORM
           ================================================= */

        div[data-testid="stForm"] {

          position: fixed !important;

          top: 23px !important;

          right: 185px !important;

          width: 125px !important;

          z-index: 99999 !important;

          border: none !important;

          padding: 0 !important;

          margin: 0 !important;

          background: transparent !important;

        }

        div[data-testid="stForm"]
        div[data-testid="stButton"] > button {

            height: 45px !important;

            width: 125px !important;

            min-height: 45px !important;

            font-size: 16px !important;

            border-radius: 8px !important;

            background:
                linear-gradient(
                    145deg,
                    #214d75,
                    #12385c,
                    #071f38
                ) !important;

            transform: translateY(0px) !important;
            

        }

        </style>
        """, unsafe_allow_html=True)


        # =================================================
        # DASHBOARD HEADER
        # =================================================
        st_autorefresh(
            interval=60000,
            key="dashboard_clock"
        )
        now = datetime.now(ZoneInfo("Asia/Kolkata"))

        current_date = now.strftime("%d-%b-%Y")

        current_time = now.strftime("%I:%M %p")


        st.markdown(f"""<div class="dashboard-header">

<div class="dashboard-logo">
<img src="data:image/png;base64,{logo}">
</div>

<div class="dashboard-center">

<div class="dashboard-main-title">
CENTRAL AUTOMATION DEPARTMENT
</div>

<div class="dashboard-sub-title">
AUTOMATION &amp; INSTRUMENT DASHBOARD
</div>

</div>

<div class="header-info">

<div class="info-box">
<div class="info-label">DATE</div>
<div class="info-value">{current_date}</div>
</div>

<div class="info-box">
<div class="info-label">TIME</div>
<div class="info-value">{current_time}</div>
</div>

</div>

</div>""", unsafe_allow_html=True)


        # =================================================
        # LOGOUT
        # =================================================

        with st.form(
            "logout_form",
            border=False
        ):

            logout_clicked = st.form_submit_button(
                "LOGOUT"
            )

            if logout_clicked:

                st.session_state.logged_in = False

                st.session_state.page = "Home"

                st.rerun()

        # =================================================
        # INDEX BUTTONS
        # =================================================

        col1, col2, col3, col4, col5 = st.columns(5)

        # =================================================
        # COLUMN 1
        # =================================================

        with col1:

            if st.button(
                " INSTRUMENT LIST",
                use_container_width=True,
                key="instrument_list"
            ):

                st.session_state.page = "Instrument"

                st.rerun()


            if st.button(
                "INSTRUMENT SUMMARY",
                use_container_width=True,
                key="instrument_summary"
            ):

                st.session_state.page = "Summary"

                st.rerun()


        # =================================================
        # COLUMN 2
        # =================================================

        with col2:

            if st.button(
                "CONTROL VALVE LIST",
                use_container_width=True,
                key="valve_list"
            ):

                st.session_state.page = "Valve"

                st.rerun()


            if st.button(
                "CONTROL VALVE SUMMARY",
                use_container_width=True,
                key="valve_summary"
            ):

                st.session_state.page = "ValveSummary"

                st.rerun()


            if st.button(
                "LINK PAGE",
                use_container_width=True,
                key="link_page"
            ):

                st.session_state.page = "LINK PAGE"

                st.rerun()


        # =================================================
        # COLUMN 3
        # =================================================

        with col3:

            if st.button(
                "PLC AUDIT CHECKLIST",
                use_container_width=True,
                key="plc_checklist"
            ):

                st.session_state.page = "PLC CHECKLIST"

                st.rerun()


            if st.button(
                "PLC CHECKLIST SUMMARY",
                use_container_width=True,
                key="plc_summary"
            ):

                st.session_state.page = "PLC SUMMARY"

                st.rerun()


        # =================================================
        # COLUMN 4
        # =================================================

        with col4:

            if st.button(
                "DEPARTMENT STATUS LIST",
                use_container_width=True,
                key="department_status"
            ):

                st.session_state.page = "DEPARTMENT STATUS LIST"

                st.rerun()


            if st.button(
                "📈 ",
                use_container_width=True,
                key="thermography_summary"
            ):

                st.session_state.page = "THERMOGRAPHY SUMMARY"

                st.rerun()

        # =================================================
        # COLUMN 5
        # =================================================

        with col5:

            if st.button(
                "SHIFT ROTA",
                use_container_width=True,
                key="shift_rota"
            ):

                st.session_state.page = "SHIFT ROTA"

                st.rerun()


            if st.button(
                "SHIFT DATA",
                use_container_width=True,
                key="shift_data"
            ):

                st.session_state.page = "SHIFT DATA"
                st.rerun()


    # =====================================================
    # OTHER PAGES
    # =====================================================

    else:

        # =================================================
        # PAGE TITLES
        # =================================================

        titles = {

            "Instrument":
                "INSTRUMENT LIST",

            "Summary":
                "INSTRUMENT SUMMARY",

            "Valve":
                "CONTROL VALVE LIST",

            "ValveSummary":
                "CONTROL VALVE SUMMARY",

            "PLC CHECKLIST":
                "PLC AUDIT CHECKLIST",

            "SHIFT ROTA":
                "SHIFT ROTA LIST",

            "APPLICATION LINK":
                "TRAINING & APPLICATION LINKS",

            "SHIFT DATA":
                "SHIFT DATA",

            "DEPARTMENT STATUS LIST":
                  "DEPARTMENT STATUS LIST",
        }


        # =================================================
        # INTERNAL PAGE HEADER CSS
        # =================================================

        st.markdown("""
        <style>

        .block-container {

            max-width: 100% !important;

            padding:
                5px 8px 5px 8px !important;

            transform:
                translateY(-40px) !important;

        }


        /* Back button */

        div[data-testid="stButton"] > button {

            width: 110px !important;

            height: 32px !important;

            min-height: 32px !important;

            padding: 0 !important;

            font-size: 12px !important;

            margin: 0 !important;

        }


        /* Page title */

        .page-title {

            text-align: center;

            font-size: 38px;

            font-weight: 700;

            margin:
                -5px 0 0 0 !important;

            padding: 0 !important;

        }


        /* Full-width data sheets */

        div[data-testid="stDataFrame"] {

            width: 100% !important;

        }
        
        /* =================================================
   3D INDUSTRIAL TRAINING & APPLICATION BUTTONS
   ================================================= */

div[data-testid="stLinkButton"] {
    width: 100% !important;
    margin-top: 8px !important;
    margin-bottom: 14px !important;
}

div[data-testid="stLinkButton"] > a {

    height: 72px !important;
    min-height: 72px !important;
    width: 100% !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    box-sizing: border-box !important;

    padding: 8px 10px !important;

    border-radius: 10px !important;

    background: linear-gradient(
        145deg,
        #315f89,
        #204d75,
        #12395f,
        #082641
    ) !important;

    color: white !important;

    border: 1px solid #6c9ec5 !important;

    font-size: 20px !important;

    font-weight: 800 !important;

    letter-spacing: 0.5px !important;

    text-decoration: none !important;

    box-shadow:
        0 7px 0 #041522,
        0 12px 20px rgba(0,0,0,0.30),
        0 0 10px rgba(30,140,220,0.25),
        inset 0 2px 2px rgba(255,255,255,0.35),
        inset 0 -5px 8px rgba(0,0,0,0.30) !important;

    transition: all 0.18s ease !important;
}


/* HOVER */

div[data-testid="stLinkButton"] > a:hover {

    transform: translateY(-5px) !important;

    color: white !important;

    border-color: #83c5ef !important;

    background: linear-gradient(
        145deg,
        #3c76a5,
        #28618e,
        #174b73,
        #0a2c49
    ) !important;

    box-shadow:
        0 12px 0 #041522,
        0 18px 30px rgba(0,0,0,0.35),
        0 0 15px rgba(30,160,240,0.60),
        0 0 30px rgba(30,150,230,0.30),
        inset 0 2px 3px rgba(255,255,255,0.45) !important;
}


/* PRESS */

div[data-testid="stLinkButton"] > a:active {

    transform: translateY(5px) !important;

    box-shadow:
        0 2px 0 #041522,
        0 5px 10px rgba(0,0,0,0.25),
        inset 0 4px 8px rgba(0,0,0,0.35) !important;
}
        </style>
        """, unsafe_allow_html=True)

        # =================================================
        # BACK BUTTON + TITLE - SAME ROW
        # =================================================

        back_col, title_col, right_col = st.columns(
            [1.3, 7.4, 1.3]
        )


        with back_col:

            if st.button(
                "⬅ Back",
                key=f"back_{st.session_state.page}"
            ):

                st.session_state.page = "Home"

                st.rerun()


        with title_col:

            st.markdown(
                f'<div class="page-title">{titles.get(st.session_state.page, st.session_state.page)}</div>',
                unsafe_allow_html=True
            )

        # =================================================
        # INSTRUMENT LIST
        # =================================================

        if st.session_state.page == "Instrument":

            df = load_sheet("Sheet1")

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                height=500
            )

        # =================================================
        # INSTRUMENT SUMMARY
        # =================================================

        elif st.session_state.page == "Summary":

            df = load_sheet("Sheet1")

            df["INSTALLED QTY"] = pd.to_numeric(
                df["INSTALLED QTY"],
                errors="coerce"
            )

            summary = pd.pivot_table(
                df,
                index="AREA",
                columns="INSTRUMENT TYPE",
                values="INSTALLED QTY",
                aggfunc="sum",
                fill_value=0
            ).reset_index()

            st.dataframe(
                summary,
                use_container_width=True,
                hide_index=True,
                height=500,

                column_config={

                    "AREA":
                        st.column_config.TextColumn(
                            "AREA",
                            pinned=True
                        )
                }
            )

        # =================================================
        # CONTROL VALVE LIST
        # =================================================

        elif st.session_state.page == "Valve":

            df = load_sheet("Sheet2")

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                height=500
            )


        # =================================================
        # CONTROL VALVE SUMMARY
        # =================================================

        elif st.session_state.page == "ValveSummary":

            df = load_sheet("Sheet2")

            df["Quantity"] = pd.to_numeric(
                df["Quantity"],
                errors="coerce"
            )

            summary = pd.pivot_table(
                df,
                index="Area",
                values="Quantity",
                aggfunc="sum",
                fill_value=0
            ).reset_index()

            summary.rename(
                columns={
                    "Quantity":
                        "CONTROL VALVE COUNT"
                },
                inplace=True
            )

            st.metric(
                "Total Control Valves",
                int(
                    summary[
                        "CONTROL VALVE COUNT"
                    ].sum()
                )
            )

            st.dataframe(
                summary,
                use_container_width=True,
                hide_index=True,
                height=500
            )

        # =================================================
        # PLC CHECKLIST
        # =================================================

        elif st.session_state.page == "PLC CHECKLIST":

            df = load_sheet("Sheet3")

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                height=500
            )

        # =================================================
        # SHIFT ROTA
        # =================================================

        elif st.session_state.page == "SHIFT ROTA":

            df = load_sheet("Sheet4")

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                height=500,

                column_config={

                    "NAME":
                        st.column_config.TextColumn(
                            "NAME",
                            pinned=True
                        )
                }
            )
        # =================================================
        # LINK PAGE
        # =================================================

        elif st.session_state.page == "APPLICATION LINK":

            df = load_sheet("Sheet5")

            for i in range(0, len(df), 4):

                c1, c2, c3, c4 = st.columns(4)

                for col, j in zip(
                    [c1, c2, c3, c4],
                    range(4)
                ):

                    if i + j < len(df):

                        row = df.iloc[i + j]

                        with col:

                            st.link_button(
                                str(row["BUTTON"]),
                                str(row["LINK"]),
                                use_container_width=True
                            )


        # =================================================
        # SHIFT DATA
        # =================================================

        elif st.session_state.page == "SHIFT DATA":

            df = load_sheet("Sheet4")

            df.columns = (
                df.columns
                .astype(str)
                .str.strip()
            )

            date_columns = list(
                df.columns[3:]
            )

            selected_date = st.selectbox(
                "📅 SELECT DATE",
                date_columns
            )

            shift = (
                df[selected_date]
                .astype(str)
                .str.strip()
                .str.upper()
            )

            shifts = {

                "A SHIFT":
                    df.loc[
                        shift == "A",
                        "NAME"
                    ].tolist(),

                "B SHIFT":
                    df.loc[
                        shift == "B",
                        "NAME"
                    ].tolist(),

                "C SHIFT":
                    df.loc[
                        shift == "C",
                        "NAME"
                    ].tolist(),

                "G SHIFT":
                    df.loc[
                        shift == "G",
                        "NAME"
                    ].tolist()
            }

            st.markdown(
                f"""
                <h3 style="text-align:center">
                    SHIFT DETAILS - {selected_date}
                </h3>
                """,
                unsafe_allow_html=True
            )

            c1, c2, c3, c4 = st.columns(4)

            for col, (shift_name, names) in zip(
                [c1, c2, c3, c4],
                shifts.items()
            ):

                with col:

                    st.markdown(
                        f"""
                        <div style="
                            text-align:center;
                            font-size:21px;
                            font-weight:bold;
                            padding:8px;
                            background:#dceaf7;
                            border-radius:8px;
                            margin-bottom:8px;">
                            {shift_name}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    for name in names:

                        st.markdown(
                            f"""
                            <div style="
                                text-align:center;
                                font-size:16px;
                                padding:6px;
                                margin:3px;
                                border:1px solid #ccc;
                                border-radius:6px;
                                background:white;">
                                {name}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

# =================================================
# DEPARTMENT STATUS
# =================================================

        elif st.session_state.page =="DEPARTMENT STATUS LIST":

                df = load_sheet("Sheet6")

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    height=500
                )
