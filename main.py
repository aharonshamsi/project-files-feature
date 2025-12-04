from src.parsers.docx_handler import extract_docx_file_to_json
from src.parsers.pdf_handler import extract_basic_text_to_json
from src.parsers.pdf_handler import extract_paragraph_and_heading_to_json

def main():

   
     input_pdf_path = "data/inputs/hashmal.pdf"
     output_json_path = "data/outputs/hashmal.json"
     extract_paragraph_and_heading_to_json(input_pdf_path, output_json_path)
    # extract_basic_text_to_json(input_pdf_path, output_json_path)



    #file_path_input = "data/inputs/regulations_occupational-safety-officials-construction-site.docx"
    #file_path_input = "data/inputs/hashmal-doc.docx"
    #file_path_output = "data/outputs/docx.json"

    #parsed_data = extract_docx_file_to_json(file_path_input, file_path_output)


if __name__ == "__main__":
    main()


