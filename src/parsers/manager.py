
from src.parsers.docx_handler import extract_docx_file_to_json
from src.parsers.pdf_handler import extract_pdf_file_to_json
from src.parsers.utils import get_file_extension_type
from src.utils.logger import logger
from src.parameters.config_model import AppConfig
import io
import json

#==================================
def handle_input_file(input_path: str) -> dict:

    # Get input file name extension (DOCX || PDF)
    file_type = get_file_extension_type(input_path)

    with open(input_path, "rb") as f: 
        file_stream = io.BytesIO(f.read()) # זרם ביטים
    
    logger.info(f"Extracting content from file: {input_path}")

    output_file_path = "data/outputs/output.json"

    if file_type == "docx":
        number_words_in_file, output_dict = extract_docx_file_to_json(file_stream)

    elif file_type == "pdf":
        number_words_in_file, output_dict = extract_pdf_file_to_json(file_stream)

    # Write the list of dictionaries to the output JSON file
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(output_dict.model_dump_json(indent=4, exclude_none=True))

    return output_dict.model_dump()

        # # Write the list of dictionaries to the output JSON file
        # with open(output_file_path, "w", encoding="utf-8") as f:
        #     json.dump(output_dict, f, indent=4, ensure_ascii=False)


