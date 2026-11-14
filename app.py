
import streamlit as st
import pandas as pd

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="MediLens AI Health Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# MODULE IMPORTS
# ==========================================

from modules.extractor import extract_text_from_pdf
from modules.analyzer import analyze_report

from modules.authentication import (
    initialize_auth_session,
    render_authentication,
    get_supabase_client,
    logout_user
)

from modules.health_profile import render_health_profile

# ==========================================
# AI EXPLANATION IMPORT
# ==========================================

try:
    from modules.ai_explanation import ai_explain_report
except ImportError:
    ai_explain_report = None

# ==========================================
# OCR IMPORT
# ==========================================

try:
    from modules.ocr_service import extract_text_from_image
except ImportError:
    try:
        from ocr_service import extract_text_from_image
    except ImportError:
        extract_text_from_image = None

# ==========================================
# CONSTANTS
# ==========================================

MAX_FILE_SIZE = 20 * 1024 * 1024

ALLOWED_FILE_TYPES = [
    "pdf", "png", "jpg", "jpeg", "bmp"
]

# ==========================================
# PROFESSIONAL MEDICAL THEME
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #F2F8FA;
    color: #183746;
}

[data-testid="stMainBlockContainer"] {
    max-width: 1150px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"] {
    background-color: #123B4A;
}

[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

h1, h2, h3 {
    color: #123B4A !important;
    font-weight: 700 !important;
}

.stApp p,
.stApp label {
    color: #294957;
