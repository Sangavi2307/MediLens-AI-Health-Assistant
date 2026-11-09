
import streamlit as st
from supabase import create_client


# ----------------------------------
# SUPABASE CONNECTION
# ----------------------------------

def get_supabase_client():
    try:
        supabase_url = st.secrets["SUPABASE_URL"]
        supabase_key = st.secrets["SUPABASE_KEY"]

        if not supabase_url or not supabase_key:
            st.error("Supabase URL or key is missing.")
            return None

        return create_client(supabase_url, supabase_key)

    except Exception as e:
        st.error(f"Supabase connection error: {e}")
        return None


# ----------------------------------
# INITIALIZE SESSION
# ----------------------------------

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


# ----------------------------------
# LOGIN FUNCTION
# ----------------------------------

def render_login(client):

    st.subheader("Welcome Back")
    st.write("Login to your MediLens AI account.")

    with st.form("login_form"):

        email = st.text_input(
            "Email Address",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        submitted = st.form_submit_button(
            "Login",
            use_container_width=True
        )

    if submitted:

        email = email.strip().lower()

        if not email or not password:
            st.warning("Please enter your email and password.")
            return

        try:
            response = client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            user = response.user
            session = response.session

            if user and session:

                st.session_state["auth_user_id"] = user.id
                st.session_state["auth_user_email"] = user.email
                st.session_state["supabase_client"] = client
                st.session_state["is_authenticated"] = True

                st.success("Login successful!")
                st.rerun()

            else:
                st.error(
                    "Login unsuccessful. Please try again."
                )

        except Exception as e:

            error_message = str(e)
            st.error(f"Login failed: {error_message}")


# ----------------------------------
# REGISTRATION FUNCTION
# ----------------------------------

def render_registration(client):

    st.subheader("Create Your MediLens Account")

    with st.form("registration_form"):

        email = st.text_input(
            "Email Address",
            key="new_user_email"
        )

        password = st.text_input(
            "Create Password",
            type="password",
            key="new_user_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="new_user_confirm_password"
        )

        submitted = st.form_submit_button(
            "Create Account",
            use_container_width=True
        )

    if submitted:

        email = email.strip().lower()

        if not email or not password or not confirm_password:
            st.warning("Please fill in all fields.")
            return

        if password != confirm_password:
            st.error("Passwords do not match.")
            return

        if len(password) < 6:
            st.error("Password must contain at least 6 characters.")
            return

        try:
            response = client.auth.sign_up({
                "email": email,
                "password": password
            })

            if response.user:

                if response.session:
                    st.session_state["auth_user_id"] = response.user.id
                    st.session_state["auth_user_email"] = response.user.email
                    st.session_state["supabase_client"] = client
                    st.session_state["is_authenticated"] = True

                    st.success("Account created successfully!")
                    st.rerun()

                else:
                    st.success(
                        "Account created! Please check your email "
                        "and confirm your account before logging in."
                    )

            else:
                st.error("Account creation was unsuccessful.")

        except Exception as e:

            st.error(f"Registration failed: {str(e)}")


# ----------------------------------
# LOGOUT FUNCTION
# ----------------------------------

def logout_user(client):

    try:
        if client:
            client.auth.sign_out()

    except Exception:
        pass

    st.session_state["auth_user_id"] = None
    st.session_state["auth_user_email"] = None
    st.session_state["supabase_client"] = None
    st.session_state["is_authenticated"] = False

    for key in [
        "extracted_report",
        "analysis_results",
        "ai_explanation"
    ]:
        st.session_state.pop(key, None)

    st.rerun()


# ----------------------------------
# MAIN AUTHENTICATION PAGE
# ----------------------------------

def render_authentication():

    initialize_auth_session()

    client = get_supabase_client()

    if client is None:
        st.error("Unable to connect to Supabase.")
        return False

    if st.session_state["is_authenticated"]:
        return True

    st.title("MediLens AI")
    st.write("Your AI Medical Report Explainer")

    login_tab, signup_tab = st.tabs([
        "Login",
        "Create Account"
    ])

    with login_tab:
        render_login(client)

    with signup_tab:
        render_registration(client)

    return st.session_state["is_authenticated"]
            
