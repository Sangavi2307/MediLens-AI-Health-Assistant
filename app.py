import streamlit as st
import pandas as pd

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="MediLens AI Health Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# MODULE IMPORTS
# ==========================================

from modules.extractor import extract_text_from_pdf
from modules.analyzer import analyze_report

from modules.authentication import (
    initialize_auth_session,
    render_authentication,
    get_supabase_client,
    logout_user
)

from modules.health_profile import render_health_profile

# ==========================================
# AI EXPLANATION IMPORT
# ==========================================

try:
    from modules.ai_explanation import ai_explain_report
except ImportError:
    ai_explain_report = None

# ==========================================
# OCR IMPORT
# ==========================================

try:
    from modules.ocr_service import extract_text_from_image
except ImportError:
    try:
        from ocr_service import extract_text_from_image
    except ImportError:
        extract_text_from_image = None

# ==========================================
# CONSTANTS
# ==========================================

MAX_FILE_SIZE = 20 * 1024 * 1024

ALLOWED_FILE_TYPES = [
    "pdf", "png", "jpg", "jpeg", "bmp"
]

# ==========================================
# PROFESSIONAL MEDICAL THEME
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #F2F8FA;
    color: #183746;
}

[data-testid="stMainBlockContainer"] {
    max-width: 1150px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"] {
    background-color: #123B4A;
}

