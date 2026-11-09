
import streamlit as st
import pandas as pd

from modules.authentication import (
    get_supabase_client,
    render_authentication
)

from modules.health_profile import render_health_profile
from modules.screening import render_screening

from modules.extractor import (
    extract_report_text
)

from modules.analyzer import (
    analyze_report,
    get_analysis_summary
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="MediLens - AI Health Assistant",
    page_icon="🏥",
    layout="wide"
)


# --------------------------------------------------
# APPLICATION HEADER
# --------------------------------------------------

st.title("🏥 MediLens")
st.subheader("AI-Powered Personal Health Guidance Platform")

st.write(
    "Understand your health reports and explore "
    "personalized educational health guidance."
)

st.divider()


# --------------------------------------------------
# USER AUTHENTICATION
# --------------------------------------------------

authenticated = render_authentication()

if not authenticated:
    st.info("Please log in or create an account to continue.")
    st.stop()


client = get_supabase_client()

if client is None:
    st.error("Unable to connect to the database.")
    st.stop()


user_id = st.session_state.get("auth_user_id")

if not user_id:
    st.warning("Please log in again.")
    st.stop()


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

st.sidebar.title("MediLens Navigation")

menu = st.sidebar.radio(
    "Select a Module",
    [
        "Dashboard",
        "Personal Health Profile",
        "Age-Based Health Screening",
        "Medical Report Upload",
        "Medical Test Analysis"
    ]
)

st.sidebar.divider()

st.sidebar.caption(
    "MediLens provides educational health information. "
    "It does not replace professional medical advice."
)


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

if menu == "Dashboard":

    st.title("Welcome to MediLens!")

    st.write(
        "Your personal health guidance dashboard."
    )

    st.subheader("Available Features")

    col1, col2 = st.columns(2)

    with col1:
        st.info(
            "**Personal Health Profile**\n\n"
            "Manage your personal and medical information."
        )

        st.info(
            "**Age-Based Health Screening**\n\n"
            "Explore general preventive health guidance."
        )

    with col2:
        st.info(
            "**Medical Report Upload**\n\n"
            "Upload PDF or image-based medical reports."
        )

        st.info(
            "**Medical Test Analysis**\n\n"
            "Review extracted medical test values and "
            "their configured reference ranges."
        )

    st.subheader("How MediLens Works")

    st.write(
        """
        1. Create your account and log in.
        2. Complete your personal health profile.
        3. Explore age-based screening information.
        4. Upload a medical report.
        5. Extract report text using OCR.
        6. Analyze supported medical test values.
        7. Review the educational analysis.
        """
    )


# --------------------------------------------------
# PERSONAL HEALTH PROFILE
# --------------------------------------------------

elif menu == "Personal Health Profile":

    render_health_profile(
        client,
        user_id
    )


# --------------------------------------------------
# AGE-BASED HEALTH SCREENING
# --------------------------------------------------

elif menu == "Age-Based Health Screening":

    render_screening(
        client,
        user_id
    )


# --------------------------------------------------
# MEDICAL REPORT UPLOAD
# --------------------------------------------------

elif menu == "Medical Report Upload":

    st.title("Medical Report Upload")

    st.write(
        "Upload your medical report in PDF, JPG or PNG format."
    )

    uploaded_file = st.file_uploader(
        "Choose your medical report",
        type=["pdf", "png", "jpg", "jpeg"],
        help="Maximum supported file size: 20 MB."
    )

    if uploaded_file is not None:

        file_size = len(uploaded_file.getvalue())

        if file_size > 20 * 1024 * 1024:

            st.error(
                "File size exceeds 20 MB. "
                "Please upload a smaller report."
            )

        else:

            st.success(
                f"Uploaded successfully: {uploaded_file.name}"
            )

            st.write(
                f"File size: {file_size / (1024 * 1024):.2f} MB"
            )

            if st.button(
                "Extract Medical Report Text",
                use_container_width=True
            ):

                with st.spinner(
                    "Extracting text from your report..."
                ):

                    extracted_text = extract_report_text(
                        uploaded_file
                    )

                if extracted_text:

                    st.session_state.extracted_report = (
                        extracted_text
                    )

                    st.session_state.report_filename = (
                        uploaded_file.name
                    )

                    st.success("Text extraction completed!")

                else:

                    st.warning(
                        "No readable text was found. "
                        "Please upload a clearer report."
                    )

    if st.session_state.get("extracted_report"):

        st.subheader("Extracted Medical Report")

        with st.expander(
            "View extracted report text",
            expanded=True
        ):

            st.text_area(
                "Extracted Text",
                value=st.session_state.extracted_report,
                height=300,
                disabled=True
            )

        st.info(
            "You can now open Medical Test Analysis "
            "from the sidebar."
        )


# --------------------------------------------------
# MEDICAL TEST ANALYSIS
# --------------------------------------------------

elif menu == "Medical Test Analysis":

    st.title("Medical Test Analysis")

    st.write(
        "Review supported test values extracted "
        "from your uploaded medical report."
    )

    report_text = st.session_state.get(
        "extracted_report",
        ""
    )

    if not report_text:

        st.warning(
            "Please upload a medical report and extract "
            "its text before starting the analysis."
        )

    else:

        if st.button(
            "Analyze Medical Report",
            use_container_width=True
        ):

            with st.spinner(
                "Analyzing medical test values..."
            ):

                results = analyze_report(report_text)

                st.session_state.analysis_results = results

        results = st.session_state.get(
            "analysis_results",
            None
        )

        if results is not None:

            if results:

                summary = get_analysis_summary(results)

                st.subheader("Analysis Summary")

                col1, col2, col3, col4 = st.columns(4)

                col1.metric(
                    "Below Range",
                    summary["Below"]
                )

                col2.metric(
                    "Within Range",
                    summary["Within"]
                )

                col3.metric(
                    "Above Range",
                    summary["Above"]
                )

                col4.metric(
                    "Needs Review",
                    summary["Needs review"]
                )

                st.divider()

                st.subheader("Medical Test Results")

                dataframe = pd.DataFrame(results)

                st.dataframe(
                    dataframe,
                    use_container_width=True,
                    hide_index=True
                )

                st.subheader("Result Interpretation")

                for result in results:

                    test_name = result["test_name"]
                    value = result["value"]
                    unit = result["unit"]
                    status = result["status"]
                    reference = result["reference_range"]

                    with st.expander(test_name):

                        st.write(f"**Result:** {value} {unit}")

                        st.write(
                            f"**Configured reference range:** "
                            f"{reference} {unit}"
                        )

                        st.write(f"**Status:** {status}")

                        if status == "Below":

                            st.warning(
                                "This value is below the "
                                "configured reference range."
                            )

                        elif status == "Above":

                            st.warning(
                                "This value is above the "
                                "configured reference range."
                            )

                        else:

                            st.success(
                                "This value is within the "
                                "configured reference range."
                            )

                st.caption(
                    "Only supported test names and simple "
                    "report formats are currently recognized. "
                    "Unrecognized tests are not included."
                )

            else:

                st.warning(
                    "No supported medical test values "
                    "were detected in the extracted text."
                )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "MediLens © 2026 | AI-Powered Personal Health "
    "Guidance Platform"
)

st.caption(
    "Medical Disclaimer: MediLens is an educational "
    "prototype. It does not diagnose diseases, prescribe "
    "medication or replace consultation with qualified "
    "healthcare professionals. Always discuss test results "
    "and medical decisions with a healthcare professional."
    )
