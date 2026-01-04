import os
import json
from src.utils.logger import logger
import time


from src.parsers.docx_handler import extract_docx_file_to_json
from src.parsers.pdf_handler import extract_pdf_file_to_json
from src.parsers.utils import load_json_to_dict, get_file_extension_type
from src.openai.functions import send_json_to_openai


def main():

    start_time = time.time()
    logger.info("Execution started")

    try:

        
        #=========== READ PARAMETERS FILE ============================
        # Reads a json file (PARAMETERS), and returns a dictionary
        path_params_file = "src/parameters/parameters.json"
        logger.info(f"Read file parameters {path_params_file}")
        parameters = load_json_to_dict(path_params_file)

        # Path of the file input in parameter
        file_path_input = parameters['input_file']

        # Get input file name extension (DOCX || PDF)
        file_type = get_file_extension_type(file_path_input)



        #=========== PARSERS FILE ============================
        logger.info(f"Extracting content from file: {file_path_input}")

        # Path to the output JSON file generated after parser
        file_path_output_json = "data/outputs/output.json"

        if file_type == "docx":
            number_words_in_file = extract_docx_file_to_json(file_path_input, file_path_output_json)
        
        elif file_type == "pdf":
            number_words_in_file = extract_pdf_file_to_json(file_path_input, file_path_output_json)


        # Add parameter of number_words_in_file in dict
        parameters["number_words_in_file"] = number_words_in_file 
        

        

    #========= OPEN AI ====================================
    # Sending to OpenAi
        logger.info(f"Sending output file to OpenAI: {file_path_output_json}")
        with open(file_path_output_json, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            json_data_string = json.dumps(json_data, ensure_ascii=False)


        response = send_json_to_openai(parameters, json_data_string)    

        message = response.choices[0].message
        
        if message.tool_calls:
            args = message.tool_calls[0].function.arguments

            # Response Validation & JSON Parsing
            try:
                data_dict = json.loads(args) # dict
                print(data_dict)

            except json.JSONDecodeError:
                logger.error("AI returned invalid JSON format")
                raise

        else:
            logger.warning("No tool calls detected in response")
        



        # End time
        end_time = time.time()
        logger.info(f"Execution completed successfully in {end_time - start_time:.2f} seconds")


    except ValueError as e:
        logger.error(f"Input error: {e}")

    except FileNotFoundError as e:
        logger.error(f"File error: {e}")

    except PermissionError as e:
        logger.error(f"Permission error: {e}")

    except json.JSONDecodeError as e:
        logger.error(f"JSON error: {e}")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()


