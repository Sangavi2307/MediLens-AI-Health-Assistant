
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

# Optional AI explanation module
try:
    from modules.ai_explanation import ai_explain_report
except ImportError:
    ai_explain_report = None

# Optional OCR module
try:
    from ocr_service import extract_text_from_image
except ImportError:
    try:
        from modules.ocr_service import extract_text_from_image
    except ImportError:
        extract_text_from_image = None


# ==========================================
# CUSTOM CSS - PREMIUM MEDICAL THEME
# ==========================================

st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #F2F8FA;
    color: #183746;
}

/* Main content */
[data-testid="stMainBlockContainer"] {
    max-width: 1100px;
    padding-top: 2rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #123B4A;
}

[data-testid="stSidebar"] * {
    color: #FFFFFF;
}

/* Headings */
h1, h2, h3 {
    color: #123B4A !important;
}

/* Normal text */
.stApp p,
.stApp label {
    color: #294957;
}

/* Metric cards */
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

/* Buttons */
div.stButton > button {
    background-color: #087F75;
    color: #FFFFFF;
    border-radius: 10px;
    min-height: 44px;
    font-weight: 700;
    border: none;
}

div.stButton > button:hover {
    background-color: #065F59;
    color: #FFFFFF;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background-color: #FFFFFF;
    border: 1px dashed #087F75;
    border-radius: 12px;
    padding: 12px;
}

/* Input fields */
.stTextInput input,
.stTextArea textarea {
    background-color: #FFFFFF;
    color: #183746;
    border: 1px solid #B7CDD4;
    border-radius: 8px;
}

/* Expanders */
[data-testid="stExpander"] {
    background-color: #FFFFFF;
    border: 1px solid #D5E7EB;
    border-radius: 10px;
}

/* Alerts */
div[data-testid="stAlert"] {
    border-radius: 12px;
}

/* Divider */
hr {
    border-color: #C9DDE2;
}

/* Footer */
footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# SESSION STATE
# ==========================================

if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "ai_explanation" not in st.session_state:
    st.session_state.ai_explanation = None


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_result_count(result, status):
    """Count results matching a status."""

    if isinstance(result, pd.DataFrame):
        if "Status" in result.columns:
            return int(
                result["Status"].astype(str).str.lower()
                .eq(status.lower()).sum()
            )

    if isinstance(result, dict):
        for key in ("results", "tests", "lab_results"):
            if key in result:
                return get_result_count(result[key], status)

    if isinstance(result, list):
        count = 0

        for item in result:
            if isinstance(item, dict):
                item_status = str(
                    item.get("Status", item.get("status", ""))
                ).lower()

                if item_status == status.lower():
                    count += 1

        return count

    return 0


def display_analysis(result):
    """Display analyzer output in a readable format."""

    if isinstance(result, pd.DataFrame):
        st.dataframe(result, use_container_width=True)
        return

    if isinstance(result, dict):
        for key in ("results", "tests", "lab_results"):
            if key in result:
                display_analysis(result[key])
                return

        st.json(result)
        return

    if isinstance(result, list):
        if result and all(isinstance(item, dict) for item in result):
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
    st.caption("AI Health Assistant")

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Medical Report Analysis",
            "AI Explanation",
            "About MediLens"
        ]
    )

    st.divider()

    st.caption("Your Health. Your Understanding.")


# ==========================================
# DASHBOARD
# ==========================================

if page == "Dashboard":

    st.title("Welcome to MediLens!")
    st.markdown(
        "Understand your medical reports with AI assistance."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Platform",
            value="AI Healthcare"
        )

    with col2:
        st.metric(
            label="Report Support",
            value="PDF / Image"
        )

    with col3:
        st.metric(
            label="Analysis",
            value="AI Assisted"
        )

    st.subheader("Our Services")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style="
            background:#123B4A;
            padding:22px;
            border-radius:14px;
            color:white;
            min-height:145px;
        ">
            <h3 style="color:white !important;">
                📄 Medical Report Analysis
            </h3>
            <p style="color:#D7E9EF;">
                Upload your medical report and
                understand your laboratory results.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="
            background:#087F75;
            padding:22px;
            border-radius:14px;
            color:white;
            min-height:145px;
        ">
            <h3 style="color:white !important;">
                ✨ AI Report Explanation
            </h3>
            <p style="color:#E1F5F1;">
                Get simple educational explanations
                of your medical report.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.success("Your MediLens dashboard is ready!")

    st.divider()

    st.subheader("Medical Disclaimer")

    st.info("""
    MediLens provides educational information only.

    It does not provide medical diagnosis or replace
    professional medical advice.

    Always consult a qualified healthcare professional
    before making medical decisions.
    """)


