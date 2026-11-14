
"""
MediLens - Gemini AI Medical Report Explainer
Includes automatic retries for temporary Gemini server errors.
"""

import time
import streamlit as st
from google import genai
from google.genai import types


# --------------------------------------------------
# GEMINI CLIENT
# --------------------------------------------------

def get_gemini_client():

    api_key = st.secrets.get("GEMINI_API_KEY", "")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing from Streamlit Secrets."
        )

    return genai.Client(api_key=api_key)


# --------------------------------------------------
# ERROR DETECTION
# --------------------------------------------------

def is_temporary_error(error):

    message = str(error).upper()

    temporary_errors = [
        "503",
        "UNAVAILABLE",
        "HIGH DEMAND",
        "OVERLOADED",
        "INTERNAL SERVER ERROR",
        "502",
        "504"
    ]

    return any(item in message for item in temporary_errors)


# --------------------------------------------------
# AI REPORT EXPLANATION
# --------------------------------------------------

def ai_explain_report(report_text, language="English"):

    if not report_text or not str(report_text).strip():
        raise ValueError(
            "No medical report text was provided."
        )

    client = get_gemini_client()

    instructions = """
You are MediLens, an AI medical laboratory report
explanation assistant.

Your task is to explain the complete medical report
in simple language.

IMPORTANT REQUIREMENTS:

1. Read the complete report carefully.
2. Identify every laboratory test.
3. Explain the purpose of each test.
4. Show the actual result, unit and reference range
   when available.
5. Explain whether the result is low, normal, high
   or cannot be determined.
6. Explain medical terminology in simple language.
7. Explain possible general reasons for abnormal
   results without diagnosing diseases.
8. Identify findings that should be discussed
   with a qualified doctor.
9. Include an overall report summary.
10. Do not skip unfamiliar laboratory tests.

STRICT SAFETY RULES:

- Never invent laboratory results.
- Never invent units or reference ranges.
- Use reference ranges printed in the report.
- If a range is missing, say it is not provided.
- Do not diagnose diseases.
- Do not prescribe medicines.
- Do not recommend changing prescribed medicines.
- Do not create unnecessary fear.
- Explain that laboratory ranges can vary.
- Explain that results require clinical interpretation.
- This is educational information, not a diagnosis.

OUTPUT STRUCTURE:

1. Medical Report Summary
2. Patient Information (only if available)
3. Complete Laboratory Test Explanation
4. Abnormal Results and Possible General Causes
5. Normal Results
6. Important Findings to Discuss with a Doctor
7. Overall Explanation
8. Medical Disclaimer

For laboratory results, use a table containing:

Test Name | Actual Result | Unit |
Reference Range | Status | Explanation

Explain everything in the requested language.
"""

    prompt = f"""
Please explain this complete medical laboratory report
in {language}.

Do not skip any laboratory test.

MEDICAL REPORT:

{str(report_text)}
"""

    # Retry temporary server errors up to 3 times.
    max_attempts = 3

    for attempt in range(max_attempts):

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

            if is_temporary_error(error):

                if attempt < max_attempts - 1:

                    wait_seconds = 2 ** (attempt + 1)

                    time.sleep(wait_seconds)

                    continue

                raise RuntimeError(
                    "Gemini is temporarily experiencing "
                    "high demand. MediLens tried again "
                    "automatically, but the service is "
                    "still unavailable. Please try again "
                    "after a few minutes."
                ) from error

            raise RuntimeError(
                f"Gemini AI explanation failed: {error}"
            ) from error

    raise RuntimeError(
        "Unable to generate the AI explanation."
    )
