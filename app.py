import streamlit as st
import gspread
import pandas as pd
import base64
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
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

if "system_architecture_department" not in st.session_state:
    st.session_state.system_architecture_department = None

if "system_architecture_department_name" not in st.session_state:
    st.session_state.system_architecture_department_name = None

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
# SYSTEM ARCHITECTURE - GOOGLE DRIVE
# =========================================================

@st.cache_resource
def get_drive_service():

    credentials = Credentials.from_service_account_file(
        "service_account.json",
        scopes=[
            "https://www.googleapis.com/auth/drive"
        ]
    )

    return build(
        "drive",
        "v3",
        credentials=credentials
    )


def get_system_architecture_folder():

    service = get_drive_service()

    query = (
        "name = 'JJSL AUTOMATION NETWORK ARCHITECTURE' "
        "and mimeType = 'application/vnd.google-apps.folder' "
        "and trashed = false"
    )

    # First search the service account's normal Drive corpus.
    result = service.files().list(
        q=query,
        spaces="drive",
        corpora="user",
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        fields="files(id,name,mimeType,webViewLink,driveId)",
        pageSize=100
    ).execute()

    folders = result.get("files", [])

    # Fallback: search all accessible drives as well.
    if not folders:
        result = service.files().list(
            q=query,
            spaces="drive",
            corpora="allDrives",
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            fields="files(id,name,mimeType,webViewLink,driveId)",
            pageSize=100
        ).execute()

        folders = result.get("files", [])

    if folders:
        return folders[0]

    return None


def get_department_folders(parent_id):

    service = get_drive_service()

    query = (
        f"'{parent_id}' in parents "
        "and mimeType = 'application/vnd.google-apps.folder' "
        "and trashed = false"
    )

    result = service.files().list(
        q=query,
        spaces="drive",
        corpora="allDrives",
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        fields="files(id,name,mimeType,webViewLink)",
        orderBy="name"
    ).execute()

    return result.get("files", [])


def get_department_documents(parent_id):

    service = get_drive_service()

    query = (
        f"'{parent_id}' in parents "
        "and mimeType != 'application/vnd.google-apps.folder' "
        "and trashed = false"
    )

    result = service.files().list(
        q=query,
        spaces="drive",
        corpora="allDrives",
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        fields="files(id,name,webViewLink,mimeType)",
        orderBy="name"
    ).execute()

    return result.get("files", [])

# ============================================================
# ANALYZER SUMMARY
# ============================================================

