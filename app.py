
import streamlit as st

from modules.authentication import render_authentication
from modules.extractor import extract_text_from_pdf
from modules.analyzer import analyze_report

# Optional AI explanation module
try:
    from modules.ai_explanation import ai_explain_report
except ImportError:
    ai_explain_report = None

# Optional image OCR module
try:
    from ocr_service import extract_text_from_image
except ImportError:
    try:
        from modules.ocr_service import extract_text_from_image
    except ImportError:
        extract_text_from_image = None


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
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #f5f8fc;
}

.main-title {
    color: #145374;
    font-size: 34px;
    font-weight: 800;
}

.subtitle {
    color: #607d8b;
    font-size: 16px;
}

div.stButton > button {
    border-radius: 10px;
    min-height: 42px;
    font-weight: 600;
}

div[data-testid="stMetric"] {
    background-color: white;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #e5edf5;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# AUTHENTICATION
# ==========================================

authenticated = render_authentication()

if not authenticated:
    st.stop()


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.title("🩺 MediLens")

    st.caption("AI Health Assistant")

    st.divider()

    st.write("Navigation")

    page = st.radio(
        "Choose a section",
        [
            "Dashboard",
            "Medical Report Analysis",
            "AI Explanation",
            "About MediLens"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.caption("Your Health. Your Understanding.")


# ==========================================
# DASHBOARD
# ==========================================

if page == "Dashboard":

    st.markdown(
        '<p class="main-title">Welcome to MediLens!</p>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="subtitle">'
        'Understand your medical reports with AI assistance.'
        '</p>',
        unsafe_allow_html=True
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Platform", "AI Healthcare")

    with col2:
        st.metric("Report Support", "PDF / Images")

    with col3:
        st.metric("Analysis", "AI Assisted")

    st.subheader("Our Services")

    col1, col2 = st.columns(2)

    with col1:
        st.info(
            "📄 Medical Report Analysis\n\n"
            "Upload your medical report and understand "
            "your laboratory results."
        )

    with col2:
        st.info(
            "🤖 AI Report Explanation\n\n"
            "Get simple educational explanations "
            "of your medical report."
        )

    st.success(
        "Your MediLens dashboard is ready!"
    )


# ==========================================
# MEDICAL REPORT ANALYSIS
# ==========================================

elif page == "Medical Report Analysis":

    st.title("📄 Medical Report Analysis")

    st.write(
        "Upload your medical report to extract and "
        "analyze the available information."
    )

    uploaded_file = st.file_uploader(
        "Upload your report",
        type=["pdf", "png", "jpg", "jpeg"]
    )

    if uploaded_file:

        if uploaded_file.size > 20 * 1024 * 1024:

            st.error("Maximum file size is 20 MB.")

            st.stop()

        st.success("Report uploaded successfully!")

        st.caption(
            f"File: {uploaded_file.name}"
        )

        if st.button(
            "Extract Report",
            use_container_width=True
        ):

            try:

                with st.spinner("Extracting report..."):

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

                        st.error(
                            "Image OCR module is not connected yet."
                        )

                        extracted_text = None

                    if extracted_text:

                        st.session_state["extracted_report"] = (
                            extracted_text
                        )

                        st.session_state.pop(
                            "analysis_results", None
                        )

                        st.session_state.pop(
                            "ai_explanation", None
                        )

                        st.success(
                            "Report text extracted successfully!"
                        )

                    else:

                        st.warning(
                            "No readable text found in the report."
                        )

            except Exception as error:

                st.error("Report extraction failed.")

                st.caption(
                    f"{type(error).__name__}: {error}"
                )


    # Display extracted report

    if st.session_state.get("extracted_report"):

        st.subheader("Extracted Report")

        st.text_area(
            "Medical Report Text",
            value=st.session_state["extracted_report"],
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

                    results = analyze_report(
                        st.session_state["extracted_report"]
                    )

                    st.session_state["analysis_results"] = results

                    st.session_state.pop(
                        "ai_explanation", None
                    )

                    st.success("Analysis completed!")

            except Exception as error:

                st.error("Analysis failed.")

                st.caption(
                    f"{type(error).__name__}: {error}"
                )


    # Display results

    results = st.session_state.get("analysis_results")

    if results is not None:

        st.divider()

        st.subheader("📊 Analysis Results")

        if isinstance(results, dict):

            below = results.get("Below", [])
            within = results.get("Within", [])
            above = results.get("Above", [])

            def get_count(value):
                if isinstance(value, (list, dict)):
                    return len(value)
                return 0

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Below Range",
                    get_count(below)
                )

            with col2:
                st.metric(
                    "Within Range",
                    get_count(within)
                )

            with col3:
                st.metric(
                    "Above Range",
                    get_count(above)
                )

            for heading, items in [
                ("Below Range", below),
                ("Within Range", within),
                ("Above Range", above)
            ]:

                with st.expander(heading):

                    st.write(items)

            other_results = {
                key: value
                for key, value in results.items()
                if key not in ["Below", "Within", "Above"]
            }

            if other_results:
                st.subheader("Additional Analysis")
                st.json(other_results)

        else:

            st.write(results)


# ==========================================
# AI EXPLANATION
# ==========================================

elif page == "AI Explanation":

    st.title("🤖 AI Medical Report Explanation")

    results = st.session_state.get("analysis_results")

    extracted_text = st.session_state.get(
        "extracted_report"
    )

    if not extracted_text:

        st.warning(
            "Please upload and extract a medical report first."
        )

    elif ai_explain_report is None:

        st.error(
            "AI explanation module is not connected. "
            "Please check modules/ai_explanation.py."
        )

    else:

        st.write(
            "Generate an educational explanation "
            "of your medical report."
        )

        if st.button(
            "Generate AI Explanation",
            use_container_width=True
        ):

            if results is None:

                st.warning(
                    "Please analyze the report first."
                )

            else:

                try:

                    with st.spinner(
                        "AI is preparing your explanation..."
                    ):

                        explanation = ai_explain_report(
                            extracted_text,
                            results
                        )

                        st.session_state["ai_explanation"] = (
                            explanation
                        )

                except Exception as error:

                    st.error(
                        "Unable to generate AI explanation."
                    )

                    st.caption(
                        f"{type(error).__name__}: {error}"
                    )

        if st.session_state.get("ai_explanation"):

            st.divider()

            st.subheader("Your Report Explained")

            st.markdown(
                st.session_state["ai_explanation"]
            )


# ==========================================
# ABOUT MEDILENS
# ==========================================

elif page == "About MediLens":

    st.title("About MediLens")

    st.write("""
    MediLens AI Health Assistant is designed to help
    people understand their medical reports.

    **Main Features**

    - Secure account authentication
    - Medical report upload
    - PDF and image text extraction
    - Laboratory result analysis
    - Below, Within and Above range classification
    - AI-powered educational explanations

    Our goal is to make medical information
    easier to understand.
    """)


# ==========================================
# MEDICAL DISCLAIMER
# ==========================================

st.divider()

st.info("""
**Medical Disclaimer**

MediLens provides educational information only.

It does not provide medical diagnosis or replace
professional medical advice.

Always consult a qualified healthcare professional
before making medical decisions.
""")


# ==========================================
# FOOTER
# ==========================================

st.caption(
    "© 2026 MediLens AI Health Assistant"
            )
