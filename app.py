import streamlit as st
import gspread
import pandas as pd
import base64
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
# HIDE Streamlit DEFAULT UI
# =========================================================
st.markdown("""
<style>
#MainMenu, footer, header {
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
        padding: 0 15px 12px;
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
        background: #f3f8fc !important;
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

        /* ==============================
           INDEX TITLE
           ============================== */

        .index-title {
            text-align: center;

            font-size: 44px;
            font-weight: 900;

            letter-spacing: 3px;

            color: #183b63;

            margin-top: -150px;
            margin-bottom: 20px;

            text-shadow:
                0 2px 3px rgba(0,0,0,0.20),
                0 0 15px rgba(40,130,200,0.25);
        }


        /* ==============================
           3D INDEX BUTTONS
           ============================== */
        .stButton {
            transform: translateY(-70px);
        }
        .stButton > button {

            height: 82px !important;
            width: 200px !important;

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


        /* ==============================
           BUTTON HOVER
           ============================== */

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


        /* ==============================
           BUTTON PRESS
           ============================== */

        .stButton > button:active {

            transform: translateY(5px) !important;

            box-shadow:

                0 2px 0 #041522,

                0 5px 10px
                rgba(0,0,0,0.25),

                inset 0 4px 8px
                rgba(0,0,0,0.35) !important;
        }


        /* ==============================
           LOGOUT
           ============================== */

        .logout-button > button {

            height: 45px !important;
            width: 125px !important;
            font-size: 36px !important;

            border-radius: 8px !important;

            background:
                linear-gradient(
                    145deg,
                    #214d75,
                    #12385c,
                    #071f38
                ) !important;
        }

        </style>
        """, unsafe_allow_html=True)


        # =================================================
        # TOP HEADER
        # =================================================
        top_left, top_center, top_right = st.columns([1, 3, 1])


        # =================================================
        # LOGOUT - TOP LEFT
        # =================================================
        with top_left:

            if st.button(
                "LOGOUT",
                key="logout"
            ):

                st.session_state.logged_in = False
                st.session_state.page = "Home"
                st.rerun()


        # =================================================
        # INDEX TITLE - CENTER
        # =================================================
        with top_center:

            st.markdown(
                '<div class="index-title">INDEX PAGE</div>',
                unsafe_allow_html=True
            )
        # =================================================
        # INDEX BUTTONS
        # =================================================
        col1, col2, col3, col4 = st.columns(4)

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
                "INSTRUMENT SUMMERY",
                use_container_width=True,
                key="instrument_summary"
            ):
                st.session_state.page = "Summary"
                st.rerun()


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
                "CONTROL VALVE SUMMERY",
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
                "PLC CHECKLIST SUMMER",
                use_container_width=True,
                key="plc_summary"
            ):
                st.session_state.page = "PLC SUMMERY"
                st.rerun()


        # =================================================
        # COLUMN 4
        # =================================================
        with col4:

            if st.button(
                "THERMOGRAPHY",
                use_container_width=True,
                key="thermography"
            ):
                st.session_state.page = "THERMOGRAPHY RECORD"
                st.rerun()


            if st.button(
                "📈 ",
                use_container_width=True,
                key="thermography_summary"
            ):
                st.session_state.page = "THERMOGRAPHY SUMMERY"
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
                "INSTRUMENT SUMMERY",

            "Valve":
                "CONTROL VALVE LIST",

            "ValveSummary":
                "CONTROL VALVE SUMMARY",

            "PLC CHECKLIST":
                "PLC AUDIT CHECKLIST",

            "SHIFT ROTA":
                "SHIFT ROTA LIST",

            "LINK PAGE":
                "TRAINING & APPLICATION LINKS",

            "SHIFT DATA":
                "SHIFT DATA"
        }


        # =================================================
        # INTERNAL PAGE HEADER CSS
        # =================================================
        st.markdown("""
        <style>

        .block-container {
            max-width: 100% !important;
            padding: 5px 8px 5px 8px !important;
            transform: translateY(-40px) !important;
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
            margin: -5px 0 0 0 !important;
            padding: 0 !important;
        }

        /* Full-width data sheets */
        div[data-testid="stDataFrame"] {
            width: 100% !important;
        }

        </style>
        """, unsafe_allow_html=True)


        # =================================================
        # BACK BUTTON + TITLE - SAME ROW
        # =================================================
        back_col, title_col, right_col = st.columns([1.3, 7.4, 1.3])

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
                df["INSTALLED QTY"], errors="coerce"
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
                    "AREA": st.column_config.TextColumn(
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
                    "Quantity": "CONTROL VALVE COUNT"
                },
                inplace=True
            )

            st.metric(
                "Total Control Valves",
                int(summary["CONTROL VALVE COUNT"].sum())
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
                    "NAME": st.column_config.TextColumn(
                        "NAME",
                        pinned=True
                    )
                }
            )


        # =================================================
        # LINK PAGE
        # =================================================
        elif st.session_state.page == "LINK PAGE":

            df = load_sheet("Sheet5")

            for i in range(0, len(df), 3):

                c1, c2, c3 = st.columns(3)

                for col, j in zip(
                    [c1, c2, c3],
                    range(3)
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
#====================================================================================================================
