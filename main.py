import os
import json

from src.parsers.docx_handler import extract_docx_file_to_json
from src.parsers.pdf_handler import extract_pdf_file_to_json
from src.parsers.utils import load_json_to_dict, get_file_extension_type
from src.openai.functions import send_json_to_openai


def main():

    try:

        #=========== PARSERS FILE ============================
        # Reads a json file (PARAMETERS), and returns a dictionary
        path_params_file = "/Users/hrwnmshsmsyn/Desktop/project-files-feature/src/parameters/parameters.json"
        parameters = load_json_to_dict(path_params_file)

        # Path of the file input in parameter
        file_path_input = parameters['input_file']

        # Get input file name extension (DOCX || PDF)
        file_type = get_file_extension_type(file_path_input)

        # Path to the output JSON file generated after parser
        file_path_output_json = "/Users/hrwnmshsmsyn/Desktop/project-files-feature/data/outputs/output.json"

        # File DOCX
        if file_type == "docx":
            number_words_in_file = extract_docx_file_to_json(file_path_input, file_path_output_json)
        
        # File PDF
        elif file_type == "pdf":
            number_words_in_file = extract_pdf_file_to_json(file_path_input, file_path_output_json)


        # Add parameter of number_words_in_file in dict
        parameters["number_words_in_file"] = number_words_in_file 
        

    #========= OPEN AI ====================================
    # Send to OpenAi

        with open(file_path_output_json, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            json_data_string = json.dumps(json_data, ensure_ascii=False)



        result = send_json_to_openai(parameters, json_data_string)
        print(result)



    except ValueError as e:
        print(f"Input error: {e}")

    except FileNotFoundError as e:
        print(f"File error: {e}")

    except PermissionError as e:
        print(f"Permission error: {e}")

    except json.JSONDecodeError as e:
        print(f"JSON error: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()