def show_analyzer_summary(df):

    # --------------------------------------------------------
    # CSS
    # --------------------------------------------------------

    st.markdown("""
    <style>

    /* =====================================================
       PAGE BACKGROUND
       ===================================================== */

    .stApp {
        background: #FFFFFF !important;
        background-image: none !important;
    }

    [data-testid="stAppViewContainer"] {
        background: #FFFFFF !important;
    }

    [data-testid="stMainBlockContainer"] {
        background: #FFFFFF !important;
    }


    /* =====================================================
       SUMMARY TITLE
       ===================================================== */

    .summary-title {
        font-size: 30px;
        font-weight: 800;
        color: #063B70;
        text-align: center;
        margin-bottom: 15px;
    }


    /* =====================================================
       FILTER BOX
       ===================================================== */

    .filter-box {
        background: #FFFFFF;
        border: 1px solid #D6E6F5;
        border-radius: 8px;
        padding: 10px 14px 12px 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    .filter-label {
        font-size: 16px;
        font-weight: 800;
        color: #063B70;
        margin-bottom: 5px;
    }


    /* =====================================================
       SELECTBOX
       ===================================================== */

    div[data-testid="stSelectbox"] label {
        color: #063B70 !important;
        font-weight: 700 !important;
    }

    div[data-testid="stSelectbox"] > div {
        color: #063B70 !important;
    }

    div[data-baseweb="select"] {
        background: #FFFFFF !important;
        border-radius: 7px !important;
    }

    div[data-baseweb="select"] > div {
        background: #FFFFFF !important;
        color: #063B70 !important;
        border: 1px solid #9DB7D0 !important;
        border-radius: 7px !important;
    }

    div[data-baseweb="select"] span {
        color: #063B70 !important;
    }


    /* =====================================================
       SUMMARY TABLE
       ===================================================== */

    .summary-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 16px;
        font-family: Arial, sans-serif;
        background: #FFFFFF;
    }


    /* =====================================================
       TABLE HEADER
       ===================================================== */

    .summary-table th {
        background: #174F86;
        color: #FFFFFF;
        padding: 12px 10px;
        text-align: center;
        font-weight: 700;
        border: 1px solid #FFFFFF;
    }


    /* =====================================================
       NORMAL TABLE DATA
       ===================================================== */

    .summary-table td {
        padding: 9px 12px;
        border: 1px solid #D0D7DE;
        background: #FFFFFF;
        color: #063B70;
    }


    /* =====================================================
       DEPARTMENT
       LEFT ALIGNED
       ===================================================== */

    .department-cell {
        background: #FFFFFF !important;
        color: #063B70 !important;
        font-weight: 800;
        text-align: left !important;
        vertical-align: middle;
        font-size: 17px;
        padding-left: 20px !important;
    }


    /* =====================================================
       MAKE / OEM
       ===================================================== */

    .make-cell {
        text-align: left;
        padding-left: 25px !important;
        color: #063B70 !important;
    }


    /* =====================================================
       QUANTITY
       ===================================================== */

    .qty-cell {
        text-align: center;
        font-weight: 600;
        color: #063B70 !important;
    }


    /* =====================================================
       DEPARTMENT TOTAL
       ===================================================== */

    .department-total td {
        background: #C9E3F8 !important;
        color: #063B70 !important;
        font-weight: 800;
    }

    .department-total .qty-cell {
        text-align: center;
        font-size: 17px;
    }


    /* =====================================================
       GRAND TOTAL
       ===================================================== */

    .grand-total td {
        background: #174F86 !important;
        color: #FFFFFF !important;
        font-weight: 800;
        font-size: 18px;
        padding: 12px;
    }

    .grand-total .qty-cell {
        text-align: center;
        font-size: 20px;
    }


    </style>
    """, unsafe_allow_html=True)


    # --------------------------------------------------------
    # FIND REQUIRED COLUMNS
    # --------------------------------------------------------

    department_col = None
    make_col = None
    quantity_col = None

    # Department column
    for col in df.columns:

        if str(col).strip().lower() in [
            "department",
            "dept",
            "department name",
            "area"
        ]:

            department_col = col
            break


    # Make / OEM column
    for col in df.columns:

        if str(col).strip().lower() in [
            "make",
            "oem",
            "make/oem",
            "make / oem",
            "manufacturer",
            "make oem"
        ]:

            make_col = col
            break


    # Quantity column
    for col in df.columns:

        if str(col).strip().lower() in [
            "quantity installed",
            "qty installed",
            "installed qty",
            "installed quantity",
            "quantity",
            "qty",
            "quantity available"
        ]:

            quantity_col = col
            break


    # --------------------------------------------------------
    # CHECK COLUMNS
    # --------------------------------------------------------

    if department_col is None:

        st.error("Department column not found.")

        st.write(
            "Available columns:",
            list(df.columns)
        )

        return


    if make_col is None:

        st.error("Make/OEM column not found.")

        st.write(
            "Available columns:",
            list(df.columns)
        )

        return


    if quantity_col is None:

        st.error("Quantity Installed column not found.")

        st.write(
            "Available columns:",
            list(df.columns)
        )

        return


    # --------------------------------------------------------
    # CLEAN DATA
    # --------------------------------------------------------

    summary_df = df[
        [
            department_col,
            make_col,
            quantity_col
        ]
    ].copy()


    summary_df.columns = [
        "Department",
        "Make / OEM",
        "Quantity Installed"
    ]


    summary_df["Department"] = (
        summary_df["Department"]
        .fillna("Others")
        .astype(str)
        .str.strip()
    )


    summary_df["Make / OEM"] = (
        summary_df["Make / OEM"]
        .fillna("Others")
        .astype(str)
        .str.strip()
    )


    summary_df["Quantity Installed"] = pd.to_numeric(
        summary_df["Quantity Installed"],
        errors="coerce"
    ).fillna(0)


    # Remove blank rows
    summary_df = summary_df[
        (summary_df["Department"] != "") &
        (summary_df["Make / OEM"] != "")
    ]


    # ========================================================
    # TITLE
    # ========================================================

    # ========================================================
    # FILTER CALLBACKS
    # ROBUST MUTUALLY EXCLUSIVE FILTERS
    # ========================================================

    def reset_oem_when_department_changes():
        st.session_state["analyzer_oem_widget"] = "ALL MAKE / OEM"
        st.session_state["analyzer_oem_search"] = "ALL MAKE / OEM"


    def reset_department_when_oem_changes():
        st.session_state["analyzer_department_widget"] = "ALL DEPARTMENTS"
        st.session_state["analyzer_department_search"] = "ALL DEPARTMENTS"


    # ========================================================
    # INITIAL FILTER VALUES
    # ========================================================

    if "analyzer_department_widget" not in st.session_state:
        st.session_state["analyzer_department_widget"] = "ALL DEPARTMENTS"

    if "analyzer_oem_widget" not in st.session_state:
        st.session_state["analyzer_oem_widget"] = "ALL MAKE / OEM"

    # Separate state values are retained for filtering.
    if "analyzer_department_search" not in st.session_state:
        st.session_state["analyzer_department_search"] = "ALL DEPARTMENTS"

    if "analyzer_oem_search" not in st.session_state:
        st.session_state["analyzer_oem_search"] = "ALL MAKE / OEM"


    # ========================================================
    # FILTER SECTION
    # SAME TWO-COLUMN LAYOUT AS BEFORE
    # ========================================================

    search_col1, search_col2 = st.columns(2)


    # ========================================================
    # DEPARTMENT FILTER
    # ========================================================

    with search_col1:

        st.markdown(
            """
            <div class="filter-label">
                     SEARCH BY DEPARTMENT
            </div>
            """,
            unsafe_allow_html=True
        )

        department_list = sorted(
            summary_df["Department"]
            .dropna()
            .unique()
            .tolist(),
            key=lambda x: str(x).lower()
        )

        department_options = ["ALL DEPARTMENTS"] + department_list

        if st.session_state["analyzer_department_widget"] not in department_options:
            st.session_state["analyzer_department_widget"] = "ALL DEPARTMENTS"

        selected_department = st.selectbox(
            "Department",
            department_options,
            key="analyzer_department_widget",
            label_visibility="collapsed",
            on_change=reset_oem_when_department_changes
        )

        st.session_state["analyzer_department_search"] = selected_department


    # ========================================================
    # MAKE / OEM FILTER
    # ========================================================

    with search_col2:

        st.markdown(
            """
            <div class="filter-label">
                 SEARCH BY MAKE / OEM
            </div>
            """,
            unsafe_allow_html=True
        )

        # Make / OEM is ALWAYS independent of Department.
        oem_list = sorted(
            summary_df["Make / OEM"]
            .dropna()
            .unique()
            .tolist(),
            key=lambda x: str(x).lower()
        )

        oem_options = ["ALL MAKE / OEM"] + oem_list

        if st.session_state["analyzer_oem_widget"] not in oem_options:
            st.session_state["analyzer_oem_widget"] = "ALL MAKE / OEM"

        selected_oem = st.selectbox(
            "Make / OEM",
            oem_options,
            key="analyzer_oem_widget",
            label_visibility="collapsed",
            on_change=reset_department_when_oem_changes
        )

        st.session_state["analyzer_oem_search"] = selected_oem

    # ========================================================
    # APPLY DEPARTMENT FILTER
    # ========================================================

    filtered_df = summary_df.copy()


    if selected_department != "ALL DEPARTMENTS":

        filtered_df = filtered_df[
            filtered_df["Department"]
            == selected_department
        ]


    # ========================================================
    # APPLY MAKE / OEM FILTER
    # ========================================================

    if selected_oem != "ALL MAKE / OEM":

        filtered_df = filtered_df[
            filtered_df["Make / OEM"]
            == selected_oem
        ]


    # ========================================================
    # NO DATA
    # ========================================================

    if filtered_df.empty:

        st.warning(
            "No analyzer data available for the selected filters."
        )

        return


    # ========================================================
    # GROUP DEPARTMENT + MAKE/OEM
    # ========================================================

    grouped = (

        filtered_df

        .groupby(
            [
                "Department",
                "Make / OEM"
            ],
            as_index=False
        )

        ["Quantity Installed"]

        .sum()
    )


    grouped = grouped.sort_values(
        [
            "Department",
            "Make / OEM"
        ]
    )


    # ========================================================
    # CREATE HTML TABLE
    # ========================================================

    html = """

    <table class="summary-table">

        <thead>

            <tr>

                <th style="width:28%;">
                    Department
                </th>

                <th style="width:47%;">
                    Make / OEM
                </th>

                <th style="width:25%;">
                    Quantity Installed
                </th>

            </tr>

        </thead>

        <tbody>

    """


    grand_total = 0


    # ========================================================
    # DEPARTMENT-WISE DISPLAY
    # ========================================================

    for department, dept_data in grouped.groupby(
        "Department",
        sort=False
    ):

        dept_total = (
            dept_data["Quantity Installed"]
            .sum()
        )


        grand_total += dept_total


        first_row = True

        rowspan = len(dept_data)


        for _, row in dept_data.iterrows():

            html += "<tr>"


            # ------------------------------------------------
            # DEPARTMENT
            # ------------------------------------------------

            if first_row:

                html += f"""

                <td
                    class="department-cell"
                    rowspan="{rowspan}"
                >

                    {department}

                </td>

                """

                first_row = False


            # ------------------------------------------------
            # MAKE / OEM
            # ------------------------------------------------

            html += f"""

                <td class="make-cell">

                    {row['Make / OEM']}

                </td>


                <td class="qty-cell">

                    {int(row['Quantity Installed'])}

                </td>

            </tr>

            """


        # ----------------------------------------------------
        # DEPARTMENT TOTAL
        # ----------------------------------------------------

        html += f"""

        <tr class="department-total">

            <td>

                {department} Total

            </td>


            <td></td>


            <td class="qty-cell">

                {int(dept_total)}

            </td>

        </tr>

        """


    # ========================================================
    # GRAND TOTAL
    # ========================================================

    html += f"""

        <tr class="grand-total">

            <td>

                GRAND TOTAL

            </td>


            <td></td>


            <td class="qty-cell">

                {int(grand_total)}

            </td>

        </tr>


        </tbody>

    </table>

    """


    # ========================================================
    # DISPLAY
    # ========================================================

    st.html(html)
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
            transform: translateY(0px);
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

    margin-top: -155px;
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
        now = datetime.now()
        current_date = now.strftime("%d-%b-%Y")
        current_time = now.strftime("%I:%M:%S %p")
        # IMPORTANT:
        # HTML starts immediately after f"""
        # This prevents Streamlit from showing
        # HTML tags as text.

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

            if st.button(
                    "ANALYZER LIST",
                    use_container_width=True,
                    key="analyzer_list"
            ):
                st.session_state.page = "Analyzer"

                st.rerun()

            if st.button(
                    "ANALYZER SUMMARY",
                    use_container_width=True,
                    key="analyzer_summery"
            ):
                st.session_state.page = "Analyzer Summary"

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
                    "SYSTEM ARCHITECTURE",
                    use_container_width=True,
                    key="system_architecture"
            ):
                st.session_state.page = "SYSTEM ARCHITECTURE"

                st.session_state.system_architecture_department = None

                st.rerun()

            if st.button(
                    "LINK PAGE",
                    use_container_width=True,
                    key="link_page"
            ):
                st.session_state.page = "LINK PAGE"

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

            "Analyzer Summary":
                "ANALYZER SUMMARY",

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
                "SHIFT DATA",

            "SYSTEM ARCHITECTURE":
                "SYSTEM ARCHITECTURE"
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


  /* =================================================
   SYSTEM ARCHITECTURE DEPARTMENT BUTTONS
   SAME STYLE AS LINK PAGE BUTTONS ONLY
   ================================================= */

