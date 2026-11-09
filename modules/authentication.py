
import streamlit as st
from supabase import create_client


# ==========================================
# INITIALIZE SESSION
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
# SUPABASE CONNECTION
# ==========================================

def get_supabase_client():

    # IMPORTANT: Check whether client is None
    if st.session_state.get("supabase_client") is None:

        try:
            supabase_url = st.secrets["SUPABASE_URL"]
            supabase_key = st.secrets["SUPABASE_KEY"]

            client = create_client(
                supabase_url,
                supabase_key
            )

            st.session_state["supabase_client"] = client

        except Exception as error:

            st.error("Supabase connection failed.")
            st.caption(
                f"{type(error).__name__}: {error}"
            )

            return None

    return st.session_state["supabase_client"]


# ==========================================
# LOGOUT
# ==========================================

def logout_user(client):

    try:
        client.auth.sign_out()
    except Exception:
        pass

    st.session_state["auth_user_id"] = None
    st.session_state["auth_user_email"] = None

    for key in [
        "extracted_report",
        "analysis_results",
        "ai_explanation"
    ]:
        st.session_state.pop(key, None)

    st.rerun()


# ==========================================
# LOGIN
# ==========================================

def render_login(client):

    st.subheader("Welcome Back!")

    with st.form("medilens_login_form"):

        email = st.text_input(
            "Email Address",
            placeholder="Enter your registered email"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        submitted = st.form_submit_button(
            "Login",
            use_container_width=True
        )

    if submitted:

        email = email.strip().lower()

        if not email or not password:

            st.warning("Enter your email and password.")

        else:

            try:

                response = client.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })

                if response.user:

                    st.session_state["auth_user_id"] = (
                        response.user.id
                    )

                    st.session_state["auth_user_email"] = (
                        response.user.email
                    )

                    st.success("Login successful!")

                    st.rerun()

                else:

                    st.error("Login was unsuccessful.")

            except Exception as error:

                st.error("Login failed.")

                st.write(
                    "Please check the authentication details."
                )

                st.caption(
                    f"Error: {type(error).__name__}: {error}"
                )


# ==========================================
# REGISTRATION
# ==========================================

def render_registration(client):

    st.subheader("Create Your MediLens Account")

    with st.form("medilens_register_form"):

        email = st.text_input(
            "Email Address",
            key="register_email"
        )

        password = st.text_input(
            "Create Password",
            type="password",
            key="register_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="register_confirm"
        )

        submitted = st.form_submit_button(
            "Create Account",
            use_container_width=True
        )

    if submitted:

        email = email.strip().lower()

        if not email or not password or not confirm_password:

            st.warning("Please complete all fields.")

        elif "@" not in email:

            st.warning("Enter a valid email address.")

        elif len(password) < 8:

            st.warning(
                "Password must contain at least 8 characters."
            )

        elif password != confirm_password:

            st.warning("Passwords do not match.")

        else:

            try:

                response = client.auth.sign_up({
                    "email": email,
                    "password": password
                })

                if response.user is None:

                    st.error("Account creation failed.")

                elif (
                    response.user.identities is not None
                    and len(response.user.identities) == 0
                ):

                    st.error(
                        "An account may already exist with this email."
                    )

                elif response.session:

                    st.session_state["auth_user_id"] = (
                        response.user.id
                    )

                    st.session_state["auth_user_email"] = (
                        response.user.email
                    )

                    st.success("Account created successfully!")

                    st.rerun()

                else:

                    st.success(
                        "Account created! Please check your email "
                        "and confirm your account before logging in."
                    )

            except Exception as error:

                st.error("Registration failed.")

                st.caption(
                    f"{type(error).__name__}: {error}"
                )


# ==========================================
# FORGOT PASSWORD
# ==========================================

def render_forgot_password(client):

    st.subheader("Reset Your Password")

    st.write(
        "Enter your registered email address. "
        "Supabase will send you a password reset link."
    )

    with st.form("medilens_reset_form"):

        email = st.text_input(
            "Registered Email",
            key="reset_email"
        )

        submitted = st.form_submit_button(
            "Send Reset Link",
            use_container_width=True
        )

    if submitted:

        email = email.strip().lower()

        if not email or "@" not in email:

            st.warning("Enter a valid email address.")

        else:

            try:

                client.auth.reset_password_for_email(email)

                st.success(
                    "If the account exists, a password reset "
                    "email will be sent. Check your inbox."
                )

            except Exception as error:

                st.error("Unable to send reset email.")

                st.caption(
                    f"{type(error).__name__}: {error}"
                )


# ==========================================
# MAIN AUTHENTICATION
# ==========================================

def render_authentication():

    initialize_auth_session()

    client = get_supabase_client()

    if client is None:
        return False

    if st.session_state.get("auth_user_id"):

        st.success(
            "Logged in as: "
            + str(st.session_state["auth_user_email"])
        )

        if st.button("Logout", use_container_width=True):
            logout_user(client)

        return True

    st.title("🩺 MediLens Account")

    login_tab, register_tab, reset_tab = st.tabs([
        "Login",
        "Create Account",
        "Forgot Password"
    ])

    with login_tab:
        render_login(client)

    with register_tab:
        render_registration(client)

    with reset_tab:
        render_forgot_password(client)

    return False
            
