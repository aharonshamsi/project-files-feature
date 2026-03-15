"""
LLM Skill Generation Module
===========================

This module is responsible for:
1. Building the system prompt for the LLM.
2. Defining the JSON schema used for structured skill generation.
3. Submitting the request to the LLM via LiteLLM.

The LLM returns a structured learning skill composed of:
- Steps
- Instructional content
- Assessment widgets (open questions, MCQ, assignments)
"""

# ======================================================================
# Imports
# ======================================================================

# from openai import OpenAI
import litellm

from src.parameters.config_model import AppConfig
from src.openai.prompts import (
    CORE_ANALYSIS_LOGIC,
    TRANSFORMATION_MODES,
    LANGUAGE_MODES,
    QUESTION_MODE
)

# ======================================================================
# Constants
# ======================================================================

MAX_TOKENS = 30000


# ======================================================================
# Schema Builder
# ======================================================================

def get_skill_generation_schema(open_q_count, mcq_count, assign_count, language_mode):
    """
    Build the function schema used by the LLM tool calling interface.

    The schema defines the structure of the generated learning skill,
    including steps, instructional content, and assessment widgets.

    Parameters
    ----------
    open_q_count : int
        Number of open-ended questions required per step.

    mcq_count : int
        Number of multiple-choice questions required per step.

    assign_count : int
        Number of assignment/file submission questions required per step.

    language_mode : str
        The language in which the entire output must be generated.

    Returns
    -------
    dict
        JSON schema describing the required output structure.
    """

    return {
        "name": "generate_complete_skill",
        "description": (
            "Generates a complete structured learning skill based on structured JSON input."
            "Instructional learning text for the learner. "
            "Must not include questions or assessment elements. "
            f"MUST be written entirely in {language_mode}. "
            "If any other language appears, the output is invalid."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "steps": {
                    "type": "array",
                    "description": "An ordered list of lesson steps composing the learning skill.",
                    "items": {
                        "type": "object",
                        "properties": {

                            "step_name": {
                                "type": "string",
                                "description": "The title of the step."
                            },

                            "step_number": {
                                "type": "integer",
                                "description": "The sequential number of the step."
                            },

                            "widgets": {
                                "type": "object",
                                "description": (
                                    "Container for all instructional and assessment widgets of the step. "
                                    "Each widget group represents a single content type."
                                ),
                                "properties": {

                                    # ------------------------------------------------------
                                    # Instructional Content
                                    # ------------------------------------------------------
                                    "contents": {
                                        "type": "array",
                                        "description": (
                                            "An ordered list of instructional content widgets. "
                                            "Each item contains pure learning text only."
                                        ),
                                        "items": {
                                            "type": "object",
                                            "properties": {

                                                "content_type": {
                                                    "type": "string",
                                                    "description": "The type of content. Always use 'text'."
                                                },

                                                "content": {
                                                    "type": "string",
                                                    "description": (
                                                        "Instructional learning text for the learner. "
                                                        "Must not include questions or assessment elements."
                                                    )
                                                }

                                            },
                                            "required": ["content_type", "content"]
                                        }
                                    },

                                    # ------------------------------------------------------
                                    # Open Questions
                                    # ------------------------------------------------------
                                    "open_questions": {
                                        "type": "array",
                                        "description": (
                                            f"List of open-ended questions for the step. "
                                            f"Must contain exactly {open_q_count} questions."
                                        ),
                                        "items": {
                                            "type": "string",
                                            "description": "An open-ended question requiring a written response."
                                        }
                                    },

                                    # ------------------------------------------------------
                                    # Multiple Choice Questions
                                    # ------------------------------------------------------
                                    "multiple_choice_questions": {
                                        "type": "array",
                                        "description": (
                                            f"List of multiple-choice questions for the step. "
                                            f"Must contain exactly {mcq_count} questions."
                                        ),
                                        "items": {
                                            "type": "object",
                                            "properties": {

                                                "question": {
                                                    "type": "string",
                                                    "description": "The question text."
                                                },

                                                "options": {
                                                    "type": "array",
                                                    "description": (
                                                        "Answer options (A–D). Exactly one option must be correct."
                                                    ),
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {

                                                            "key": {
                                                                "type": "string",
                                                                "description": "The answer option text."
                                                            },

                                                            "correct_answer": {
                                                                "type": "boolean",
                                                                "description": (
                                                                    "Indicates whether this option is the correct answer."
                                                                )
                                                            }

                                                        },
                                                        "required": ["key", "correct_answer"]
                                                    }
                                                }

                                            },
                                            "required": ["question", "options"]
                                        }
                                    },

                                    # ------------------------------------------------------
                                    # Assignment / File Submission Questions
                                    # ------------------------------------------------------
                                    "file_questions": {
                                        "type": "array",
                                        "description": (
                                            f"Assignment-based questions for the step requiring file submission. "
                                            f"Must contain exactly {assign_count} assignments."
                                        ),
                                        "items": {
                                            "type": "string",
                                            "description": (
                                                "An assignment task requiring the learner to submit a file "
                                                "(e.g., document, image, video)."
                                            )
                                        }
                                    }

                                },

                                "required": [
                                    "contents",
                                    "open_questions",
                                    "multiple_choice_questions",
                                    "file_questions"
                                ]
                            }

                        },
                        "required": ["step_name", "step_number", "widgets"]
                    }
                }
            },
            "required": ["steps"]
        }
    }


