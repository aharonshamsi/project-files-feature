
from src.parsers.docx_handler import extract_docx_file
from src.parsers.pdf_handler import extract_basic_text_to_json


def main():
    
    #file_path_input = "data/inputs/lesson_1.docx"

   
    input_pdf_path = "./data/inputs/exported-document.pdf"
    output_json_path = "./data/outputs/pdf_text.json"

    extract_basic_text_to_json(input_pdf_path, output_json_path)


    file_path_input = "data/inputs/5 Things to Do Every Day to Be Happy.docx"

    file_path_output = "data/outputs/docx.json"


    parsed_data = extract_docx_file(file_path_input, file_path_output)


if __name__ == "__main__":
    main()


