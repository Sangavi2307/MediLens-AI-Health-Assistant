
import streamlit as st
import pandas as pd
import re
import io
from datetime import datetime

st.set_page_config(
    page_title="MediLens | AI Health Assistant",
    page_icon="🩺",
    layout="wide"
)

# ---------------- SESSION STATE ----------------

if "profile" not in st.session_state:
    st.session_state.profile = {}

if "reports" not in st.session_state:
    st.session_state.reports = []

if "current_results" not in st.session_state:
    st.session_state.current_results = pd.DataFrame()

# ---------------- DESIGN ----------------

st.markdown("""
<style>
.stApp {
    background-color: #F5F8FC;
}
.main-title {
    font-size: 38px;
    font-weight: 800;
    color: #123B63;
}
.subtitle {
    color: #64748B;
    font-size: 16px;
}
div[data-testid="stMetric"] {
    background: white;
    padding: 16px;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🩺 MediLens</div>',
            unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">AI-Powered Personal Health Guidance Platform</div>',
    unsafe_allow_html=True
)

st.divider()

# ---------------- SIDEBAR ----------------

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Personal Health Profile",
        "Age-Based Screening",
        "Medical Report Upload",
        "Medical Test Analysis",
        "AI Report Explanation",
        "Health Risk Monitoring",
        "Multi-Report Tracking",
        "Next-Test Recommendations"
    ]
)

st.sidebar.info(
    "MediLens provides educational health information. "
    "It does not diagnose diseases or replace medical professionals."
)

# ---------------- PROFILE ----------------

if menu == "Personal Health Profile":

    st.header("Personal Health Profile")

    with st.form("profile_form"):
        name = st.text_input("Full Name")
        age = st.number_input("Age", min_value=1, max_value=120, value=25)
        gender = st.selectbox(
            "Gender",
            ["Prefer not to say", "Female", "Male", "Other"]
        )
        history = st.text_area("Previous Medical History")
        conditions = st.text_area("Existing Health Conditions")
        symptoms = st.text_area("Current Symptoms")

        submitted = st.form_submit_button("Save Profile")

        if submitted:
            st.session_state.profile = {
                "Name": name,
                "Age": age,
                "Gender": gender,
                "Medical History": history,
                "Existing Conditions": conditions,
                "Symptoms": symptoms
            }
            st.success("Profile saved for this session.")

    if st.session_state.profile:
        st.subheader("Your Profile")
        st.json(st.session_state.profile)

# ---------------- AGE SCREENING ----------------

elif menu == "Age-Based Screening":

    st.header("Age-Based Health Screening")

    profile = st.session_state.profile
    age = profile.get("Age")

    if age is None:
        st.warning("Please complete your Personal Health Profile first.")
    else:
        st.write(f"Screening information for age: **{age} years**")

        if age < 30:
            st.info(
                "Discuss routine preventive care and screening based "
                "on personal and family medical history."
            )
        elif age < 40:
            st.info(
                "Discuss blood pressure and diabetes screening, "
                "and other preventive checks based on risk factors."
            )
        elif age < 50:
            st.info(
                "Review blood pressure, diabetes and age-appropriate "
                "cancer screening eligibility with a healthcare professional."
            )
        else:
            st.info(
                "Review age-appropriate cancer screening, blood pressure, "
                "diabetes and other preventive health checks with a "
                "healthcare professional."
            )

        if profile.get("Gender") == "Female" and age >= 30:
            st.write(
                "Women's health: ask about eligibility for cervical "
                "and breast cancer screening."
            )

        st.warning(
            "These are general educational prompts, not a personal "
            "test prescription. Screening depends on local guidelines, "
            "medical history and individual risk."
        )

# ---------------- REPORT EXTRACTION ----------------

def extract_report(uploaded_file):
    file_bytes = uploaded_file.getvalue()
    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):
        try:
            import pymupdf

            document = pymupdf.open(
                stream=file_bytes,
                filetype="pdf"
            )

            text = ""
            for page in document:
                page_text = page.get_text()
                text += page_text + "\n"

                # OCR pages that contain no selectable text
                if not page_text.strip():
                    try:
                        import pytesseract
                        from PIL import Image

                        pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))
                        image = Image.open(
                            io.BytesIO(pix.tobytes("png"))
                        )
                        text += pytesseract.image_to_string(image) + "\n"
                    except Exception:
                        pass

            return text

        except Exception as error:
            st.error(f"PDF extraction error: {error}")
            return ""

    elif filename.endswith((".png", ".jpg", ".jpeg")):
        try:
            import pytesseract
            from PIL import Image

            image = Image.open(io.BytesIO(file_bytes))
            return pytesseract.image_to_string(image)

        except Exception as error:
            st.error(f"Image OCR error: {error}")
            return ""

    return ""

# ---------------- TEST ANALYSIS ----------------

def analyze_report(report_text):

    results = []

    # Recognizes lines containing a test value and a numeric range.
    pattern = re.compile(
        r"^\s*(.+?)\s+"
        r"([<>]?\s*\d+(?:\.\d+)?)\s*"
        r"([A-Za-zµμ/%^0-9._-]*)\s+"
        r"(\d+(?:\.\d+)?)\s*[-–]\s*"
        r"(\d+(?:\.\d+)?)\s*$"
    )

    for line in report_text.splitlines():
        match = pattern.match(line.strip())

        if not match:
            continue

        test = match.group(1).strip(" :-")
        value_text = match.group(2).replace(" ", "")
        unit = match.group(3).strip()
        low = float(match.group(4))
        high = float(match.group(5))

        if value_text.startswith(("<", ">")):
            continue

        try:
            value = float(value_text)
        except ValueError:
            continue

        if low > high:
            continue

        if value < low:
            status = "Below Normal"
        elif value > high:
            status = "Above Normal"
        else:
            status = "Within Normal Range"

        results.append({
            "Test": test,
            "Result": value,
            "Unit": unit,
            "Reference Range": f"{low} - {high}",
            "Status": status
        })

    return pd.DataFrame(results)

# ---------------- REPORT UPLOAD ----------------

elif menu == "Medical Report Upload":

    st.header("Medical Report Upload")

    uploaded_file = st.file_uploader(
        "Upload your medical report",
        type=["pdf", "png", "jpg", "jpeg"]
    )

    if uploaded_file:
        if uploaded_file.size > 20 * 1024 * 1024:
            st.error("Maximum upload size is 20 MB.")
        else:
            if st.button("Extract Medical Information"):
                with st.spinner("Extracting report information..."):
                    extracted_text = extract_report(uploaded_file)

                st.session_state.extracted_text = extracted_text
                st.session_state.upload_name = uploaded_file.name

                if extracted_text.strip():
                    st.success("Report text extracted successfully.")
                    st.text_area(
                        "Extracted Report Text",
                        extracted_text,
                        height=300
                    )
                else:
                    st.warning(
                        "No text was extracted. The report may be "
                        "unclear, scanned or unsupported."
                    )

# ---------------- MEDICAL TEST ANALYSIS ----------------

elif menu == "Medical Test Analysis":

    st.header("Medical Test Analysis")

    report_text = st.session_state.get("extracted_text", "")

    if not report_text:
        st.info("Upload a medical report and extract its text first.")
    else:
        if st.button("Analyse Test Results"):
            results = analyze_report(report_text)
            st.session_state.current_results = results

            if not results.empty:
                st.session_state.reports.append({
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Results": results.copy()
                })
                st.success("Analysis completed.")
            else:
                st.warning(
                    "No test rows with numeric reference ranges were "
                    "recognized. Please check the extracted report text."
                )

        results = st.session_state.current_results

        if not results.empty:
            st.dataframe(results, use_container_width=True)

# ---------------- AI EXPLANATION ----------------

elif menu == "AI Report Explanation":

    st.header("Medical Report Explanation")

    results = st.session_state.current_results

    if results.empty:
        st.info("Analyse a medical report first.")
    else:
        for _, row in results.iterrows():
            st.subheader(row["Test"])
            st.write(f"Result: **{row['Result']} {row['Unit']}**")
            st.write(f"Reference range: {row['Reference Range']}")
            st.write(f"Status: **{row['Status']}**")

            if row["Status"] == "Within Normal Range":
                st.success(
                    "This value is within the reference range shown "
                    "in the report."
                )
            else:
                st.warning(
                    "This value is outside the reference range. "
                    "There can be several possible explanations. "
                    "Discuss it with a healthcare professional."
                )

# ---------------- HEALTH RISK MONITORING ----------------

elif menu == "Health Risk Monitoring":

    st.header("Health Risk Monitoring")

    results = st.session_state.current_results

    if results.empty:
        st.info("Analyse a report first.")
    else:
        abnormal = results[
            results["Status"] != "Within Normal Range"
        ]

        if abnormal.empty:
            st.success(
                "No values outside the supplied reference ranges "
                "were detected in the analysed results."
            )
        else:
            st.warning("The following results are outside their ranges:")
            st.dataframe(abnormal, use_container_width=True)

        st.caption(
            "An out-of-range result is not automatically an emergency. "
            "Urgency depends on the actual value, symptoms and clinical context."
        )

# ---------------- MULTI-REPORT TRACKING ----------------

elif menu == "Multi-Report Tracking":

    st.header("Multi-Report Health Tracking")

    reports = st.session_state.reports

    if not reports:
        st.info("Analyse and save reports to view your history.")
    else:
        history_rows = []

        for report in reports:
            for _, row in report["Results"].iterrows():
                history_rows.append({
                    "Date": report["Date"],
                    "Test": row["Test"],
                    "Result": row["Result"],
                    "Unit": row["Unit"]
                })

        history_df = pd.DataFrame(history_rows)

        st.dataframe(history_df, use_container_width=True)

        selected_test = st.selectbox(
            "Select a test to view its trend",
            sorted(history_df["Test"].unique())
        )

        chart_data = history_df[
            history_df["Test"] == selected_test
        ].set_index("Date")[["Result"]]

        st.line_chart(chart_data)

        st.caption(
            "Only reports analysed during this current session are "
            "included. Persistent secure storage will be added later."
        )

# ---------------- NEXT TEST RECOMMENDATIONS ----------------

elif menu == "Next-Test Recommendations":

    st.header("Smart Next-Test Recommendations")

    results = st.session_state.current_results

    if results.empty:
        st.info("Analyse a medical report first.")
    else:
        follow_up_guidance = {
            "hemoglobin": (
                "Discuss whether a complete blood count, ferritin, "
                "iron studies, vitamin B12 or folate evaluation is "
                "appropriate, depending on the clinical context."
            ),
            "glucose": (
                "Discuss whether repeat glucose testing or HbA1c "
                "is appropriate, depending on the test type and history."
            ),
            "vitamin d": (
                "Discuss whether follow-up vitamin D testing is "
                "appropriate based on symptoms and treatment history."
            ),
            "tsh": (
                "Discuss whether free T4 or repeat thyroid testing "
                "is appropriate based on symptoms and previous results."
            ),
            "creatinine": (
                "Discuss whether eGFR and urine albumin testing "
                "are appropriate based on medical history."
            )
        }

        for _, row in results.iterrows():
            if row["Status"] == "Within Normal Range":
                continue

            st.subheader(row["Test"])

            test_name = row["Test"].lower()
            found = False

            for key, guidance in follow_up_guidance.items():
                if key in test_name:
                    st.write(guidance)
                    found = True
                    break

            if not found:
                st.write(
                    "Discuss this result with a healthcare professional "
                    "to determine whether any follow-up testing is needed."
                )

        st.warning(
            "These are discussion prompts, not automatic test orders. "
            "Do not repeat or start tests without considering clinical advice."
        )

# ---------------- DASHBOARD ----------------

elif menu == "Dashboard":

    st.header("Welcome to MediLens")

    st.write(
        "Understand your medical reports, monitor your health "
        "information and explore preventive health guidance."
    )

    profile = st.session_state.profile
    results = st.session_state.current_results

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Profile",
        "Completed" if profile else "Not completed"
    )

    col2.metric(
        "Reports Analysed",
        len(st.session_state.reports)
    )

    abnormal_count = (
        len(results[results["Status"] != "Within Normal Range"])
        if not results.empty else 0
    )

    col3.metric("Out-of-range Results", abnormal_count)

    st.subheader("Your MediLens Journey")

    st.markdown("""
    1. Complete your personal health profile.
    2. Explore age-based screening information.
    3. Upload your medical report.
    4. Extract and analyse medical test results.
    5. Understand your report explanations.
    6. Monitor out-of-range results.
    7. Compare reports over time.
    8. Explore possible follow-up test information.
    """)

    st.info(
        "Start by completing your Personal Health Profile "
        "from the sidebar."
    )

# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "MediLens | AI-Powered Personal Health Guidance Platform"
)

st.caption(
    "Educational information only. Not a medical diagnosis or "
    "substitute for professional medical care."
)