# ======================================================================
# Prompt Builder
# ======================================================================

def build_system_prompts(source_mode: str, language_mode: str,
                         open_q_count: int, mcq_count: int, assign_count: int) -> str:
    """
    Build the complete system prompt sent to the LLM.

    The prompt combines:
    - Language enforcement rules
    - Core analysis logic
    - Transformation mode
    - Assessment generation rules

    Returns
    -------
    str
        The final system prompt string.
    """

    return "\n".join([

        "LANGUAGE RULE",
        LANGUAGE_MODES['general_language_rules'],
        LANGUAGE_MODES[language_mode],

        CORE_ANALYSIS_LOGIC,
        TRANSFORMATION_MODES[source_mode],

        f"Create {open_q_count} OPEN QUESTIONS based strictly on the step content, following these rules: {QUESTION_MODE['open_questions']}",
        f"Create {mcq_count} MULTIPLE CHOICE QUESTIONS based strictly on the step content, following these rules: {QUESTION_MODE['multiple_choice_questions']}",
        f"Create {assign_count} ASSIGNMENT QUESTIONS based strictly on the step content, following these rules: {QUESTION_MODE['assignment_questions']}"

    ])


# ======================================================================
# LLM API Submission
# ======================================================================

def submit_to_llm_api(json_data_string, parameters: AppConfig):
    """
    Submit the request to the LLM using LiteLLM.

    The function:
    1. Extracts configuration parameters.
    2. Builds the system prompt.
    3. Generates the tool schema.
    4. Sends the request to the model.

    Parameters
    ----------
    json_data_string : str
        Structured input JSON string containing the source content.

    parameters : AppConfig
        Application configuration containing model selection and
        question counts.

    Returns
    -------
    dict
        LLM response object.
    """

    # --------------------------------------------------------------
    # Extract parameters
    # --------------------------------------------------------------

    model_name = parameters.model_name
    source_mode = parameters.source_mode
    language_mode = parameters.language_mode

    open_q_count = parameters.open_questions_count
    mcq_count = parameters.multiple_choice_questions_count
    assign_count = parameters.file_questions_count

    # --------------------------------------------------------------
    # Debug prints (for testing)
    # --------------------------------------------------------------

    print(model_name)
    print(source_mode)
    print(language_mode)

    print(f"open_questions_count: {open_q_count}")
    print(f"multiple_choice_questions_count: {mcq_count}")
    print(f"file_questions_count: {assign_count}")

    # --------------------------------------------------------------
    # Build prompt and schema
    # --------------------------------------------------------------

    system_prompts = build_system_prompts(
        source_mode,
        language_mode,
        open_q_count,
        mcq_count,
        assign_count
    )

    functions_definition = get_skill_generation_schema(
        open_q_count,
        mcq_count,
        assign_count,
        language_mode
    )

    # --------------------------------------------------------------
    # Call LLM API
    # --------------------------------------------------------------

    try:
        response = litellm.completion(
            model=model_name,

            messages=[
                {
                    "role": "system",
                    "content": system_prompts
                },
                {
                    "role": "user",
                    "content": json_data_string
                }
            ],

            tools=[{
                "type": "function",
                "function": functions_definition
            }],

            tool_choice={
                "type": "function",
                "function": {"name": "generate_complete_skill"}
            },

            max_tokens=MAX_TOKENS,
        )

        return response

    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        