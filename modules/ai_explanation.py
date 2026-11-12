
import streamlit as st
from openai import OpenAI


# ==========================================
# OPENAI CLIENT
# ==========================================

def get_openai_client():

    try:

        api_key = st.secrets["OPENAI_API_KEY"]

        if not api_key:
            raise ValueError("OpenAI API key is empty.")

        return OpenAI(api_key=api_key)

    except Exception as error:

        raise RuntimeError(
            "OpenAI API key is missing or incorrect. "
            "Please check Streamlit Secrets."
        ) from error


# ==========================================
# AI MEDICAL REPORT EXPLANATION
# ==========================================

def ai_explain_report(report_text):

    if not report_text or not str(report_text).strip():

        raise ValueError(
            "Medical report text is empty."
        )

    client = get_openai_client()

    instructions = """
You are MediLens, an educational medical report
explanation assistant.

Explain the following medical report in simple English.

Your responsibilities:

1. Summarize the medical report.
2. Explain each available laboratory test.
3. Explain values marked Below, Within or Above.
4. Explain medical terminology in simple language.
5. Explain the meaning of the supplied reference ranges.
6. Identify results that should be discussed with a doctor.
7. Use clear headings and short paragraphs.

IMPORTANT SAFETY RULES:

- Do not diagnose diseases.
- Do not prescribe medicines or treatments.
- Do not recommend changing medication.
- Do not invent missing test values.
- Do not invent reference ranges.
- Do not claim normal results guarantee good health.
- Do not create unnecessary fear.
- Explain that laboratory reference ranges may vary.
- Recommend consulting a qualified healthcare professional.
- Clearly state that this is educational information,
  not a medical diagnosis.
"""

    try:

        response = client.responses.create(
            model="gpt-5.5",
            instructions=instructions,
            input=(
                "Explain this medical report in simple language:\n\n"
                + str(report_text)
            ),
            store=False
        )

        explanation = response.output_text

        if not explanation:

            raise RuntimeError(
                "AI returned an empty explanation."
            )

        return explanation

    except Exception as error:

        raise RuntimeError(
            f"AI explanation failed: {error}"
        ) from error
        
