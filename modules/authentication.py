
import streamlit as st
from supabase import create_client


# ==========================================
# SESSION INITIALIZATION
# ==========================================

def initialize_auth_session():

    defaults = {
        "auth_user_id": None,
        "auth_user_email": None,
        "supabase_client": None,
        "is_authenticated": False
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


# ==========================================
# SUPABASE CONNECTION
# ==========================================

def get_supabase_client():

    if st.session_state.get("supabase_client") is None:

        try:

            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]

            client = create_client(url, key)

            st.session_state["supabase_client"] = client

        except Exception as error:

            st.error("Supabase connection failed.")

            st.caption(
                f"{type(error).__name__}: {error}"
            )

            return None

    return st.session_state["supabase_client"]


# ==========================================
# ANONYMOUS SIGN-IN
# ==========================================

def guest_sign_in(client):

    try:

        response = client.auth.sign_in_anonymously()

        if response.user is None:

            st.error("Guest sign-in was unsuccessful.")
            return False

        # Save authenticated user ID

        st.session_state["auth_user_id"] = (
            response.user.id
        )

        st.session_state["auth_user_email"] = None

        st.session_state["is_authenticated"] = True

        st.success("Guest access activated successfully!")

        st.rerun()

    except Exception as error:

        st.error("Unable to start guest session.")

        st.caption(
            f"{type(error).__name__}: {error}"
        )

        return False


# ==========================================
# LOGOUT
# ==========================================

def logout_user(client):

    try:

        client.auth.sign_out()

    except Exception as error:

        st.warning("Unable to complete sign-out.")

        st.caption(str(error))

    st.session_state["auth_user_id"] = None
    st.session_state["auth_user_email"] = None
    st.session_state["is_authenticated"] = False

    st.session_state.pop("extracted_text", None)
    st.session_state.pop("analysis_result", None)
    st.session_state.pop("ai_explanation", None)

    st.session_state.pop("extracted_report", None)
    st.session_state.pop("analysis_results", None)

    st.rerun()


# ==========================================
# MAIN AUTHENTICATION
# ==========================================

def render_authentication():

    initialize_auth_session()

    client = get_supabase_client()

    if client is None:
        return False

    # Check authenticated user

    if (
        st.session_state.get("auth_user_id")
        and st.session_state.get("is_authenticated")
    ):

        st.success("You are using MediLens as a Guest.")

        st.caption(
            "Your guest session is active."
        )

        if st.button(
            "Logout",
            use_container_width=True
        ):

            logout_user(client)

        return True

    # Welcome screen

    st.title("🩺 Welcome to MediLens")

    st.write(
        "Understand your medical reports with AI assistance."
    )

    st.info(
        "You can use MediLens without creating an account."
    )

    st.subheader("Guest Access")

    st.write(
        "Continue securely with a temporary guest session."
    )

    if st.button(
        "Continue as Guest",
        use_container_width=True
    ):

        guest_sign_in(client)

    return False
        
