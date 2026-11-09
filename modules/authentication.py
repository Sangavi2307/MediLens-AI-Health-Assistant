import streamlit as st
from supabase import create_client


def get_supabase_client():
    """Create one Supabase client for the current Streamlit session."""

    if "supabase_client" not in st.session_state:
        try:
            supabase_url = st.secrets["SUPABASE_URL"]
            supabase_key = st.secrets["SUPABASE_KEY"]

            st.session_state.supabase_client = create_client(
                supabase_url,
                supabase_key
            )

        except Exception:
            st.error(
                "Unable to connect to Supabase. "
                "Please check your Streamlit Secrets."
            )
            return None

    return st.session_state.supabase_client


def render_authentication():
    """Display registration, login and logout screens."""

    if "auth_user_id" not in st.session_state:
        st.session_state.auth_user_id = None

    if "auth_user_email" not in st.session_state:
        st.session_state.auth_user_email = None

    client = get_supabase_client()

    if client is None:
        return False

    # Already logged in
    if st.session_state.auth_user_id:
        st.success(
            f"Logged in as {st.session_state.auth_user_email}"
        )

        if st.button("Logout"):
            try:
                client.auth.sign_out()
            except Exception:
                pass

            st.session_state.auth_user_id = None
            st.session_state.auth_user_email = None
            st.rerun()

        return True

    st.title("MediLens Account")

    login_tab, register_tab = st.tabs(
        ["Login", "Create Account"]
    )

    # LOGIN
    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email address")
            password = st.text_input(
                "Password",
                type="password"
            )

            login_button = st.form_submit_button(
                "Login",
                use_container_width=True
            )

        if login_button:
            if not email.strip() or not password:
                st.warning("Please enter your email and password.")

            else:
                try:
                    response = client.auth.sign_in_with_password({
                        "email": email.strip(),
                        "password": password
                    })

                    st.session_state.auth_user_id = (
                        response.user.id
                    )
                    st.session_state.auth_user_email = (
                        response.user.email
                    )

                    st.success("Login successful!")
                    st.rerun()

                except Exception:
                    st.error(
                        "Login failed. Check your email and password."
                    )

    # REGISTRATION
    with register_tab:
        with st.form("registration_form"):
            new_email = st.text_input(
                "Email address",
                key="register_email"
            )

            new_password = st.text_input(
                "Create password",
                type="password",
                key="register_password"
            )

            confirm_password = st.text_input(
                "Confirm password",
                type="password",
                key="confirm_password"
            )

            register_button = st.form_submit_button(
                "Create Account",
                use_container_width=True
            )

        if register_button:
            email_value = new_email.strip()

            if not email_value or not new_password:
                st.warning("Please complete all fields.")

            elif "@" not in email_value:
                st.warning("Please enter a valid email address.")

            elif len(new_password) < 8:
                st.warning(
                    "Password must contain at least 8 characters."
                )

            elif new_password != confirm_password:
                st.warning("Passwords do not match.")

            else:
                try:
                    response = client.auth.sign_up({
                        "email": email_value,
                        "password": new_password
                    })

                    if response.session and response.user:
                        st.session_state.auth_user_id = (
                            response.user.id
                        )
                        st.session_state.auth_user_email = (
                            response.user.email
                        )

                        st.success("Account created successfully!")
                        st.rerun()

                    else:
                        st.success(
                            "Registration received! "
                            "Check your email to confirm your account, "
                            "then log in."
                        )

                except Exception:
                    st.error(
                        "Registration could not be completed. "
                        "Check your details or try logging in."
                    )

    return False
