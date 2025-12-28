import json
import os
from openai import OpenAI
from config import Config

from src.openai.prompts import CORE_ANALYSIS_LOGIC, PEDAGOGY_STANDARDS, TRANSFORMATION_MODES, LANGUAGE_MODES


api_key = Config.API_KEY
client = OpenAI(api_key=api_key)

MAX_TOKENS = 6000


functions = [
    {
        "name": "generate_complete_skill",
        "description": f"Generates a complete lesson......", # ?מה לגבי פרמטרים פה, איזה צריך לשרשר 
        "parameters": {
            "type": "object",
            "properties": {
                "steps": {
                    "type": "array",
                    "description": "A JSON array of step objects, representing a sequence of lesson steps. Each step must contain full content. ",
                    "items": {
                        "type": "object",
                        "properties": {
                            "step_name": {
                                "type": "string",
                                "description": "The title of the step (generated in the specified language)."
                            },
                            "step_number": {
                                "type": "integer",
                                "description": "The sequential number of the step."
                            },
                            "widgets": {
                                "type": "object",
                                "description": "Container for content, open questions, and multiple choice questions.",
                                "properties": {
                                    "contents": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "content": {
                                                    "type": "string", # {widget_config.sentences * 5} מה לשרשר פה?
                                                    "description": f"(Generated in the specified language and should contain at least ...... sentences.) the content should be aimed at the learners directly and should match the lesson setting like age_level and level etc. If content is not required (0 expected), leave the contents array empty.",
                                                }
                                            },
                                            "required": ["content"] #widgets זה לא היה אצל נעומי, למה לא לחייב לחזיר אותם זה התוכן בתוך  
                                        },
                                        "description": "Content provided based on the learning_content_component array."
                                    }

                                }, 
                                "required": ["contents"]
                            }
                           
                        },
                        "required": ["step_name", "step_number", "widgets"]
                    }
                }
            },
            "required": ["steps"]
        }
    }
    
    
    ]




# Send json file to openAi, and return content text
def send_json_to_openai (parameters, json_data_string):
    

    # List of parameters
    source_mode = parameters["source_mode"]
    language_mode = parameters["language_mode"]
    number_words_in_file = parameters["number_words_in_file"]
    



    # PROMPTS
    final_system_message = "\n".join([

        CORE_ANALYSIS_LOGIC,
        TRANSFORMATION_MODES[source_mode],
        PEDAGOGY_STANDARDS,
        "LANGUAGE RULE",
        LANGUAGE_MODES[language_mode],
        "However:",
        LANGUAGE_MODES['language_prompt']
        
    ])
    #print(final_system_message)


    print(source_mode)
    print(language_mode)
    print(number_words_in_file)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": final_system_message
                },
                {
                    "role": "user",
                    "content": json_data_string
                }
            ],
            max_tokens=MAX_TOKENS,

            # שימוש בפורמט הכלים החדש
            tools=[
                {
                "type": "function",
                "function": functions[0]  # כאן נכנס המילון שהגדרנו קודם
                }]


             #tool_choice={"type": "function", "function": {"name": "generate_complete_skill"}}
        )


        # ====== Return Function call arguments in format Json =====
        message = response.choices[0].message

        if message.tool_calls:
            skill_args_json = message.tool_calls[0].function.arguments

        else:
            skill_args_json = None
        
        return skill_args_json
                    

    except Exception as e:
        print(f"Error calling OpenAI API: {e}")







# return {
#         "name": "generate_complete_skill",
#         "description": f"Generates a complete lesson based on the '{goal.value}' goal. {goal_description}.",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "steps": {
#                     "type": "array",
#                     "description": "A JSON array of step objects, representing a sequence of lesson steps. Each step must contain full content. ",
#                     "items": {
#                         "type": "object",
#                         "properties": {
#                             "step_name": {
#                                 "type": "string",
#                                 "description": "The title of the step (generated in the specified language)."
#                             },
#                             "step_number": {
#                                 "type": "integer",
#                                 "description": "The sequential number of the step."
#                             },
#                             "widgets": {
#                                 "type": "object",
#                                 "description": "Container for content, open questions, and multiple choice questions.",
#                                 "properties": {
#                                     "contents": {
#                                         "type": "array",
#                                         "items": {
#                                             "type": "object",
#                                             "properties": {
#                                                 "content_type": {
#                                                     "type": "string",
#                                                     # למה אין לו פה תיאור
#                                                 },
#                                                 "content": {
#                                                     "type": "string",
#                                                     "description": f"(Generated in the specified language and should contain at least {widget_config.sentences * 5} sentences.) the content should be aimed at the learners directly and should match the lesson setting like age_level and level etc. If content is not required (0 expected), leave the contents array empty.",
#                                                 },
#                                             },
#                                             "description": "Content provided based on the learning_content_component array; leave empty if none."
#                                         },
#                                         "minItems": widget_config.content,
#                                         "maxItems": widget_config.content,
#                                     },
#                                 "required": ["contents"]
#                             },
                           
#                         },
#                         "required": ["step_name", "step_number", "widgets"]
#                     }
#                 }
#             },
#             "required": ["steps"]
#         }
#     }