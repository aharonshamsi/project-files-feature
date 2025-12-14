import os
import json

from src.parsers.docx_handler import extract_docx_file_to_json
from src.parsers.pdf_handler import extract_pdf_file_to_json


from src.services.openai_service import send_json_to_openai


def main():

   # File PDF
    input_pdf_path = "./data/inputs/לאסוף את השברים.pdf"
    output_json_path = "data/outputs/pdf.json"

    extract_pdf_file_to_json(input_pdf_path, output_json_path)


    # # File DOCX
    # file_path_input = "data/inputs/regulations_occupational-safety-officials-construction-site.docx"
    # file_path_output = "data/outputs/docx.json"

    # extract_docx_file_to_json(file_path_input, file_path_output)



#======================================
    file_path = "data/outputs/pdf.json"


    with open(file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)


    result = send_json_to_openai(json_data)
    print(result)





if __name__ == "__main__":
    main()


