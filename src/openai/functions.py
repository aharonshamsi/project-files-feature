import json
import os
from openai import OpenAI
from config import Config

from src.openai.prompts import CORE_ANALYSIS_LOGIC, PEDAGOGY_STANDARDS, TRANSFORMATION_MODES, LANGUAGE_MODES


api_key = Config.API_KEY
client = OpenAI(api_key=api_key)

MAX_TOKENS = 6000

# functions = [
#     {
#         "name": "generate_complete_skill",
#         "description": "", # חסר תיאור 
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "steps": {
#                     "type": "array",
#                     "description": "A JSON array of step objects, representing a sequence of lesson steps. Each step must contain full content.",
#                     "items": {
#                         "type": "object",
#                         "properties": {
#                             "step_name": {
#                                 "type": "string",
#                                 "description": "The title of the step (generated in the specified language)."
#                             },
#                             "step_number": {
#                                 "type": "string",
#                                 "description": "The sequential number of the step."
#                             },
#                             "content": {
#                                 "type": "string",
#                                 "description": "The instructional content or explanation for this step."
#                             }
#                         },
#                         "required": ["step_name", "step_number", "content"]
#                     }
#                 }
#             },
#             "required": ["steps"]
#         }
#     }
# ]




# Send json file to openAi, and return content text
def send_json_to_openai (parameters, json_data_string):
    

    # List of parameters
    source_mode = parameters["source_mode"]
    language_mode = parameters["language_mode"]


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

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
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
            max_tokens=MAX_TOKENS
        )


        print( response.choices[0].message.content)

        # # ====== Return Function call arguments in format Json =====
        # function_call = response.choices[0].message.function_call

        # if function_call:
        #     skill_object = json.loads(function_call.arguments)
        
        # else:
        #     skill_object = None
        
        # return skill_object
            

    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
    






