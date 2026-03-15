import json
#from src.utils.logger import logger
from src.openai.functions import submit_to_openai_api
from src.parameters.config_model import AppConfig



def handle_ai_content_generation(output_dict: dict, parameters: AppConfig) -> dict:

    json_data_string = json.dumps(output_dict, ensure_ascii=False, indent=2)
    submit_to_openai_api(json_data_string, parameters)
    # response = submit_to_openai_api(json_data_string, parameters)    
    # message = response.choices[0].message
    
    # if not message.tool_calls:
    #    # logger.warning("No tool calls detected in response")
    #     return {}

    # # Response Validation & JSON Parsing
    # try:
    #     args = message.tool_calls[0].function.arguments
    #     return json.loads(args) # dict
        

    # except json.JSONDecodeError:
    #    # logger.error("AI returned invalid JSON format")
    #    print("AI returned invalid JSON format")
    # raise
