
import streamlit as st
from supabase import create_client


# ==========================================
# SUPABASE CONNECTION
# ==========================================

def get_supabase_client():

    if "supabase_client" not in st.session_state:

        try:
            supabase_url = st.secrets["SUPABASE_URL"]
            supabase_key = st.secrets["SUPABASE_KEY"]

            st.session_state.supabase_client = create_client(
                supabase_url,
                supabase_key
            )

        except Exception as error:

            st.error("Supabase connection failed.")

            st.caption(
                f"Error: {type(error).__name__}: {error}"
            )

            return None

    return st.session_state.supabase_client


# ==========================================
# AUTHENTICATION SESSION
# ==========================================

def initialize_auth_session():

    defaults = {
        "auth_user_id": None,
        "auth_user_email": None,
        "supabase_client": None
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


# ==========================================
# LOGOUT
# ==========================================

def logout_user(client):

    try:
        client.auth.sign_out()

    except Exception:
        pass

    st.session_state.auth_user_id = None
    st.session_state.auth_user_email = None

    st.session_state.pop("extracted_report", None)
    st.session_state.pop("analysis_results", None)
    st.session_state.pop("ai_explanation", None)

    st.rerun()


# ==========================================
# LOGIN
# ==========================================

def render_login(client):

    st.subheader("Login to MediLens")

    with st.form("medilens_login_form"):

        email = st.text_input(
            "Email address",
            placeholder="Enter your email"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        login_button = st.form_submit_button(
            "Login",
            use_container_width=True
        )

    if login_button:

        email = email.strip().lower()

        if not email or not password:

            st.warning(
                "Please enter your email and password."
            )

        else:

            try:

                response = client.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })

                if response.user:

                    st.session_state.auth_user_id = (
                        response.user.id
                    )

                    st.session_state.auth_user_email = (
                        response.user.email
                    )

                    st.success("Login successful!")

                    st.rerun()

                else:

                    st.error(
                        "Login failed. Please check your account."
                    )

            except Exception as error:

                st.error("Unable to log in.")

                st.caption(
                    f"Error type: {type(error).__name__}"
                )

                st.caption(
                    f"Details: {error}"
                )


# ==========================================
# REGISTRATION
# ==========================================

def render_registration(client):

    st.subheader("Create a MediLens Account")

    with st.form("medilens_registration_form"):

        email = st.text_input(
            "Email address",
            placeholder="Enter your email",
            key="new_user_email"
        )

        password = st.text_input(
            "Create password",
            type="password",
            key="new_user_password"
        )

        confirm_password = st.text_input(
            "Confirm password",
            type="password",
            key="new_user_confirm_password"
        )

        register_button = st.form_submit_button(
            "Create Account",
            use_container_width=True
        )

    if register_button:

        email = email.strip().lower()

        if not email or not password or not confirm_password:

            st.warning(
                "Please complete all registration fields."
            )

        elif "@" not in email:

            st.warning(
                "Please enter a valid email address."
            )

        elif len(password) < 8:

            st.warning(
                "Password must contain at least 8 characters."
            )

        elif password != confirm_password:

            st.warning(
                "Passwords do not match."
            )

        else:

            try:

                response = client.auth.sign_up({
                    "email": email,
                    "password": password
                })

                if response.user is None:

                    st.error(
                        "Registration could not be completed."
                    )

                elif (
                    response.user.identities is not None
                    and len(response.user.identities) == 0
                ):

                    st.warning(
                        "An account may already exist with this "
                        "email address. Please try logging in."
                    )

                elif response.session and response.user:

                    st.session_state.auth_user_id = (
                        response.user.id
                    )

                    st.session_state.auth_user_email = (
                        response.user.email
                    )

                    st.success(
                        "Your MediLens account was created successfully!"
                    )

                    st.rerun()

                else:

                    st.success(
                        "Registration successful! "
                        "Please check your email and confirm "
                        "your account before logging in."
                    )

            except Exception as error:

                st.error(
                    "Registration failed."
                )

                st.caption(
                    f"Error type: {type(error).__name__}"
                )

                st.caption(
                    f"Details: {error}"
                )


# ==========================================
# MAIN AUTHENTICATION PAGE
# ==========================================

def render_authentication():

    initialize_auth_session()

    client = get_supabase_client()

    if client is None:
        return False

    # Already logged-in user
    if st.session_state.auth_user_id:

        st.success(
            f"Logged in as: "
            f"{st.session_state.auth_user_email}"
        )

        if st.button(
            "Logout",
            use_container_width=True
        ):

            logout_user(client)

        return True

    # Login and registration tabs
    st.title("MediLens Account")

    login_tab, register_tab = st.tabs(
        ["Login", "Create Account"]
    )

    with login_tab:

        render_login(client)

    with register_tab:

        render_registration(client)

    return False
                    