[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

h1, h2, h3 {
    color: #123B4A !important;
    font-weight: 700 !important;
}

.stApp p,
.stApp label {
    color: #294957;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    background-color: transparent;
    border-radius: 8px;
    padding: 8px;
}

div[data-testid="stMetric"] {
    background-color: #FFFFFF;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #D5E7EB;
    box-shadow: 0 3px 12px rgba(18,59,74,0.07);
}

div[data-testid="stMetricLabel"] {
    color: #526F7C !important;
}

div[data-testid="stMetricValue"] {
    color: #087F75 !important;
    font-weight: 800;
}

div.stButton > button {
    background-color: #087F75;
    color: #FFFFFF !important;
    border-radius: 10px;
    min-height: 44px;
    font-weight: 700;
    border: none;
}

div.stButton > button:hover {
    background-color: #065F59;
    color: #FFFFFF !important;
}

[data-testid="stFileUploader"] {
    background-color: #FFFFFF;
    border: 1px dashed #087F75;
    border-radius: 12px;
    padding: 12px;
}

.stTextInput input,
.stTextArea textarea {
    background-color: #FFFFFF;
    color: #183746;
    border: 1px solid #B7CDD4;
    border-radius: 8px;
}

.stSelectbox div[data-baseweb="select"] {
    background-color: #FFFFFF;
    border-radius: 8px;
}

[data-testid="stExpander"] {
    background-color: #FFFFFF;
    border: 1px solid #D5E7EB;
    border-radius: 10px;
}

.stTabs [data-baseweb="tab"] {
    color: #123B4A;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    color: #087F75 !important;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

[data-testid="stDataFrame"] {
    background-color: #FFFFFF;
    border-radius: 10px;
}

hr {
    border-color: #C9DDE2;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE
# ==========================================

defaults = {
    "extracted_text": "",
    "analysis_result": None,
    "ai_explanation": None,
    "selected_page": "Patient Health Profile",
    "is_guest": False
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ==========================================
# AUTHENTICATION AND GUEST MODE
# ==========================================

initialize_auth_session()

is_guest = st.session_state.get("is_guest", False)

if is_guest:

    # Guest users can enter without Supabase login.
    authenticated = True

else:

    # Existing Login and Create Account screen.
    authenticated = render_authentication()

    if not authenticated:

        st.divider()

        st.markdown("### Continue without an account")

        st.write(
            "You can use Medical Report Analysis and "
            "AI Explanation without creating an account."
        )

        if st.button(
            "Continue as Guest",
            use_container_width=True
        ):

            st.session_state["is_guest"] = True

            st.session_state["selected_page"] = (
                "Medical Report Analysis"
            )

            st.rerun()

        st.stop()

# ==========================================
# SUPABASE USER DETAILS
# ==========================================

supabase_client = get_supabase_client()

user_id = st.session_state.get("auth_user_id")

# Guest users do not need a Supabase user ID.
if not is_guest:

    if supabase_client is None or not user_id:

        st.error(
            "Your session is unavailable. "
            "Please log in again."
        )

        st.stop()

# ==========================================
# NAVIGATION CALLBACK
# ==========================================

def navigate_to_analysis():

    st.session_state["selected_page"] = (
        "Medical Report Analysis"
    )

# ==========================================
# RESULT COUNT HELPER
# ==========================================

def get_result_count(result, status):

    if isinstance(result, pd.DataFrame):

        if "Status" in result.columns:

            return int(
                result["Status"].astype(str)
                .str.lower()
                .eq(status.lower())
                .sum()
            )

    if isinstance(result, dict):

        for key in ("results", "tests", "lab_results"):

            if key in result:

                return get_result_count(
                    result[key],
                    status
                )

    if isinstance(result, list):

        count = 0

        for item in result:

            if isinstance(item, dict):

                item_status = str(
                    item.get(
                        "Status",
                        item.get("status", "")
                    )
                ).lower()

                if item_status == status.lower():
                    count += 1

        return count

    return 0

# ==========================================
# DISPLAY ANALYSIS RESULTS
# ==========================================

def display_analysis(result):

    if isinstance(result, pd.DataFrame):

        st.dataframe(
            result,
            use_container_width=True
        )

        return

    if isinstance(result, dict):

        for key in ("results", "tests", "lab_results"):

            if key in result:
                display_analysis(result[key])
                return

        st.json(result)
        return

    if isinstance(result, list):

        if result and all(
            isinstance(item, dict) for item in result
        ):

            st.dataframe(
                pd.DataFrame(result),
                use_container_width=True
            )

        else:
            st.write(result)

        return

    st.write(result)

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================

with st.sidebar:

    st.markdown("# 🩺 MediLens")

    st.caption("AI HEALTH ASSISTANT")

    st.divider()

    # Hide personal profile from guest users.
    if is_guest:

        pages = [
            "Medical Report Analysis",
            "AI Explanation",
            "About MediLens"
        ]

        st.info("You are using MediLens as a Guest.")

    else:

        pages = [
            "Patient Health Profile",
            "Medical Report Analysis",
            "AI Explanation",
            "About MediLens"
        ]

    # Ensure selected page is valid.
    if st.session_state["selected_page"] not in pages:

        st.session_state["selected_page"] = (
            "Medical Report Analysis"
            if is_guest
            else "Patient Health Profile"
        )

    page = st.radio(
        "Navigation",
        pages,
        key="selected_page"
    )

    st.divider()

    st.caption("Your Health. Your Understanding.")

    # Guest logout and normal logout are separate.
    if is_guest:

        if st.button(
            "Exit Guest Mode",
            use_container_width=True
        ):

            st.session_state["is_guest"] = False

            st.session_state["extracted_text"] = ""
            st.session_state["analysis_result"] = None
            st.session_state["ai_explanation"] = None

            st.session_state["selected_page"] = (
                "Patient Health Profile"
            )

            st.rerun()

    else:

        if st.button(
            "Logout",
            use_container_width=True
        ):

            logout_user(supabase_client)
            st.rerun()

# ==========================================
# PATIENT HEALTH PROFILE
# ==========================================

if page == "Patient Health Profile":

    if is_guest:

        st.warning(
            "Please log in to access your Patient Health Profile."
        )

    else:

        st.title("🩺 Patient Health Profile")

        st.write(
            "Manage your personal health information "
            "and medical details."
        )

        st.button(
            "Go to Medical Report Analysis ➜",
            use_container_width=True,
            on_click=navigate_to_analysis
        )

        st.divider()

        render_health_profile(
            supabase_client,
            user_id
        )

# ==========================================
# MEDICAL REPORT ANALYSIS
# ==========================================

elif page == "Medical Report Analysis":

    st.title("📄 Medical Report Analysis")

    st.write(
        "Upload your medical report to extract and "
        "analyze laboratory information."
    )

    if is_guest:

        st.info(
            "Guest Mode: You can analyze a report without "
            "creating an account. Your report is not saved "
            "to a personal Health Profile."
        )

    st.info(
        "Maximum upload size: 20 MB per file. "
        "Supported formats: PDF, JPG, JPEG, PNG and BMP."
    )

    uploaded_file = st.file_uploader(
        "Upload your medical report",
        type=ALLOWED_FILE_TYPES,
        help="Maximum file size: 20 MB",
        key="medical_report_uploader"
    )

    if uploaded_file is not None:

        if uploaded_file.size > MAX_FILE_SIZE:

            st.error(
                "File size exceeds 20 MB. "
                "Please upload a smaller report."
            )

        else:

            st.success(
                f"Uploaded successfully: {uploaded_file.name}"
            )

            st.caption(
                f"File size: "
                f"{uploaded_file.size / (1024 * 1024):.2f} MB"
            )

            if st.button(
                "Extract Report Text",
                use_container_width=True
            ):

                try:

                    with st.spinner(
                        "Extracting medical report text..."
                    ):

                        uploaded_file.seek(0)

                        file_extension = (
                            uploaded_file.name
                            .lower()
                            .rsplit(".", 1)[-1]
                        )

                        if file_extension == "pdf":

                            extracted_text = extract_text_from_pdf(
                                uploaded_file
                            )

                        elif file_extension in [
                            "jpg", "jpeg", "png", "bmp"
                        ]:

                            if extract_text_from_image is None:

                                raise ImportError(
                                    "Image OCR module is unavailable. "
                                    "Check modules/ocr_service.py."
                                )

                            extracted_text = extract_text_from_image(
                                uploaded_file
                            )

                        else:

                            raise ValueError(
                                "Unsupported file format."
                            )

                        if (
                            not extracted_text
                            or not str(extracted_text).strip()
                        ):

                            st.warning(
                                "No readable text was found. "
                                "Please upload a clearer report."
                            )

                        else:

                            st.session_state.extracted_text = str(
                                extracted_text
                            )

                            st.session_state.analysis_result = None
                            st.session_state.ai_explanation = None

                            st.success(
                                "Report text extracted successfully!"
                            )

                except Exception as error:

                    st.error(
                        f"Extraction error: {error}"
                    )

    # ======================================
    # EXTRACTED REPORT TEXT
    # ======================================

    if st.session_state.extracted_text:

        st.divider()

        st.subheader("📋 Extracted Report Text")

        st.text_area(
            "Report content",
            value=st.session_state.extracted_text,
            height=250,
            disabled=True
        )

        if st.button(
            "Analyze Medical Report",
            use_container_width=True
        ):

            try:

                with st.spinner(
                    "Analyzing medical report..."
                ):

                    result = analyze_report(
                        st.session_state.extracted_text
                    )

                    st.session_state.analysis_result = result
                    st.session_state.ai_explanation = None

                st.success(
                    "Medical report analysis completed!"
                )

            except Exception as error:

                st.error(
                    f"Analysis error: {error}"
                )

    # ======================================
    # ANALYSIS RESULTS
    # ======================================

    if st.session_state.analysis_result is not None:

        st.divider()

        st.subheader("📊 Analysis Results")

        result = st.session_state.analysis_result

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Below Range",
                get_result_count(result, "Below")
            )

        with col2:

            st.metric(
                "Within Range",
                get_result_count(result, "Within")
            )

        with col3:

            st.metric(
                "Above Range",
                get_result_count(result, "Above")
            )

        st.divider()

        st.subheader("Laboratory Results")

        display_analysis(result)

        st.caption(
            "Reference ranges can vary by laboratory, "
            "age and other individual factors. "
            "Consult a healthcare professional."
        )

# ==========================================
# AI EXPLANATION
# ==========================================

elif page == "AI Explanation":

    st.title("✨ AI Medical Report Explanation")

    st.write(
        "Get an easy-to-understand educational "
        "explanation of your medical report."
    )

    if not st.session_state.extracted_text:

        st.warning(
            "Please upload and extract a medical report "
            "from the Medical Report Analysis section first."
        )

    else:

        st.success(
            "Medical report text is available."
        )

        if ai_explain_report is None:

            st.error(
                "AI explanation module is unavailable. "
                "Please check modules/ai_explanation.py."
            )

        else:

            if st.button(
                "Generate AI Explanation",
                use_container_width=True
            ):

                try:

                    with st.spinner(
                        "Generating AI explanation..."
                    ):

                        explanation = ai_explain_report(
                            st.session_state.extracted_text
                        )

                        st.session_state.ai_explanation = (
                            explanation
                        )

                except Exception as error:

                    st.error(
                        f"AI explanation error: {error}"
                    )

            if st.session_state.ai_explanation is not None:

                st.divider()

                st.subheader("AI Explanation")

                st.markdown(
                    str(st.session_state.ai_explanation)
                )

                st.info(
                    "This explanation is for educational "
                    "purposes and is not a medical diagnosis. "
                    "Please consult a qualified healthcare professional."
                )

# ==========================================
# ABOUT MEDILENS
# ==========================================

elif page == "About MediLens":

    st.title("About MediLens")

    st.markdown("""
    MediLens is an AI-powered medical report understanding
    application designed to help users understand their
    laboratory reports in simple language.

    ### Main Features

    - Login and Create Account
    - Guest Mode
    - Patient health profile
    - Medical report upload
    - PDF text extraction
    - Image-based report extraction using OCR
    - Laboratory result analysis
    - Below, Within and Above reference range identification
    - AI-based educational report explanation

    ### Supported Upload Formats

    - PDF
    - JPG
    - JPEG
    - PNG
    - BMP

    ### Maximum Upload Size

    20 MB per file.

    ### Technology Stack

    - Python
    - Streamlit
    - Supabase
    - AI-based explanation
    - OCR
    - Pandas

    ### Our Goal

    To make medical report information easier to understand
    through accessible AI assistance.
    """)

    st.divider()

    st.info(
        "MediLens is an educational assistant, "
        "not a replacement for healthcare professionals."
    )

# ==========================================
# FOOTER
# ==========================================

st.divider()

st.markdown("""
<div style="
    text-align:center;
    color:#526F7C;
    padding:15px;
">
    <p><b>MediLens AI Health Assistant</b></p>
    <p>© 2026 MediLens. All rights reserved.</p>
    <p>Understand Your Health Better.</p>
</div>
""", unsafe_allow_html=True)
