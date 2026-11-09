
import streamlit as st


def render_health_profile(client, user_id):
    """
    Display and manage the personal health profile
    for the currently authenticated user.
    """

    st.title("Personal Health Profile")

    st.write(
        "Enter your personal health information "
        "to receive relevant educational health guidance."
    )

    if not user_id:
        st.warning("Please log in to access your health profile.")
        return

    # Load the user's existing health profile
    try:
        response = (
            client.table("health_profiles")
            .select("*")
            .eq("id", user_id)
            .execute()
        )

        profile = response.data[0] if response.data else {}

    except Exception as error:
        st.error("Unable to load your health profile.")
        st.caption(f"Database error: {error}")
        return

    # Available gender options
    gender_options = [
        "Prefer not to say",
        "Female",
        "Male",
        "Other"
    ]

    saved_gender = profile.get(
        "gender",
        "Prefer not to say"
    )

    if saved_gender not in gender_options:
        saved_gender = "Prefer not to say"

    # Health profile form
    with st.form("health_profile_form"):

        st.subheader("Personal Information")

        full_name = st.text_input(
            "Full Name",
            value=profile.get("full_name", ""),
            placeholder="Enter your full name"
        )

        age = st.number_input(
            "Age",
            min_value=1,
            max_value=120,
            value=int(profile.get("age") or 18),
            step=1
        )

        gender = st.selectbox(
            "Gender",
            gender_options,
            index=gender_options.index(saved_gender)
        )

        st.divider()

        st.subheader("Medical Information")

        medical_history = st.text_area(
            "Medical History",
            value=profile.get("medical_history", ""),
            placeholder=(
                "Enter relevant past medical history"
            )
        )

        existing_conditions = st.text_area(
            "Existing Health Conditions",
            value=profile.get("existing_conditions", ""),
            placeholder=(
                "Enter existing health conditions, if any"
            )
        )

        current_symptoms = st.text_area(
            "Current Symptoms",
            value=profile.get("current_symptoms", ""),
            placeholder=(
                "Describe your current symptoms, if any"
            )
        )

        st.info(
            "Your information is intended for educational "
            "health guidance. It is not a medical diagnosis."
        )

        submitted = st.form_submit_button(
            "Save Health Profile",
            use_container_width=True
        )

    # Save profile to Supabase
    if submitted:

        if not full_name.strip():
            st.warning("Please enter your full name.")

        else:
            profile_data = {
                "id": user_id,
                "full_name": full_name.strip(),
                "age": int(age),
                "gender": gender,
                "medical_history": medical_history.strip(),
                "existing_conditions": existing_conditions.strip(),
                "current_symptoms": current_symptoms.strip()
            }

            try:
                client.table("health_profiles").upsert(
                    profile_data
                ).execute()

                st.success(
                    "Your health profile has been saved successfully!"
                )

                st.rerun()

            except Exception as error:
                st.error(
                    "Unable to save your health profile."
                )
                st.caption(f"Database error: {error}")
              
