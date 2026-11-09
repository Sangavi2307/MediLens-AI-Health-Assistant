
import streamlit as st
import pandas as pd


def get_risk_summary(results):
    """
    Summarize analyzed test results for monitoring.
    This does not calculate disease risk.
    """

    summary = {
        "Below": 0,
        "Within": 0,
        "Above": 0,
        "Needs review": 0
    }

    for result in results:

        status = result.get("status", "Needs review")

        if status in summary:
            summary[status] += 1
        else:
            summary["Needs review"] += 1

    return summary


def render_risk_monitoring(results=None):

    st.title("Health Risk Monitoring")

    st.write(
        "Review medical test results and identify "
        "values that may need further professional attention."
    )

    st.info(
        "This feature monitors reported test values. "
        "It does not predict diseases or provide a medical diagnosis."
    )

    if results is None:
        results = st.session_state.get(
            "analysis_results",
            []
        )

    if not results:

        st.warning(
            "No analyzed medical report is available yet. "
            "Upload a report and complete Medical Test Analysis first."
        )
        return

    summary = get_risk_summary(results)

    st.subheader("Current Monitoring Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Below Range", summary["Below"])
    col2.metric("Within Range", summary["Within"])
    col3.metric("Above Range", summary["Above"])
    col4.metric("Needs Review", summary["Needs review"])

    st.divider()

    st.subheader("Test Result Monitoring")

    dataframe = pd.DataFrame(results)

    st.dataframe(
        dataframe,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Results Requiring Attention")

    attention_results = [
        result for result in results
        if result.get("status") in [
            "Below",
            "Above",
            "Needs review"
        ]
    ]

    if attention_results:

        for result in attention_results:

            test_name = result.get(
                "test_name",
                "Unknown test"
            )

            value = result.get("value", "Not available")

            unit = result.get("unit", "")

            status = result.get(
                "status",
                "Needs review"
            )

            with st.expander(
                f"{test_name} - {status}"
            ):

                st.write(f"**Result:** {value} {unit}")

                st.write(f"**Status:** {status}")

                st.warning(
                    "Discuss this result with a qualified "
                    "healthcare professional. The importance "
                    "of a result depends on your health history "
                    "and laboratory reference range."
                )

    else:

        st.success(
            "No below-range, above-range or unreviewed "
            "results were identified in this analysis."
        )

    st.divider()

    st.subheader("Monitoring Guidance")

    st.write(
        """
        - Keep copies of previous medical reports.
        - Compare results using the same laboratory's
          reference ranges when possible.
        - Follow the testing schedule recommended by
          your healthcare professional.
        - Discuss unexpected or changing results with
          a qualified healthcare professional.
        """
    )

    st.caption(
        "A result within a reference range does not guarantee "
        "that a person is healthy. Seek medical care for "
        "concerning symptoms regardless of test results."
          )
  
