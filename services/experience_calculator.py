"""
Module: services.experience_calculator

Description:
Calculates the total work experience of a candidate based on
the Experience list extracted from the resume.
"""

import re
import logging
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)

# Month mapping
MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def parse_date(date_text: str):
    """
    Convert text like:

    Jan 2023
    January 2023
    Present
    Current
    Now

    into a datetime object.
    """

    if not date_text:
        return None

    text = str(date_text).strip().lower()

    if text in ["present", "current", "now"]:
        return datetime.today()

    match = re.search(r"([A-Za-z]+)\s+(\d{4})", text)

    if not match:
        return None

    month_name = match.group(1).lower()
    year = int(match.group(2))

    month = MONTHS.get(month_name)

    if month is None:
        return None

    return datetime(year, month, 1)


def calculate_total_experience(experience_list):
    """
    Calculates the total work experience from the parsed
    experience list.

    Example Input:

    [
        {
            "Job Title": "...",
            "Company": "...",
            "Duration": "Jan 2023 - Jul 2025"
        }
    ]

    Returns:

    "2 Years 6 Months"
    """

    try:

        if not isinstance(experience_list, list):
            return "0 Months"

        total_months = 0

        for experience in experience_list:

            duration = str(
                experience.get("Duration", "")
            ).strip()

            if "-" not in duration:
                continue

            start_text, end_text = duration.split("-", 1)

            start_date = parse_date(start_text)
            end_date = parse_date(end_text)

            if start_date is None or end_date is None:
                continue

            months = (
                (end_date.year - start_date.year) * 12
                + (end_date.month - start_date.month)
            )

            if months > 0:
                total_months += months

        years = total_months // 12
        months = total_months % 12

        if years == 0:
            return f"{months} Months"

        return f"{years} Years {months} Months"

    except Exception as error:
        logger.error(
            f"Experience calculation failed: {str(error)}"
        )
        return "0 Months"
