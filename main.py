
from src.parsers.docx_handler import extract_docx_file


def main():
    
    #file_path_input = "data/inputs/lesson_1.docx"
    file_path_input = "data/inputs/5 Things to Do Every Day to Be Happy.docx"

    file_path_output = "data/outputs/docx.json"


    parsed_data = extract_docx_file(file_path_input, file_path_output)


if __name__ == "__main__":
    main()