# ==========================================
# MEDICAL REPORT ANALYSIS
# ==========================================

elif page == "Medical Report Analysis":

    st.title("📄 Medical Report Analysis")

    st.write(
        "Upload your medical report to extract and analyze "
        "laboratory information."
    )

    uploaded_file = st.file_uploader(
        "Upload your medical report",
        type=["pdf", "png", "jpg", "jpeg", "bmp"],
        help="Maximum file size: 20 MB"
    )

    if uploaded_file is not None:

        if uploaded_file.size > 20 * 1024 * 1024:

            st.error("File size exceeds the 20 MB limit.")

        else:

            st.success(
                f"Uploaded successfully: {uploaded_file.name}"
            )

            if st.button("Extract Report Text"):

                try:

                    with st.spinner("Extracting report text..."):

                        uploaded_file.seek(0)

                        if uploaded_file.type == "application/pdf":

                            extracted_text = extract_text_from_pdf(
                                uploaded_file
                            )

                        elif extract_text_from_image is not None:

                            extracted_text = extract_text_from_image(
                                uploaded_file
                            )

                        else:

                            raise ImportError(
                                "Image OCR module is not available."
                            )

                        if not extracted_text or not str(
                            extracted_text
                        ).strip():

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

                except Exception as e:

                    st.error(f"Extraction error: {e}")

    if st.session_state.extracted_text:

        st.subheader("Extracted Report Text")

        st.text_area(
            "Report content",
            value=st.session_state.extracted_text,
            height=250,
            disabled=True
        )

        if st.button("Analyze Medical Report"):

            try:

                with st.spinner("Analyzing medical report..."):

                    result = analyze_report(
                        st.session_state.extracted_text
                    )

                    st.session_state.analysis_result = result
                    st.session_state.ai_explanation = None

                st.success("Medical report analysis completed!")

            except Exception as e:

                st.error(f"Analysis error: {e}")

    if st.session_state.analysis_result is not None:

        st.divider()

        st.subheader("Analysis Results")

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

        st.subheader("Laboratory Results")

        display_analysis(result)


# ==========================================
# AI EXPLANATION
# ==========================================

elif page == "AI Explanation":

    st.title("✨ AI Medical Report Explanation")

    st.write(
        "Get an easy-to-understand educational explanation "
        "of your medical report."
    )

    if not st.session_state.extracted_text:

        st.warning(
            "Please upload and extract a medical report "
            "from the Medical Report Analysis section first."
        )

    else:

        st.success("Medical report text is available.")

        if ai_explain_report is None:

            st.error(
                "AI explanation module is unavailable. "
                "Please check modules/ai_explanation.py."
            )

        else:

            if st.button("Generate AI Explanation"):

                try:

                    with st.spinner(
                        "Generating AI explanation..."
                    ):

                        explanation = ai_explain_report(
                            st.session_state.extracted_text
                        )

                        st.session_state.ai_explanation = explanation

                except Exception as e:

                    st.error(f"AI explanation error: {e}")

            if st.session_state.ai_explanation is not None:

                st.subheader("AI Explanation")

                st.markdown(
                    str(st.session_state.ai_explanation)
                )

                st.info(
                    "This explanation is for educational purposes "
                    "and is not a medical diagnosis."
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

    - Medical report upload
    - PDF text extraction
    - Image-based report extraction using OCR
    - Laboratory result analysis
    - Below, Within and Above reference range identification
    - AI-based educational report explanation

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

    st.info(
        "MediLens is an educational assistant, "
        "not a replacement for healthcare professionals."
    )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:#526F7C;">
        <p>© 2026 MediLens AI Health Assistant</p>
        <p>Understand Your Health Better.</p>
    </div>
    """,
    unsafe_allow_html=True
    )
