from src.parsers.docx_handler import extract_docx_file_to_json
from src.parsers.pdf_handler import extract_pdf_file_to_json


def main():

   # File PDF
    input_pdf_path = "./data/inputs/5 Things to Do Every Day to Be Happy.pdf"
    output_json_path = "data/outputs/pdf.json"

    extract_pdf_file_to_json(input_pdf_path, output_json_path)


    # File DOCX
    file_path_input = "data/inputs/5 Things to Do Every Day to Be Happy.docx"
    file_path_output = "data/outputs/docx.json"

    extract_docx_file_to_json(file_path_input, file_path_output)


if __name__ == "__main__":
    main()


