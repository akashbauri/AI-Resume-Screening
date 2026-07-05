"""
Module: services.interview_generator

Uses the existing LLM service to generate interview questions
from the candidate profile and job description.
"""

import json
import logging

from services.llm_service import call_llm
from prompts.interview_prompt import INTERVIEW_PROMPT

# Configure logger
logger = logging.getLogger(__name__)


def generate_interview_questions(candidate_profile: dict, job_description: str) -> dict:
    """
    Generates interview questions using the AI model.

    Args:
        candidate_profile (dict):
            Parsed candidate profile.

        job_description (str):
            Job description entered by recruiter.

    Returns:
        dict:
            {
                "Technical Questions": [],
                "Behavioral Questions": [],
                "Project Questions": [],
                "HR Questions": []
            }
    """

    try:

        prompt = INTERVIEW_PROMPT.format(
            candidate_profile=json.dumps(candidate_profile, indent=2),
            job_description=job_description
        )

        logger.info("Generating AI Interview Questions...")

        response = call_llm(prompt)

        cleaned = (
            response.replace("```json", "")
            .replace("```", "")
            .strip()
        )

        questions = json.loads(cleaned)

        # Ensure all required keys exist
        required_keys = [
            "Technical Questions",
            "Behavioral Questions",
            "Project Questions",
            "HR Questions"
        ]

        for key in required_keys:

            if key not in questions:
                questions[key] = []

            if not isinstance(questions[key], list):
                questions[key] = []

        logger.info("Interview questions generated successfully.")

        return questions

    except json.JSONDecodeError as e:

        logger.error(f"Invalid JSON returned by LLM: {e}")

        return {
            "Technical Questions": [],
            "Behavioral Questions": [],
            "Project Questions": [],
            "HR Questions": [],
            "error": "Invalid JSON returned by LLM"
        }

    except Exception as e:

        logger.error(f"Interview question generation failed: {str(e)}")

        return {
            "Technical Questions": [],
            "Behavioral Questions": [],
            "Project Questions": [],
            "HR Questions": [],
            "error": str(e)
        }
