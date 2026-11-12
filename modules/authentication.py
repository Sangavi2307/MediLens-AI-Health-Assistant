
import streamlit as st
from supabase import create_client


# ==========================================
# INITIALIZE AUTHENTICATION SESSION
# ==========================================

def initialize_auth_session():
    defaults = {
        "auth_user_id": None,
        "auth_user_email": None,
        "supabase_client": None,
        "is_authenticated": False,
        "auth_method": None
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
            st.caption(str(error))
            return None

    return st.session_state["supabase_client"]


# ==========================================
# SAVE USER SESSION
# ==========================================

def set_user_session(user, auth_method):

    st.session_state["auth_user_id"] = user.id

    st.session_state["auth_user_email"] = getattr(
        user, "email", None
    )

    st.session_state["is_authenticated"] = True
    st.session_state["auth_method"] = auth_method


# ==========================================
# CREATE ACCOUNT
# ==========================================

def create_account(client, email, password):

    try:

        response = client.auth.sign_up({
            "email": email,
            "password": password
        })

        if response.user is None:
            st.error("Account creation failed.")
            return False

        # Email confirmation is disabled in Supabase.
        # A session should normally be returned immediately.

        if response.session is None:
            st.warning(
                "Account was created, but no login session was returned. "
                "Please check your Supabase email confirmation settings."
            )
            return False

        set_user_session(response.user, "email")

        st.success("Account created successfully!")

        return True

    except Exception as error:

        st.error("Unable to create your account.")
        st.caption(str(error))

        return False


# ==========================================
# EMAIL LOGIN
# ==========================================

def login_user(client, email, password):

    try:

        response = client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if response.user is None or response.session is None:

            st.error(
                "Login failed. Please check your email and password."
            )

            return False

        set_user_session(response.user, "email")

        st.success("Login successful!")

        return True

    except Exception as error:

        st.error("Login failed. Please check your login details.")
        st.caption(str(error))

        return False


# ==========================================
# LOGOUT
# ==========================================

def logout_user(client, cookies=None):

    try:
        client.auth.sign_out()

    except Exception as error:
        st.warning("Sign-out could not be completed.")
        st.caption(str(error))

    st.session_state["auth_user_id"] = None
    st.session_state["auth_user_email"] = None
    st.session_state["is_authenticated"] = False
    st.session_state["auth_method"] = None
    st.session_state["supabase_client"] = None

    st.session_state["extracted_text"] = ""
    st.session_state["analysis_result"] = None
    st.session_state["ai_explanation"] = None

    st.rerun()


# ==========================================
# RENDER AUTHENTICATION PAGE
# ==========================================

def render_authentication():

    initialize_auth_session()

    # Reuse existing authenticated session.

    if (
        st.session_state.get("is_authenticated")
        and st.session_state.get("auth_user_id")
    ):
        return True

    client = get_supabase_client()

    if client is None:
        return False

    st.title("🩺 Welcome to MediLens")

    st.write(
        "Understand your medical reports "
        "with AI assistance."
    )

    st.divider()

    login_tab, signup_tab = st.tabs([
        "Login",
        "Create Account"
    ])

    # ======================================
    # LOGIN TAB
    # ======================================

    with login_tab:

        st.subheader("Login to MediLens")

        with st.form("login_form"):

            login_email = st.text_input(
                "Email Address",
                key="login_email"
            )

            login_password = st.text_input(
                "Password",
                type="password",
                key="login_password"
            )

            login_submit = st.form_submit_button(
                "Login",
                use_container_width=True
            )

        if login_submit:

            if not login_email.strip() or not login_password:

                st.warning(
                    "Please enter your email and password."
                )

            else:

                success = login_user(
                    client,
                    login_email.strip(),
                    login_password
                )

                if success:
                    st.rerun()

    # ======================================
    # CREATE ACCOUNT TAB
    # ======================================

    with signup_tab:

        st.subheader("Create Your Account")

        with st.form("signup_form"):

            signup_email = st.text_input(
                "Email Address",
                key="signup_email"
            )

            signup_password = st.text_input(
                "Create Password",
                type="password",
                key="signup_password"
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                key="confirm_password"
            )

            signup_submit = st.form_submit_button(
                "Create Account",
                use_container_width=True
            )

        if signup_submit:

            if not signup_email.strip():

                st.warning("Please enter your email address.")

            elif not signup_password:

                st.warning("Please create a password.")

            elif len(signup_password) < 8:

                st.warning(
                    "Password must contain at least 8 characters."
                )

            elif signup_password != confirm_password:

                st.error("Passwords do not match.")

            else:

                success = create_account(
                    client,
                    signup_email.strip(),
                    signup_password
                )

                if success:
                    st.rerun()

    return False
