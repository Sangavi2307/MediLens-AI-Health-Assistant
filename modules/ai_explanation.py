
import streamlit as st
from google import genai
from google.genai import types


# ==========================================
# GEMINI AI CLIENT
# ==========================================

def get_gemini_client():

    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")

        if not api_key:
            raise ValueError("Gemini API key is missing.")

        return genai.Client(api_key=api_key)

    except Exception as error:
        raise RuntimeError(
            "Unable to connect to Gemini. "
            "Please check Streamlit Secrets."
        ) from error


# ==========================================
# AI MEDICAL REPORT EXPLANATION
# ==========================================

def ai_explain_report(report_text, language="English"):

    if not report_text or not str(report_text).strip():
        raise ValueError("Medical report text is empty.")

    client = get_gemini_client()

    instructions = """
You are MediLens, an AI medical report explanation assistant.

Your task is to explain medical laboratory reports
using the actual information supplied in the report.

REQUIREMENTS:

1. Summarize the complete medical report.
2. Explain every laboratory test found in the report.
3. Explain the purpose of each test.
4. Explain the patient's actual result.
5. Explain the supplied reference range and unit.
6. Explain whether a result is low, normal or high
   when the report provides enough information.
7. Explain medical terminology in simple language.
8. Explain possible general reasons for abnormal results,
   without claiming that they are the patient's diagnosis.
9. Mention results that should be discussed with a doctor.
10. Use headings, tables and simple explanations.

IMPORTANT RULES:

- Do not diagnose diseases.
- Do not prescribe medicines.
- Do not recommend changing medication.
- Never invent test results or reference ranges.
- Do not assume a missing reference range.
- If a test is unfamiliar, clearly say so.
- Use the reference ranges printed in the report.
- Explain that reference ranges may vary between laboratories.
- Do not create unnecessary fear.
- This is educational information, not a medical diagnosis.

Explain the report in the requested language.
"""

    prompt = f"""
Explain the following medical report in {language}.

MEDICAL REPORT:

{str(report_text)}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=instructions,
                temperature=0.3,
                max_output_tokens=5000
            )
        )

        explanation = response.text

        if not explanation or not explanation.strip():
            raise RuntimeError("Gemini returned an empty explanation.")

        return explanation

    except Exception as error:
        raise RuntimeError(
            f"Gemini AI explanation failed: {error}"
        ) from error
