import os
import json

from src.parsers.docx_handler import extract_docx_file_to_json
from src.parsers.pdf_handler import extract_pdf_file_to_json


from src.openai.functions import send_json_to_openai


def main():


    try:

    # File PDF
        # input_pdf_path = "./data/inputs/סלבוס ארגון אתר ובחירת ציוד בניה .pdf"
        # output_json_path = "data/outputs/pdf.json"

        # extract_pdf_file_to_json(input_pdf_path, output_json_path)


        # File DOCX
        file_path_input = "data/inputs/איפוקסי.docx"
        file_path_output = "data/outputs/docx.json"

        extract_docx_file_to_json(file_path_input, file_path_output)



    # Send to OpenAi
        file_path = "data/outputs/docx.json"

        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)

        result = send_json_to_openai(json_data)
        print(result)







    except FileNotFoundError as e:
        print(f"File error: {e}")
        raise

    except PermissionError as e:
        print(f"Permission error: {e}")
        raise

    except json.JSONDecodeError as e:
        print(f"JSON error: {e}")
        raise

    except Exception as e:
        print(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()


