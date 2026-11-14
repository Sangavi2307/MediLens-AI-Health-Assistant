
import streamlit as st
from google import genai
from google.genai import types


def get_gemini_client():
    """Create a Gemini client using Streamlit Secrets."""

    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")

        if not api_key:
            raise ValueError("Gemini API key is missing.")

        return genai.Client(api_key=api_key)

    except Exception as error:
        raise RuntimeError(
            "Unable to connect to Gemini. "
            "Please check your GEMINI_API_KEY in Streamlit Secrets."
        ) from error


def ai_explain_report(report_text, language="English"):
    """
    Generate an AI explanation of a medical laboratory report.

    Parameters:
        report_text: Extracted text from the uploaded medical report.
        language: English or Tamil.

    Returns:
        AI-generated medical report explanation.
    """

    if not report_text or not str(report_text).strip():
        raise ValueError("Medical report text is empty.")

    client = get_gemini_client()

    instructions = """
You are MediLens, an AI medical laboratory report explanation assistant.

Your job is to explain the complete medical laboratory report
in simple language using the actual information supplied.

IMPORTANT REQUIREMENTS:

1. Read the complete medical report carefully.
2. Identify every laboratory test in the report.
3. Explain the purpose of every identified test.
4. Show the actual result for each test.
5. Include the unit and reference range when provided.
6. Explain whether each result is low, normal, high,
   or cannot be determined.
7. Explain medical terminology in simple words.
8. Explain possible general reasons for abnormal results.
9. Explain which findings should be discussed with a doctor.
10. Provide a short overall summary of the report.
11. Use clear headings and tables where appropriate.
12. Do not ignore tests simply because they are unfamiliar.

STRICT MEDICAL SAFETY RULES:

- Never invent laboratory results.
- Never invent units or reference ranges.
- Use reference ranges printed in the report.
- If a reference range is missing, clearly mention it.
- Do not diagnose any disease.
- Do not prescribe medicines.
- Do not recommend changing prescribed medicines.
- Do not create unnecessary fear.
- Explain that reference ranges can vary between laboratories.
- Mention that results must be interpreted with symptoms
  and medical history by a qualified healthcare professional.
- This explanation is educational, not a medical diagnosis.

OUTPUT STRUCTURE:

1. Medical Report Summary
2. Patient Information (only if present in the report)
3. Complete Laboratory Test Explanation
4. Abnormal Results and Their Possible General Causes
5. Normal Results
6. Important Findings to Discuss with a Doctor
7. Overall Explanation
8. Medical Disclaimer

For the laboratory test explanation, use a table with:
Test Name | Actual Result | Unit | Reference Range | Status | Explanation

Explain the report in the language requested by the user.
"""


    prompt = f"""
Please explain this complete medical laboratory report
in {language}.

Do not skip any laboratory test.

MEDICAL REPORT TEXT:

{str(report_text)}
"""


    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=instructions,
                temperature=0.3,
                max_output_tokens=5000
            )
        )

        explanation = response.text

        if not explanation or not explanation.strip():
            raise RuntimeError(
                "Gemini returned an empty explanation."
            )

        return explanation

    except Exception as error:
        raise RuntimeError(
            f"Gemini AI explanation failed: {error}"
        ) from error
