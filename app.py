
import streamlit as st
import pandas as pd
import json

from modules.authentication import (
    initialize_auth_session,
    get_supabase_client,
    render_authentication,
    logout_user
)

from modules.health_profile import render_health_profile

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image
from analyzer import analyze_report

try:
    from ai_explainer import ai_explain_report
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="MediLens AI Health Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==========================================
# PROFESSIONAL COLOUR THEME
# ==========================================

st.markdown(
    """
    <style>
    .stApp {
        background-color: #F2F8FA;
        color: #183B45;
    }

    [data-testid="stHeader"] {
        background-color: #F2F8FA;
    }

    h1, h2, h3 {
        color: #123B4A;
    }

    [data-testid="stSidebar"] {
        background-color: #123B4A;
    }

    [data-testid="stSidebar"] * {
        color: white;
    }

    div.stButton > button {
        background-color: #087F75;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.55rem 1rem;
        font-weight: 600;
    }

    div.stButton > button:hover {
        background-color: #06665F;
        color: white;
        border: none;
    }

    div[data-testid="stFormSubmitButton"] button {
        background-color: #087F75;
        color: white;
        border-radius: 8px;
        font-weight: 600;
    }

    [data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #DCE9ED;
        padding: 16px;
        border-radius: 10px;
    }

    .main-card {
        background-color: white;
        padding: 22px;
        border-radius: 12px;
        border: 1px solid #DCE9ED;
        margin-bottom: 15px;
    }

    .app-footer {
        text-align: center;
        color: #607D86;
        padding: 20px;
        font-size: 13px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================
# SESSION STATE
# ==========================================

def initialize_app_state():

    defaults = {
        "extracted_text": "",
        "analysis_result": None,
        "ai_explanation": None,
        "uploaded_file_name": None,
        "report_analyzed": False
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_app_state()


# ==========================================
# AUTHENTICATION
# ==========================================

initialize_auth_session()

authenticated = render_authentication()

if not authenticated:
    st.stop()


# ==========================================
# GET SUPABASE CLIENT AND USER ID
# ==========================================

supabase_client = get_supabase_client()

user_id = st.session_state.get("auth_user_id")

if supabase_client is None or not user_id:
    st.error("Your guest session is unavailable. Please try again.")
    st.stop()


# ==========================================
# APPLICATION HEADER
# ==========================================

st.markdown(
    """
    <div class="main-card">
        <h1>🩺 MediLens AI Health Assistant</h1>
        <p>
            Understand your medical reports with AI-powered
            educational explanations.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================
# HEALTH PROFILE - FIRST PAGE AFTER LOGIN
# ==========================================

st.header("👤 Patient Health Profile")

render_health_profile(supabase_client, user_id)

st.divider()


# ==========================================
# LOGOUT
# ==========================================

with st.expander("Account and Session"):

    st.write("You are currently using MediLens as a guest.")

    if st.button("Logout", key="logout_button"):
        logout_user(supabase_client)


# ==========================================
# MEDICAL REPORT UPLOAD
# ==========================================

st.header("📄 Medical Report Analysis")

st.write(
    "Upload your medical report in PDF or image format "
    "to understand the reported test results."
)

uploaded_file = st.file_uploader(
    "Upload your medical report",
    type=["pdf", "png", "jpg", "jpeg"],
    help="Maximum file size: 20 MB"
)


# ==========================================
# FILE SIZE VALIDATION
# ==========================================

MAX_FILE_SIZE = 20 * 1024 * 1024

if uploaded_file is not None:

    if uploaded_file.size > MAX_FILE_SIZE:

        st.error("File size exceeds the 20 MB limit.")

    else:

        st.success(
            f"Uploaded successfully: {uploaded_file.name}"
        )

        st.caption(
            f"File size: {uploaded_file.size / (1024 * 1024):.2f} MB"
        )

        # ==========================================
        # EXTRACT TEXT FROM PDF OR IMAGE
        # ==========================================

        if st.button(
            "Extract Medical Report Text",
            use_container_width=True
        ):

            try:

                with st.spinner("Extracting medical report text..."):

                    uploaded_file.seek(0)

                    file_extension = uploaded_file.name.lower()

                    if file_extension.endswith(".pdf"):

                        extracted_text = extract_text_from_pdf(
                            uploaded_file
                        )

                    else:

                        extracted_text = extract_text_from_image(
                            uploaded_file
                        )

                    if not extracted_text or not str(extracted_text).strip():

                        st.error(
                            "No readable text was found. "
                            "Please upload a clearer report."
                        )

                    else:

                        st.session_state.extracted_text = str(
                            extracted_text
                        )

                        st.session_state.uploaded_file_name = (
                            uploaded_file.name
                        )

                        st.session_state.analysis_result = None
                        st.session_state.ai_explanation = None
                        st.session_state.report_analyzed = False

                        st.success(
                            "Medical report text extracted successfully!"
                        )

            except Exception as error:

                st.error("Unable to extract text from the report.")

                st.caption(
                    f"{type(error).__name__}: {error}"
                )


# ==========================================
# DISPLAY EXTRACTED TEXT
# ==========================================

if st.session_state.extracted_text:

    st.subheader("Extracted Medical Report")

    st.text_area(
        "Report Text",
        value=st.session_state.extracted_text,
        height=250,
        disabled=True
    )


# ==========================================
# ANALYZE MEDICAL REPORT
# ==========================================

if st.session_state.extracted_text:

    if st.button(
        "🔍 Analyze Medical Report",
        use_container_width=True
    ):

        try:

            with st.spinner("Analyzing your medical report..."):

                result = analyze_report(
                    st.session_state.extracted_text
                )

                st.session_state.analysis_result = result
                st.session_state.report_analyzed = True
                st.session_state.ai_explanation = None

            st.success("Medical report analysis completed!")

        except Exception as error:

            st.error("Unable to analyze the medical report.")

            st.caption(
                f"{type(error).__name__}: {error}"
            )


# ==========================================
# ANALYSIS RESULTS
# ==========================================

def display_analysis(result):

    if result is None:
        return

    st.subheader("📊 Medical Report Analysis Results")

    # Handle dictionary results.
    if isinstance(result, dict):

        # Display count metrics when these values are provided
        # by the analyzer.
        below = result.get("below_count", result.get("below", 0))
        within = result.get("within_count", result.get("within", 0))
        above = result.get("above_count", result.get("above", 0))

        if all(
            isinstance(value, (int, float))
            for value in [below, within, above]
        ):

            col1, col2, col3 = st.columns(3)

            col1.metric("Below Range", below)
            col2.metric("Within Range", within)
            col3.metric("Above Range", above)

        # Display the complete result without discarding
        # fields that the analyzer may return.
        st.markdown("### Detailed Analysis")

        for key, value in result.items():

            if key in [
                "below_count",
                "within_count",
                "above_count",
                "below",
                "within",
                "above"
            ]:
                continue

            st.markdown(f"**{str(key).replace('_', ' ').title()}**")

            if isinstance(value, list):

                if value and all(
                    isinstance(item, dict) for item in value
                ):
                    st.dataframe(
                        pd.DataFrame(value),
                        use_container_width=True
                    )
                else:
                    for item in value:
                        st.write(f"• {item}")

            elif isinstance(value, dict):

                st.json(value)

            else:

                st.write(value)

    elif isinstance(result, pd.DataFrame):

        st.dataframe(
            result,
            use_container_width=True
        )

    elif isinstance(result, list):

        if result and all(
            isinstance(item, dict) for item in result
        ):
            st.dataframe(
                pd.DataFrame(result),
                use_container_width=True
            )
        else:
            for item in result:
                st.write(f"• {item}")

    else:

        st.write(result)


if st.session_state.analysis_result is not None:

    display_analysis(
        st.session_state.analysis_result
    )


# ==========================================
# AI EXPLANATION
# ==========================================

if st.session_state.analysis_result is not None:

    st.divider()

    st.header("🤖 AI Medical Report Explanation")

    st.write(
        "Get an educational explanation of your medical report "
        "in simple language."
    )

    if not AI_AVAILABLE:

        st.warning(
            "AI explanation module could not be imported. "
            "Check the module name and file location."
        )

    else:

        if st.button(
            "Generate AI Explanation",
            use_container_width=True
        ):

            try:

                with st.spinner(
                    "Generating your AI explanation..."
                ):

                    explanation = ai_explain_report(
                        st.session_state.extracted_text
                    )

                    st.session_state.ai_explanation = explanation

                st.success("AI explanation generated successfully!")

            except Exception as error:

                st.error("Unable to generate AI explanation.")

                st.caption(
                    f"{type(error).__name__}: {error}"
                )


# ==========================================
# DISPLAY AI EXPLANATION
# ==========================================

if st.session_state.ai_explanation:

    st.subheader("Medical Report Explanation")

    explanation = st.session_state.ai_explanation

    if isinstance(explanation, (dict, list)):

        st.json(explanation)

    else:

        st.markdown(str(explanation))


# ==========================================
# MEDICAL DISCLAIMER
# ==========================================

st.divider()

st.warning(
    """
    **Medical Disclaimer**

    MediLens provides AI-generated educational information
    to help users understand medical reports.

    It does not provide a medical diagnosis or replace
    professional medical advice.

    Always consult a qualified healthcare professional
    before making medical decisions.
    """
)


# ==========================================
# ABOUT MEDILENS
# ==========================================

with st.expander("About MediLens"):

    st.write(
        """
        MediLens AI Health Assistant helps users understand
        medical reports through text extraction, laboratory
        result analysis, and AI-generated explanations.

        The application supports patient health profiles
        and is designed to make medical information easier
        to understand.
        """
    )


# ==========================================
# FOOTER
# ==========================================

st.markdown(
    """
    <div class="app-footer">
        MediLens AI Health Assistant |
        Educational Health Information |
        © 2026 MediLens
    </div>
    """,
    unsafe_allow_html=True
)
