import re


# Common medical test names and their reference ranges.
# These are illustrative adult ranges, not universal
# clinical decision limits.

TEST_RANGES = {
    "hemoglobin": {
        "aliases": ["hb", "haemoglobin", "hemoglobin"],
        "unit": "g/dL",
        "min": 12.0,
        "max": 16.0
    },
    "wbc": {
        "aliases": [
            "wbc",
            "white blood cell count",
            "total leukocyte count",
            "tlc"
        ],
        "unit": "cells/uL",
        "min": 4000,
        "max": 11000
    },
    "platelets": {
        "aliases": [
            "platelet count",
            "platelets",
            "platelet"
        ],
        "unit": "cells/uL",
        "min": 150000,
        "max": 450000
    },
    "glucose": {
        "aliases": [
            "fasting blood sugar",
            "fasting glucose",
            "fbs",
            "blood glucose"
        ],
        "unit": "mg/dL",
        "min": 70,
        "max": 99
    },
    "cholesterol": {
        "aliases": [
            "total cholesterol",
            "cholesterol"
        ],
        "unit": "mg/dL",
        "min": 0,
        "max": 200
    },
    "vitamin d": {
        "aliases": [
            "vitamin d",
            "25-oh vitamin d",
            "25 hydroxy vitamin d"
        ],
        "unit": "ng/mL",
        "min": 20,
        "max": 100
    },
    "creatinine": {
        "aliases": ["creatinine"],
        "unit": "mg/dL",
        "min": 0.6,
        "max": 1.3
    },
    "urea": {
        "aliases": ["blood urea", "urea"],
        "unit": "mg/dL",
        "min": 15,
        "max": 45
    }
}


def detect_status(value, minimum, maximum):
    """Compare a result with the configured reference range."""

    if value < minimum:
        return "Below"

    elif value > maximum:
        return "Above"

    return "Within"


def analyze_report(report_text):
    """
    Extract supported test values from report text.

    Returns a list of dictionaries containing test name,
    value, unit, reference range and status.
    """

    if not report_text or not report_text.strip():
        return []

    results = []
    processed_tests = set()

    for test_name, details in TEST_RANGES.items():

        for alias in details["aliases"]:

            pattern = (
                r"(?<![A-Za-z])"
                + re.escape(alias)
                + r"(?![A-Za-z])"
                + r"\s*[:\-]?\s*"
                + r"([-+]?\d[\d,]*(?:\.\d+)?)"
            )

            match = re.search(
                pattern,
                report_text,
                flags=re.IGNORECASE
            )

            if match:

                if test_name in processed_tests:
                    break

                try:
                    value = float(
                        match.group(1).replace(",", "")
                    )

                    minimum = details["min"]
                    maximum = details["max"]

                    status = detect_status(
                        value,
                        minimum,
                        maximum
                    )

                    results.append({
                        "test_name": test_name.title(),
                        "value": value,
                        "unit": details["unit"],
                        "reference_range": (
                            f"{minimum} - {maximum}"
                        ),
                        "status": status
                    })

                    processed_tests.add(test_name)

                except (ValueError, TypeError):
                    continue

                break

    return results


def get_analysis_summary(results):
    """Count results by status."""

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
