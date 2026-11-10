
import streamlit as st
from supabase import create_client

# ==========================================
# CONFIGURATION
# ==========================================

REDIRECT_URL = (
    "https://medilens-ai-health-assistant-dxmjwcxyg2evxbx62ttbox.streamlit.app/"
)

# ==========================================
# SESSION INITIALIZATION
# ==========================================

def initialize_auth_session():
    defaults = {
        "auth_user_id": None,
        "auth_user_email": None,
        "supabase_client": None,
        "recovery_mode": False,
        "recovery_verified": False
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

            st.session_state["supabase_client"] = (
                create_client(url, key)
            )

        except Exception as error:
            st.error("Supabase connection failed.")
            st.caption(str(error))
            return None

    return st.session_state["supabase_client"]


# ==========================================
# PASSWORD RECOVERY LINK VERIFICATION
# ==========================================

def handle_recovery_link(client):
    token_hash = st.query_params.get("token_hash")
    recovery_type = st.query_params.get("type")

    if (
        token_hash
        and recovery_type == "recovery"
        and not st.session_state["recovery_verified"]
    ):
        try:
            response = client.auth.verify_otp({
                "token_hash": token_hash,
                "type": "recovery"
            })

            if response.session:
                st.session_state["recovery_mode"] = True
                st.session_state["recovery_verified"] = True
                st.query_params.clear()
                st.rerun()

            else:
                st.error("Recovery session could not be verified.")

        except Exception as error:
            st.error("Password recovery link verification failed.")
            st.caption(
                f"{type(error).__name__}: {error}"
            )


# ==========================================
# UPDATE NEW PASSWORD
# ==========================================

def render_update_password(client):
    st.title("Create New Password")

    st.write("Enter your new MediLens account password.")

    with st.form("update_password_form"):

        new_password = st.text_input(
            "New Password",
            type="password"
        )

        confirm_password = st.text_input(
            "Confirm New Password",
            type="password"
        )

        submitted = st.form_submit_button(
            "Create Now",
            use_container_width=True
        )

    if submitted:

        if not new_password or not confirm_password:
            st.warning("Please complete both password fields.")

        elif len(new_password) < 8:
            st.warning("Password must contain at least 8 characters.")

        elif new_password != confirm_password:
            st.warning("Passwords do not match.")

        else:
            try:
                response = client.auth.update_user({
                    "password": new_password
                })

                if response.user:

                    st.session_state["auth_user_id"] = None
                    st.session_state["auth_user_email"] = None
                    st.session_state["recovery_mode"] = False
                    st.session_state["recovery_verified"] = False

                    client.auth.sign_out()

                    st.success(
                        "Password updated successfully! "
                        "Please log in with your new password."
                    )

                else:
                    st.error("Password update was unsuccessful.")

            except Exception as error:
                st.error("Unable to update password.")
                st.caption(
                    f"{type(error).__name__}: {error}"
                )


# ==========================================
# LOGIN
# ==========================================

def render_login(client):
    st.subheader("Welcome Back!")

    with st.form("medilens_login_form"):

        email = st.text_input("Email Address")

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
                st.caption(
                    f"{type(error).__name__}: {error}"
                )


# ==========================================
# REGISTRATION
# ==========================================

def render_registration(client):
    st.subheader("Create Your MediLens Account")

    with st.form("medilens_register_form"):

        email = st.text_input("Email Address")

        password = st.text_input(
            "Create Password",
            type="password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password"
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
            st.warning("Password must contain at least 8 characters.")

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
                        "Account created! Check your email "
                        "to confirm your account."
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
        "We will send you a password reset link."
    )

    with st.form("medilens_reset_form"):

        email = st.text_input("Registered Email")

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
                client.auth.reset_password_for_email(
                    email,
                    options={
                        "redirect_to": REDIRECT_URL
                    }
                )

                st.success(
                    "If the account exists, a reset email "
                    "has been requested. Check your inbox."
                )

            except Exception as error:
                st.error("Unable to send reset email.")
                st.caption(
                    f"{type(error).__name__}: {error}"
                )


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
# MAIN AUTHENTICATION
# ==========================================

def render_authentication():

    initialize_auth_session()

    client = get_supabase_client()

    if client is None:
        return False

    # Check for password recovery link
    handle_recovery_link(client)

    # Show new password form
    if st.session_state["recovery_mode"]:
        render_update_password(client)
        return False

    # Check logged-in user
    if st.session_state.get("auth_user_id"):

        st.success(
            "Logged in as: "
            + str(st.session_state["auth_user_email"])
        )

        if st.button("Logout", use_container_width=True):
            logout_user(client)

        return True

    # Authentication tabs
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
        
