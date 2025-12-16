import json
import os
from openai import OpenAI
from config import Config

from src.openai.prompts import SYSTEM_INSTRUCTIONS
from src.parsers.utils import read_file_json


api_key = Config.API_KEY
client = OpenAI(api_key=api_key)

MAX_TOKENS = 8000

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
def send_json_to_openai (json_data):
    
    json_data_string = json.dumps(json_data, ensure_ascii=False)
    path_params_file = "/Users/hrwnmshsmsyn/Desktop/project-files-feature/src/parameters/source_mode .json"
    parameters = read_file_json(path_params_file)

    # List of parameters
    source_mode = parameters["source_mode"]

    print (source_mode)

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system", 
                    "content": SYSTEM_INSTRUCTIONS
                 },
                {
                    "role": "system", 
                    "content": f"The value of source_mode is: {source_mode}. Apply the rules strictly."
                 },
                {
                    "role": "user", 
                    "content": json_data_string
                }
            ],
            #functions=functions
            max_tokens=MAX_TOKENS
        )

        return response.choices[0].message.content

        # # ====== Return Function call arguments in format Json =====
        # function_call = response.choices[0].message.function_call

        # if function_call:
        #     skill_object = json.loads(function_call.arguments)
        
        # else:
        #     skill_object = None
        
        # return skill_object
            

    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
    






