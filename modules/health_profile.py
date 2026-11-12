
import streamlit as st
from datetime import datetime, timezone


def render_health_profile(client, user_id):

    st.title("Patient Health Profile")
    st.write("View and update your saved health information.")

    if not user_id:
        st.error("Guest session unavailable. Please sign in again.")
        return

    # Load existing profile
    try:
        response = (
            client.table("health_profiles")
            .select("*")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )

        existing = response.data[0] if response.data else {}

    except Exception as error:
        st.error("Unable to load health profile.")
        st.caption(str(error))
        return

    if existing:
        st.success("Your saved health profile is loaded.")
    else:
        st.info("Create your health profile.")

    # Edit mode
    edit_key = f"edit_profile_{user_id}"

    if edit_key not in st.session_state:
        st.session_state[edit_key] = not bool(existing)

    if existing and not st.session_state[edit_key]:

        st.subheader("My Health Profile")

        st.write("**Full Name:**", existing.get("full_name", ""))
        st.write("**Age:**", existing.get("age", ""))
        st.write("**Gender:**", existing.get("gender", ""))
        st.write("**Weight:**", existing.get("weight_kg") or "Not provided")
        st.write("**Medical History:**", existing.get("medical_history", ""))
        st.write("**Existing Conditions:**", existing.get("existing_conditions", ""))
        st.write("**Current Medications:**", existing.get("current_medications", ""))
        st.write("**Allergies:**", existing.get("allergies", ""))

        st.write(
            "**Preferred Language:**",
            existing.get("preferred_language", "English")
        )

        if st.button("Edit Health Profile", use_container_width=True):
            st.session_state[edit_key] = True
            st.rerun()

        return

    # Profile edit form
    with st.form("patient_health_profile"):

        st.subheader("Personal Information")

        full_name = st.text_input(
            "Full Name",
            value=existing.get("full_name") or ""
        )

        age = st.number_input(
            "Age",
            min_value=1,
            max_value=120,
            value=int(existing.get("age") or 18)
        )

        gender_options = [
            "Male",
            "Female",
            "Other",
            "Prefer not to say"
        ]

        saved_gender = existing.get(
            "gender",
            "Prefer not to say"
        )

        gender = st.selectbox(
            "Gender",
            gender_options,
            index=(
                gender_options.index(saved_gender)
                if saved_gender in gender_options
                else 3
            )
        )

        weight_kg = st.number_input(
            "Weight (kg)",
            min_value=0.0,
            max_value=500.0,
            value=float(existing.get("weight_kg") or 0.0),
            step=0.5
        )

        st.divider()
        st.subheader("Health Information")

        medical_history = st.text_area(
            "Medical History",
            value=existing.get("medical_history") or ""
        )

        existing_conditions = st.text_area(
            "Existing Health Conditions",
            value=existing.get("existing_conditions") or ""
        )

        current_medications = st.text_area(
            "Current Medications",
            value=existing.get("current_medications") or ""
        )

        allergies = st.text_area(
            "Allergies",
            value=existing.get("allergies") or ""
        )

        st.divider()
        st.subheader("Language Preference")

        language_options = ["English", "Tamil"]

        saved_language = existing.get(
            "preferred_language",
            "English"
        )

        preferred_language = st.selectbox(
            "Choose Your Preferred Language",
            language_options,
            index=(
                language_options.index(saved_language)
                if saved_language in language_options
                else 0
            )
        )

        submitted = st.form_submit_button(
            "Save Changes",
            use_container_width=True
        )

    if submitted:

        if not full_name.strip():
            st.warning("Please enter your full name.")
            return

        profile_data = {
            "user_id": user_id,
            "full_name": full_name.strip(),
            "age": age,
            "gender": gender,
            "weight_kg": weight_kg if weight_kg > 0 else None,
            "medical_history": medical_history.strip(),
            "existing_conditions": existing_conditions.strip(),
            "current_medications": current_medications.strip(),
            "allergies": allergies.strip(),
            "preferred_language": preferred_language,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        try:

            if existing:
                (
                    client.table("health_profiles")
                    .update(profile_data)
                    .eq("user_id", user_id)
                    .execute()
                )

            else:
                (
                    client.table("health_profiles")
                    .insert(profile_data)
                    .execute()
                )

            st.session_state[edit_key] = False

            st.success("Health Profile Saved Successfully!")
            st.rerun()

        except Exception as error:
            st.error("Unable to save health profile.")
            st.caption(f"{type(error).__name__}: {error}")
