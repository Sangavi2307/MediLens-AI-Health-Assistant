
import streamlit as st


def get_screening_guidance(age, gender):
    """
    Provide general age-based preventive screening
    information. This is educational, not a diagnosis.
    """

    guidance = []

    if age < 18:
        guidance = [
            ("Growth and development",
             "Discuss growth, development and routine check-ups."),
            ("Vision and hearing",
             "Ask about age-appropriate vision and hearing checks."),
            ("Dental health",
             "Discuss regular dental check-ups.")
        ]

    elif age < 30:
        guidance = [
            ("Blood pressure",
             "Discuss periodic blood pressure checks."),
            ("Dental and vision health",
             "Maintain routine dental and vision check-ups."),
            ("General health",
             "Discuss appropriate preventive checks based on "
             "family history and risk factors.")
        ]

    elif age < 40:
        guidance = [
            ("Blood pressure",
             "Discuss regular blood pressure monitoring."),
            ("Blood sugar",
             "Ask a healthcare professional whether diabetes "
             "screening is appropriate."),
            ("Lifestyle assessment",
             "Review nutrition, physical activity and sleep.")
        ]

    elif age < 50:
        guidance = [
            ("Blood pressure",
             "Discuss regular blood pressure checks."),
            ("Diabetes screening",
             "Discuss blood sugar testing based on risk factors."),
            ("Cholesterol",
             "Ask whether a lipid profile is appropriate."),
            ("Cancer screening",
             "Discuss screening based on personal and family history.")
        ]

    else:
        guidance = [
            ("Blood pressure",
             "Discuss regular blood pressure monitoring."),
            ("Diabetes screening",
             "Discuss appropriate blood sugar screening."),
            ("Cholesterol",
             "Discuss lipid profile testing."),
            ("Cancer screening",
             "Ask about age-appropriate cancer screening."),
            ("Bone health",
             "Discuss bone health assessment and osteoporosis "
             "screening where appropriate."),
            ("Vision and hearing",
             "Maintain regular vision and hearing assessments.")
        ]

    if gender == "Female":
        guidance.append(
            (
                "Women's preventive health",
                "Discuss cervical and breast cancer screening "
                "according to age, history and local guidelines."
            )
        )

    elif gender == "Male":
        guidance.append(
            (
                "Men's preventive health",
                "Discuss any relevant preventive checks with "
                "a healthcare professional."
            )
        )

    return guidance


def render_screening(client=None, user_id=None):

    st.title("Age-Based Health Screening")

    st.write(
        "Explore general preventive health screening "
        "information based on your age."
    )

    st.info(
        "These are general educational suggestions. "
        "The appropriate tests and timing depend on your "
        "health history, risk factors and local guidelines."
    )

    age = st.number_input(
        "Enter your age",
        min_value=1,
        max_value=120,
        value=25,
        step=1
    )

    gender = st.selectbox(
        "Select gender",
        [
            "Prefer not to say",
            "Female",
            "Male",
            "Other"
        ]
    )

    if st.button(
        "View Screening Guidance",
        use_container_width=True
    ):

        guidance = get_screening_guidance(
            int(age),
            gender
        )

        st.subheader("Your Screening Guidance")

        for index, item in enumerate(guidance, start=1):

            title, description = item

            with st.expander(
                f"{index}. {title}",
                expanded=True
            ):
                st.write(description)

        st.warning(
            "Do not start, stop or change medical tests "
            "or treatment based only on this information. "
            "Consult a qualified healthcare professional."
        )
      