div[class*="st-key-architecture_department_"] div[data-testid="stButton"] {
    width: 100% !important;
    margin-top: 8px !important;
    margin-bottom: 14px !important;
}

div[class*="st-key-architecture_department_"] div[data-testid="stButton"] > button {

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

    box-shadow:
        0 7px 0 #041522,
        0 12px 20px rgba(0,0,0,0.30),
        0 0 10px rgba(30,140,220,0.25),
        inset 0 2px 2px rgba(255,255,255,0.35),
        inset 0 -5px 8px rgba(0,0,0,0.30) !important;

    transition: all 0.18s ease !important;
}

div[class*="st-key-architecture_department_"] div[data-testid="stButton"] > button p {
    color: white !important;
    font-size: 20px !important;
    font-weight: 800 !important;
    letter-spacing: 0.5px !important;
}

div[class*="st-key-architecture_department_"] div[data-testid="stButton"] > button:hover {

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

div[class*="st-key-architecture_department_"] div[data-testid="stButton"] > button:hover p {
    color: white !important;
}

div[class*="st-key-architecture_department_"] div[data-testid="stButton"] > button:active {

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
        # SAME PLATFORM / DESIGN AS ANALYZER SUMMARY
        # =================================================

        elif st.session_state.page == "Summary":

            # =================================================
            # INSTRUMENT SUMMARY
            # SAME PLATFORM / DESIGN AS ANALYZER SUMMARY
            # =================================================

            # -------------------------------------------------
            # CSS - SAME LOOK AS ANALYZER SUMMARY
            # -------------------------------------------------

            st.markdown("""
            <style>

            .stApp {
                background: #FFFFFF !important;
                background-image: none !important;
            }

            [data-testid="stAppViewContainer"] {
                background: #FFFFFF !important;
            }

            [data-testid="stMainBlockContainer"] {
                background: #FFFFFF !important;
            }

            .instrument-filter-label {
                font-size: 16px;
                font-weight: 800;
                color: #063B70;
                margin-bottom: 5px;
            }

            div[data-testid="stSelectbox"] label {
                color: #063B70 !important;
                font-weight: 700 !important;
            }

            div[data-testid="stSelectbox"] > div {
                color: #063B70 !important;
            }

            div[data-baseweb="select"] {
                background: #FFFFFF !important;
                border-radius: 7px !important;
            }

            div[data-baseweb="select"] > div {
                background: #FFFFFF !important;
                color: #063B70 !important;
                border: 1px solid #9DB7D0 !important;
                border-radius: 7px !important;
            }

            div[data-baseweb="select"] span {
                color: #063B70 !important;
            }

            .instrument-summary-table {
                width: 100%;
                border-collapse: collapse;
                font-size: 16px;
                font-family: Arial, sans-serif;
                background: #FFFFFF;
            }

            .instrument-summary-table th {
                background: #174F86;
                color: #FFFFFF;
                padding: 12px 10px;
                text-align: center;
                font-weight: 700;
                border: 1px solid #FFFFFF;
            }

            .instrument-summary-table td {
                padding: 9px 12px;
                border: 1px solid #D0D7DE;
                background: #FFFFFF;
                color: #063B70;
            }

            .instrument-department-cell {
                background: #FFFFFF !important;
                color: #063B70 !important;
                font-weight: 800;
                text-align: left !important;
                vertical-align: middle;
                font-size: 17px;
                padding-left: 20px !important;
            }

            .instrument-type-cell {
                text-align: left;
                padding-left: 25px !important;
                color: #063B70 !important;
            }

            .instrument-qty-cell {
                text-align: center;
                font-weight: 600;
                color: #063B70 !important;
            }

            .instrument-department-total td {
                background: #C9E3F8 !important;
                color: #063B70 !important;
                font-weight: 800;
            }

            .instrument-department-total .instrument-qty-cell {
                text-align: center;
                font-size: 17px;
            }

            .instrument-grand-total td {
                background: #174F86 !important;
                color: #FFFFFF !important;
                font-weight: 800;
                font-size: 18px;
                padding: 12px;
            }

            .instrument-grand-total .instrument-qty-cell {
                text-align: center;
                font-size: 20px;
            }

            </style>
            """, unsafe_allow_html=True)

            # -------------------------------------------------
            # LOAD DATA
            # -------------------------------------------------

            df = load_sheet("Sheet1")

            # Clean column names
            df.columns = (
                df.columns
                .astype(str)
                .str.strip()
            )

            # -------------------------------------------------
            # CHECK REQUIRED COLUMNS
            # -------------------------------------------------

            required_columns = [
                "AREA",
                "INSTRUMENT TYPE",
                "INSTALLED QTY"
            ]

            missing_columns = [
                col for col in required_columns
                if col not in df.columns
            ]

            if missing_columns:
                st.error(
                    "Required columns not found: "
                    + ", ".join(missing_columns)
                )
                st.write(
                    "Available columns:",
                    list(df.columns)
                )
                st.stop()

            # -------------------------------------------------
            # CLEAN DATA
            # -------------------------------------------------

            df["INSTALLED QTY"] = pd.to_numeric(
                df["INSTALLED QTY"],
                errors="coerce"
            ).fillna(0)

            df["AREA"] = (
                df["AREA"]
                .fillna("Others")
                .astype(str)
                .str.strip()
            )

            df["INSTRUMENT TYPE"] = (
                df["INSTRUMENT TYPE"]
                .fillna("Others")
                .astype(str)
                .str.strip()
            )

            # Remove blank rows
            df = df[
                (df["AREA"] != "") &
                (df["INSTRUMENT TYPE"] != "")
            ].copy()

            # =================================================
            # FILTER CALLBACKS
            # MUTUALLY EXCLUSIVE FILTERS
            # =================================================

            def reset_instrument_type_when_department_changes():
                st.session_state[
                    "instrument_summary_type"
                ] = "ALL INSTRUMENT TYPES"

            def reset_department_when_instrument_type_changes():
                st.session_state[
                    "instrument_summary_department"
                ] = "ALL DEPARTMENTS"

            # =================================================
            # INITIAL FILTER VALUES
            # =================================================

            if "instrument_summary_department" not in st.session_state:
                st.session_state[
                    "instrument_summary_department"
                ] = "ALL DEPARTMENTS"

            if "instrument_summary_type" not in st.session_state:
                st.session_state[
                    "instrument_summary_type"
                ] = "ALL INSTRUMENT TYPES"

            # =================================================
            # FILTER SECTION
            # SAME TWO-COLUMN LAYOUT AS ANALYZER SUMMARY
            # =================================================

            search_col1, search_col2 = st.columns(2)

            # =================================================
            # SEARCH BY DEPARTMENT
            # =================================================

            with search_col1:

                st.markdown(
                    """
                    <div class="instrument-filter-label">
                        SEARCH BY DEPARTMENT
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                department_list = sorted(
                    df["AREA"]
                    .dropna()
                    .unique()
                    .tolist(),
                    key=lambda x: str(x).lower()
                )

                department_options = [
                    "ALL DEPARTMENTS"
                ] + department_list

                # Safety check for stale session-state values
                if st.session_state[
                    "instrument_summary_department"
                ] not in department_options:
                    st.session_state[
                        "instrument_summary_department"
                    ] = "ALL DEPARTMENTS"

                selected_department = st.selectbox(
                    "Department",
                    department_options,
                    key="instrument_summary_department",
                    label_visibility="collapsed",
                    on_change=reset_instrument_type_when_department_changes
                )

            # =================================================
            # SEARCH BY INSTRUMENT TYPE
            # =================================================

            with search_col2:

                st.markdown(
                    """
                    <div class="instrument-filter-label">
                        SEARCH BY INSTRUMENT TYPE
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # IMPORTANT:
                # Instrument Type is ALWAYS independent of Department.
                instrument_type_list = sorted(
                    df["INSTRUMENT TYPE"]
                    .dropna()
                    .unique()
                    .tolist(),
                    key=lambda x: str(x).lower()
                )

                instrument_type_options = [
                    "ALL INSTRUMENT TYPES"
                ] + instrument_type_list

                # Safety check for stale session-state values
                if st.session_state[
                    "instrument_summary_type"
                ] not in instrument_type_options:
                    st.session_state[
                        "instrument_summary_type"
                    ] = "ALL INSTRUMENT TYPES"

                selected_instrument_type = st.selectbox(
                    "Instrument Type",
                    instrument_type_options,
                    key="instrument_summary_type",
                    label_visibility="collapsed",
                    on_change=reset_department_when_instrument_type_changes
                )

            # =================================================
            # APPLY FILTERS
            # =================================================

            filtered_df = df.copy()

            if selected_department != "ALL DEPARTMENTS":
                filtered_df = filtered_df[
                    filtered_df["AREA"] == selected_department
                ]

            if selected_instrument_type != "ALL INSTRUMENT TYPES":
                filtered_df = filtered_df[
                    filtered_df["INSTRUMENT TYPE"]
                    == selected_instrument_type
                ]

            # =================================================
            # NO DATA
            # =================================================

            if filtered_df.empty:
                st.warning(
                    "No instrument data available "
                    "for the selected filters."
                )
                st.stop()

            # =================================================
            # GROUP DEPARTMENT + INSTRUMENT TYPE
            # =================================================

            grouped = (
                filtered_df
                .groupby(
                    ["AREA", "INSTRUMENT TYPE"],
                    as_index=False
                )["INSTALLED QTY"]
                .sum()
            )

            grouped = grouped.sort_values(
                ["AREA", "INSTRUMENT TYPE"],
                key=lambda col: col.astype(str).str.lower()
            )

            # =================================================
            # CREATE HTML TABLE
            # SAME STRUCTURE / STYLE AS ANALYZER SUMMARY
            # =================================================

            html = """
            <table class="instrument-summary-table">
                <thead>
                    <tr>
                        <th style="width:28%;">
                            Department
                        </th>
                        <th style="width:47%;">
                            Instrument Type
                        </th>
                        <th style="width:25%;">
                            Quantity Installed
                        </th>
                    </tr>
                </thead>
                <tbody>
            """

            grand_total = 0

            # =================================================
            # DEPARTMENT-WISE DISPLAY
            # =================================================

            for department, dept_data in grouped.groupby(
                "AREA",
                sort=False
            ):

                dept_total = dept_data["INSTALLED QTY"].sum()
                grand_total += dept_total

                first_row = True
                rowspan = len(dept_data)

                for _, row in dept_data.iterrows():

                    html += "<tr>"

                    if first_row:
                        html += f"""
                        <td
                            class="instrument-department-cell"
                            rowspan="{rowspan}"
                        >
                            {department}
                        </td>
                        """
                        first_row = False

                    html += f"""
                        <td class="instrument-type-cell">
                            {row["INSTRUMENT TYPE"]}
                        </td>

                        <td class="instrument-qty-cell">
                            {int(row["INSTALLED QTY"])}
                        </td>
                    </tr>
                    """

                # =================================================
                # DEPARTMENT TOTAL
                # =================================================

                html += f"""
                <tr class="instrument-department-total">
                    <td>
                        {department} Total
                    </td>
                    <td></td>
                    <td class="instrument-qty-cell">
                        {int(dept_total)}
                    </td>
                </tr>
                """

            # =================================================
            # GRAND TOTAL
            # =================================================

            html += f"""
                <tr class="instrument-grand-total">
                    <td>
                        GRAND TOTAL
                    </td>
                    <td></td>
                    <td class="instrument-qty-cell">
                        {int(grand_total)}
                    </td>
                </tr>
                </tbody>
            </table>
            """

            # =================================================
            # DISPLAY
            # =================================================

            st.html(html)

        # =================================================
        # ANALYZER SUMMARY
        # =================================================

        elif st.session_state.page == "Analyzer Summary":

            df = load_sheet("Analyzer")

            show_analyzer_summary(df)

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
        # SAME PLATFORM / DESIGN AS ANALYZER SUMMARY
        # =================================================

        elif st.session_state.page == "ValveSummary":

            # =================================================
            # CSS
            # SAME LOOK AS ANALYZER SUMMARY
            # =================================================

            st.markdown("""
            <style>

            .stApp {
                background: #FFFFFF !important;
                background-image: none !important;
            }

            [data-testid="stAppViewContainer"] {
                background: #FFFFFF !important;
            }

            [data-testid="stMainBlockContainer"] {
                background: #FFFFFF !important;
            }

            .cv-filter-label {
                font-size: 16px;
                font-weight: 800;
                color: #063B70;
                margin-bottom: 5px;
            }

            div[data-testid="stSelectbox"] label {
                color: #063B70 !important;
                font-weight: 700 !important;
            }

            div[data-baseweb="select"] {
                background: #FFFFFF !important;
                border-radius: 7px !important;
            }

            div[data-baseweb="select"] > div {
                background: #FFFFFF !important;
                color: #063B70 !important;
                border: 1px solid #9DB7D0 !important;
                border-radius: 7px !important;
            }

            div[data-baseweb="select"] span {
                color: #063B70 !important;
            }

            .cv-summary-table {
                width: 100%;
                border-collapse: collapse;
                font-size: 16px;
                font-family: Arial, sans-serif;
                background: #FFFFFF;
            }

            .cv-summary-table th {
                background: #174F86;
                color: #FFFFFF;
                padding: 12px 10px;
                text-align: center;
                font-weight: 700;
                border: 1px solid #FFFFFF;
            }

            .cv-summary-table td {
                padding: 9px 12px;
                border: 1px solid #D0D7DE;
                background: #FFFFFF;
                color: #063B70;
            }

            .cv-department-cell {
                background: #FFFFFF !important;
                color: #063B70 !important;
                font-weight: 800;
                text-align: left !important;
                vertical-align: middle;
                font-size: 17px;
                padding-left: 20px !important;
            }

            .cv-make-cell {
                text-align: left;
                padding-left: 25px !important;
                color: #063B70 !important;
            }

            .cv-qty-cell {
                text-align: center;
                font-weight: 600;
                color: #063B70 !important;
            }

            .cv-department-total td {
                background: #C9E3F8 !important;
                color: #063B70 !important;
                font-weight: 800;
            }

            .cv-department-total .cv-qty-cell {
                text-align: center;
                font-size: 17px;
            }

            .cv-grand-total td {
                background: #174F86 !important;
                color: #FFFFFF !important;
                font-weight: 800;
                font-size: 18px;
                padding: 12px;
            }

            .cv-grand-total .cv-qty-cell {
                text-align: center;
                font-size: 20px;
            }

            </style>
            """, unsafe_allow_html=True)

            # =================================================
            # LOAD CONTROL VALVE DATA
            # =================================================

            df = load_sheet("Sheet2")

            # =================================================
            # CLEAN COLUMN NAMES
            # =================================================

            df.columns = (
                df.columns
                .astype(str)
                .str.strip()
            )

            # =================================================
            # CHECK REQUIRED COLUMNS
            # =================================================

            required_columns = [
                "Area",
                "Make",
                "Quantity"
            ]

            missing_columns = [
                col
                for col in required_columns
                if col not in df.columns
            ]

            if missing_columns:
                st.error(
                    "Required columns not found: "
                    + ", ".join(missing_columns)
                )
                st.write(
                    "Available columns:",
                    list(df.columns)
                )
                st.stop()

            # =================================================
            # CLEAN DATA
            # =================================================

            df["Area"] = (
                df["Area"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            df["Make"] = (
                df["Make"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            df["Quantity"] = pd.to_numeric(
                df["Quantity"],
                errors="coerce"
            ).fillna(0)

            df = df[
                (df["Area"] != "") &
                (df["Make"] != "")
            ].copy()

            # =================================================
            # FILTER CALLBACKS
            # MUTUALLY EXCLUSIVE FILTERS
            # =================================================

            def reset_make_when_department_changes():
                st.session_state[
                    "control_valve_make_search"
                ] = "ALL MAKES"


            def reset_department_when_make_changes():
                st.session_state[
                    "control_valve_department_search"
                ] = "ALL DEPARTMENTS"


            # =================================================
            # INITIAL FILTER VALUES
            # =================================================

            if "control_valve_department_search" not in st.session_state:
                st.session_state[
                    "control_valve_department_search"
                ] = "ALL DEPARTMENTS"

            if "control_valve_make_search" not in st.session_state:
                st.session_state[
                    "control_valve_make_search"
                ] = "ALL MAKES"

            # =================================================
            # FILTER SECTION
            # SAME TWO-COLUMN LAYOUT AS ANALYZER SUMMARY
            # =================================================

            search_col1, search_col2 = st.columns(2)

            # =================================================
            # SEARCH BY DEPARTMENT
            # =================================================

            with search_col1:

                st.markdown(
                    """
                    <div class="cv-filter-label">
                        🏭 SEARCH BY DEPARTMENT
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                department_list = sorted(
                    df["Area"]
                    .dropna()
                    .unique()
                    .tolist(),
                    key=lambda x: str(x).lower()
                )

                department_options = [
                    "ALL DEPARTMENTS"
                ] + department_list

                # If the previous selection is no longer available,
                # safely return to ALL DEPARTMENTS.
                if (
                    st.session_state[
                        "control_valve_department_search"
                    ] not in department_options
                ):
                    st.session_state[
                        "control_valve_department_search"
                    ] = "ALL DEPARTMENTS"

                selected_department = st.selectbox(
                    "Department",
                    department_options,
                    key="control_valve_department_search",
                    label_visibility="collapsed",
                    on_change=reset_make_when_department_changes
                )

            # =================================================
            # SEARCH BY MAKE
            # =================================================

            with search_col2:

                st.markdown(
                    """
                    <div class="cv-filter-label">
                        🔧 SEARCH BY MAKE
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # IMPORTANT:
                # Make is ALWAYS independent of Department.
                make_list = sorted(
                    df["Make"]
                    .dropna()
                    .unique()
                    .tolist(),
                    key=lambda x: str(x).lower()
                )

                make_options = [
                    "ALL MAKES"
                ] + make_list

                # If the previous selection is no longer available,
                # safely return to ALL MAKES.
                if (
                    st.session_state[
                        "control_valve_make_search"
                    ] not in make_options
                ):
                    st.session_state[
                        "control_valve_make_search"
                    ] = "ALL MAKES"

                selected_make = st.selectbox(
                    "Make",
                    make_options,
                    key="control_valve_make_search",
                    label_visibility="collapsed",
                    on_change=reset_department_when_make_changes
                )

            # =================================================
            # APPLY DEPARTMENT FILTER
            # =================================================

            filtered_df = df.copy()

            if selected_department != "ALL DEPARTMENTS":
                filtered_df = filtered_df[
                    filtered_df["Area"]
                    == selected_department
                ]

            # =================================================
            # APPLY MAKE FILTER
            # =================================================

            if selected_make != "ALL MAKES":
                filtered_df = filtered_df[
                    filtered_df["Make"]
                    == selected_make
                ]

            # =================================================
            # NO DATA
            # =================================================

            if filtered_df.empty:
                st.warning(
                    "No control valve data available "
                    "for the selected filter."
                )
                st.stop()

            # =================================================
            # GROUP DEPARTMENT + MAKE
            # =================================================

            grouped = (
                filtered_df
                .groupby(
                    ["Area", "Make"],
                    as_index=False
                )["Quantity"]
                .sum()
            )

            grouped = grouped.sort_values(
                ["Area", "Make"],
                key=lambda col: col.astype(str).str.lower()
            )

            # =================================================
            # CREATE HTML TABLE
            # SAME STRUCTURE AS ANALYZER SUMMARY
            # =================================================

            html = """
            <table class="cv-summary-table">
                <thead>
                    <tr>
                        <th style="width:28%;">
                            Department
                        </th>
                        <th style="width:47%;">
                            Make
                        </th>
                        <th style="width:25%;">
                            Quantity Installed
                        </th>
                    </tr>
                </thead>
                <tbody>
            """

            grand_total = 0

            # =================================================
            # DEPARTMENT-WISE DISPLAY
            # =================================================

            for department, dept_data in grouped.groupby(
                "Area",
                sort=False
            ):

                dept_total = dept_data["Quantity"].sum()
                grand_total += dept_total

                first_row = True
                rowspan = len(dept_data)

                for _, row in dept_data.iterrows():

                    html += "<tr>"

                    if first_row:
                        html += f"""
                        <td
                            class="cv-department-cell"
                            rowspan="{rowspan}"
                        >
                            {department}
                        </td>
                        """
                        first_row = False

                    html += f"""
                        <td class="cv-make-cell">
                            {row["Make"]}
                        </td>

                        <td class="cv-qty-cell">
                            {int(row["Quantity"])}
                        </td>
                    </tr>
                    """

                # =================================================
                # DEPARTMENT TOTAL
                # =================================================

                html += f"""
                <tr class="cv-department-total">
                    <td>
                        {department} Total
                    </td>
                    <td></td>
                    <td class="cv-qty-cell">
                        {int(dept_total)}
                    </td>
                </tr>
                """

            # =================================================
            # GRAND TOTAL
            # =================================================

            html += f"""
                <tr class="cv-grand-total">
                    <td>
                        GRAND TOTAL
                    </td>
                    <td></td>
                    <td class="cv-qty-cell">
                        {int(grand_total)}
                    </td>
                </tr>
                </tbody>
            </table>
            """

            # =================================================
            # DISPLAY TABLE
            # =================================================

            st.html(html)

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

        elif st.session_state.page == "LINK PAGE":

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
        # SYSTEM ARCHITECTURE
        # =================================================

        elif st.session_state.page == "SYSTEM ARCHITECTURE":

            root_folder = get_system_architecture_folder()

            if root_folder is None:

                st.error(
                    " "
                    "not found in Google Drive."
                )

            else:

                selected_department = st.session_state.get(
                    "system_architecture_department",
                    None
                )

                # =============================================
                # DEPARTMENT LIST
                # =============================================

                if selected_department is None:

                    departments = get_department_folders(
                        root_folder["id"]
                    )

                    if not departments:
                        st.warning("No department folders found.")

                    else:

                        for i in range(0, len(departments), 4):

                            cols = st.columns(4)

                            for col, department in zip(
                                cols,
                                departments[i:i + 4]
                            ):

                                with col:

                                    if st.button(
                                        department["name"],
                                        use_container_width=True,
                                        key=f"architecture_department_{department['id']}"
                                    ):

                                        st.session_state.system_architecture_department = department["id"]
                                        st.session_state.system_architecture_department_name = department["name"]
                                        st.rerun()

                # =============================================
                # DOCUMENT LIST
                # =============================================

                else:

                    department_name = st.session_state.get(
                        "system_architecture_department_name",
                        "DEPARTMENT"
                    )

                    st.markdown(
                        f"""
                        <h2 style="
                            text-align:center;
                            color:#12395f;
                            margin-bottom:20px;
                        ">
                            {department_name}
                        </h2>
                        """,
                        unsafe_allow_html=True
                    )

                    if st.button(
                        "⬅ BACK TO DEPARTMENTS",
                        key="architecture_back"
                    ):

                        st.session_state.system_architecture_department = None
                        st.session_state.system_architecture_department_name = None
                        st.rerun()

                    documents = get_department_documents(
                        selected_department
                    )

                    if not documents:
                        st.warning("No documents found in this department.")

                    else:

                        for i in range(0, len(documents), 3):

                            cols = st.columns(3)

                            for col, document in zip(
                                cols,
                                documents[i:i + 3]
                            ):

                                with col:

                                    st.link_button(
                                        f"📄 {document['name']}",
                                        document["webViewLink"],
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
        # CONTROL VALVE LIST
        # =================================================

        elif st.session_state.page == "Analyzer":

            df = load_sheet("Analyzer")

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                height=500
            )
