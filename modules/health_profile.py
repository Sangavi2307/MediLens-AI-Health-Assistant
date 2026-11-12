
import streamlit as st
from datetime import datetime, timezone


def render_health_profile(client, user_id):

    st.title("👤 Patient Health Profile")

    if not user_id:
        st.error("Your guest session is unavailable. Please sign in again.")
        return

    # ------------------------------------------
    # LOAD EXISTING HEALTH PROFILE
    # ------------------------------------------

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
        st.error("Unable to load your health profile.")
        st.caption(f"{type(error).__name__}: {error}")
        return

    if existing:
        st.success("Your previously saved health profile has been loaded.")
        st.info("Your saved information is displayed below. You can edit it and save your changes.")
    else:
        st.info("Welcome! Please create your health profile.")

    # ------------------------------------------
    # DEFAULT VALUES
    # ------------------------------------------

    saved_gender = existing.get("gender") or "Prefer not to say"
    gender_options = [
        "Male",
        "Female",
        "Other",
        "Prefer not to say"
    ]

    saved_language = existing.get("preferred_language") or "English"
    language_options = ["English", "Tamil"]

    gender_index = (
        gender_options.index(saved_gender)
        if saved_gender in gender_options
        else 3
    )

    language_index = (
        language_options.index(saved_language)
        if saved_language in language_options
        else 0
    )

    # ------------------------------------------
    # HEALTH PROFILE FORM
    # ------------------------------------------

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

        gender = st.selectbox(
            "Gender",
            gender_options,
            index=gender_index
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
            value=existing.get("medical_history") or "",
            placeholder="Enter your relevant medical history."
        )

        existing_conditions = st.text_area(
            "Existing Health Conditions",
            value=existing.get("existing_conditions") or "",
            placeholder="Example: Diabetes, hypertension"
        )

        current_medications = st.text_area(
            "Current Medications",
            value=existing.get("current_medications") or "",
            placeholder="Enter medicines you currently take."
        )

        allergies = st.text_area(
            "Allergies",
            value=existing.get("allergies") or "",
            placeholder="Enter any known allergies."
        )

        st.divider()
        st.subheader("Language Preference")

        preferred_language = st.selectbox(
            "Choose Your Preferred Language",
            language_options,
            index=language_index
        )

        submitted = st.form_submit_button(
            "Save Health Profile",
            use_container_width=True
        )

    # ------------------------------------------
    # SAVE OR UPDATE PROFILE
    # ------------------------------------------

    if submitted:

        if not full_name.strip():
            st.warning("Please enter your full name.")
            return

        profile_data = {
            "user_id": user_id,
            "full_name": full_name.strip(),
            "age": int(age),
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
                # Update the existing profile.
                client.table("health_profiles").update(
                    profile_data
                ).eq(
                    "id", existing["id"]
                ).execute()

                st.success("Your existing Health Profile was updated successfully!")

            else:
                # Insert only when this user has no profile.
                client.table("health_profiles").insert(
                    profile_data
                ).execute()

                st.success("Your Health Profile was created successfully!")

            st.rerun()

        except Exception as error:
            st.error("Unable to save your health profile.")
            st.caption(f"{type(error).__name__}: {error}")
