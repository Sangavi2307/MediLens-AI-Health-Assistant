
import streamlit as st
from supabase import create_client
from streamlit_cookies_manager import EncryptedCookieManager


COOKIE_NAME = "medilens_guest_refresh_token"


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


def get_cookies():
    try:
        password = st.secrets["COOKIE_PASSWORD"]

        cookies = EncryptedCookieManager(
            prefix="medilens/",
            password=password
        )

        if not cookies.ready():
            st.info("Restoring your secure MediLens session...")
            st.stop()

        return cookies

    except Exception as error:
        st.error("Unable to initialize secure session storage.")
        st.caption(f"{type(error).__name__}: {error}")
        return None


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


def restore_auth_session(client, cookies):
    try:
        refresh_token = cookies.get(COOKIE_NAME)

        if not refresh_token:
            return False

        response = client.auth.refresh_session(refresh_token)

        if not response or not response.session:
            return False

        session = response.session

        cookies[COOKIE_NAME] = session.refresh_token
        cookies.save()

        st.session_state["auth_user_id"] = session.user.id
        st.session_state["auth_user_email"] = session.user.email
        st.session_state["is_authenticated"] = True

        return True

    except Exception:
        return False


def guest_sign_in(client, cookies):
    try:
        # First try restoring the previous guest account.
        if restore_auth_session(client, cookies):
            st.success("Your previous guest account was restored.")
            st.rerun()
            return True

        # Create a guest only when no previous session exists.
        response = client.auth.sign_in_anonymously()

        if not response.user or not response.session:
            st.error("Guest sign-in was unsuccessful.")
            return False

        session = response.session

        cookies[COOKIE_NAME] = session.refresh_token
        cookies.save()

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


def logout_user(client, cookies=None):
    try:
        client.auth.sign_out()

    except Exception as error:
        st.warning("Unable to complete sign-out.")
        st.caption(str(error))

    if cookies is not None:
        try:
            if COOKIE_NAME in cookies:
                del cookies[COOKIE_NAME]
                cookies.save()
        except Exception:
            pass

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

    cookies = get_cookies()

    if cookies is None:
        return False

    client = get_supabase_client()

    if client is None:
        return False

    # Existing authenticated session in Streamlit.
    if (
        st.session_state.get("auth_user_id")
        and st.session_state.get("is_authenticated")
    ):
        return True

    # Restore the same guest account after reopening.
    if restore_auth_session(client, cookies):
        return True

    st.title("🩺 Welcome to MediLens")
    st.write("Understand your medical reports with AI assistance.")

    st.info("Use MediLens without creating an email account.")

    st.subheader("Guest Access")
    st.write("Continue securely with a guest session.")

    if st.button("Continue as Guest", use_container_width=True):
        guest_sign_in(client, cookies)

    return False
