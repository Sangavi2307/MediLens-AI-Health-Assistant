
import streamlit as st
from supabase import create_client


def initialize_auth_session():
    defaults = {
        "auth_user_id": None,
        "auth_user_email": None,
        "supabase_client": None,
        "is_authenticated": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_supabase_client():
    if st.session_state.get("supabase_client") is None:
        try:
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]

            st.session_state["supabase_client"] = create_client(
                url, key
            )

        except Exception as error:
            st.error("Supabase connection failed.")
            st.caption(f"{type(error).__name__}: {error}")
            return None

    return st.session_state["supabase_client"]


def restore_auth_session(client):
    try:
        session = client.auth.get_session()

        if session and session.user:
            st.session_state["auth_user_id"] = session.user.id
            st.session_state["auth_user_email"] = session.user.email
            st.session_state["is_authenticated"] = True
            return True

    except Exception:
        pass

    return False


def guest_sign_in(client):
    try:
        if restore_auth_session(client):
            st.success("Your existing guest session has been restored.")
            st.rerun()
            return True

        response = client.auth.sign_in_anonymously()

        if not response.user:
            st.error("Guest sign-in was unsuccessful.")
            return False

        st.session_state["auth_user_id"] = response.user.id
        st.session_state["auth_user_email"] = None
        st.session_state["is_authenticated"] = True

        st.success("Guest access activated successfully!")
        st.rerun()
        return True

    except Exception as error:
        st.error("Unable to start your guest session.")
        st.caption(f"{type(error).__name__}: {error}")
        return False


def logout_user(client):
    try:
        client.auth.sign_out()

    except Exception as error:
        st.warning("Unable to complete sign-out.")
        st.caption(str(error))

    st.session_state["auth_user_id"] = None
    st.session_state["auth_user_email"] = None
    st.session_state["is_authenticated"] = False

    for key in [
        "extracted_text",
        "analysis_result",
        "ai_explanation",
        "extracted_report",
        "analysis_results",
    ]:
        st.session_state.pop(key, None)

    st.rerun()


def render_authentication():
    initialize_auth_session()

    client = get_supabase_client()

    if client is None:
        return False

    if (
        st.session_state.get("auth_user_id")
        and st.session_state.get("is_authenticated")
    ):
        return True

    if restore_auth_session(client):
        return True

    st.title("🩺 Welcome to MediLens")
    st.write("Understand your medical reports with AI assistance.")

    st.info("Use MediLens without creating an email account.")

    st.subheader("Guest Access")
    st.write("Continue securely with a temporary guest session.")

    if st.button("Continue as Guest", use_container_width=True):
        guest_sign_in(client)

    return False
