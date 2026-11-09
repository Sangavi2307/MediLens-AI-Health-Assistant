
import json
import streamlit as st

from openai import OpenAI


def get_openai_client():
    """Create an OpenAI client using Streamlit Secrets."""

    try:
        api_key = st.secrets["OPENAI_API_KEY"]

        return OpenAI(api_key=api_key)

    except Exception:
        st.error(
            "OpenAI API key is missing. "
            "Please configure OPENAI_API_KEY in Streamlit Secrets."
        )
        return None


def generate_ai_explanation(results):
    """
    Generate simple educational explanations
    for analyzed medical test results.
    """

    if not results:
        return "No medical test results are available to explain."

    client = get_openai_client()

    if client is None:
        return None

    # Send structured test results rather than the full report.
    test_data = json.dumps(
        results,
        indent=2,
        ensure_ascii=False
    )

    instructions = """
You are MediLens, an educational medical report
explanation assistant.

Your responsibilities:

1. Explain each test result in simple English.
2. Explain what the test generally measures.
3. Explain whether the value is below, within or above
   the supplied reference range.
4. Explain that reference ranges can vary between laboratories.
5. Identify results that should be discussed with a healthcare
   professional.
6. Use clear headings and short paragraphs.

IMPORTANT SAFETY RULES:

- Do not diagnose diseases.
- Do not prescribe medicines or treatments.
- Do not recommend changing medication.
- Do not invent missing test values or reference ranges.
- Do not claim that a normal result guarantees good health.
- Do not create unnecessary fear.
- Explain that abnormal results need professional interpretation.
- If a result may indicate an urgent concern, advise the user
  to seek prompt medical assessment.
- Make clear that this is educational information, not
  a substitute for professional medical advice.
"""

    try:

        response = client.responses.create(
            model="gpt-5.5",
            instructions=instructions,
            input=(
                "Explain the following medical test results "
                "in simple English:\n\n"
                + test_data
            ),
            store=False
        )

        return response.output_text

    except Exception as error:

        st.error(
            "Unable to generate the AI explanation. "
            "Please check your API configuration."
        )

        st.caption(str(error))

        return None


def render_ai_explanation(results):

    """Display AI-generated medical report explanations."""

    st.title("AI Medical Report Explanation")

    st.write(
        "Understand your medical test results "
        "through simple educational explanations."
    )

    if not results:

        st.warning(
            "Please complete medical test analysis first."
        )
        return

    st.info(
        "AI explanations are educational and do not "
        "provide a medical diagnosis."
    )

    if st.button(
        "Generate AI Explanation",
        use_container_width=True
    ):

        with st.spinner(
            "Generating your AI explanation..."
        ):

            explanation = generate_ai_explanation(results)

            if explanation:

                st.session_state.ai_explanation = explanation

                st.success(
                    "AI explanation generated successfully!"
                )

    saved_explanation = st.session_state.get(
        "ai_explanation"
    )

    if saved_explanation:

        st.subheader("Your AI Explanation")

        st.markdown(saved_explanation)

        st.divider()

        st.warning(
            "Please consult a qualified healthcare professional "
            "before making medical decisions. MediLens does not "
            "diagnose conditions or prescribe treatment."
        )
      
