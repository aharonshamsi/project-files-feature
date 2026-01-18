import io
from pathlib import Path
from src.utils.logger import logger
from src.parameters.config_model import AppConfig


from src.parsers.docx_handler import extract_docx_file_to_model
from src.parsers.pdf_handler import extract_pdf_file_to_model
from src.parsers.pptx_handler import extract_pptx_file_to_model
from src.parsers.utils import get_file_extension_type


#==============================================
def handle_input_file(parameters: AppConfig) -> dict:

    input_file_path = parameters.input_file

    # Get input file name extension (DOCX || PDF)
    file_type = get_file_extension_type(input_file_path)

    with open(input_file_path, "rb") as f: 
        file_stream = io.BytesIO(f.read()) 
    
    logger.info(f"Extracting content from file: {input_file_path}")

    output_file_path = "data/outputs/output.json"

    # path of dir extract images
    IMAGE_OUTPUT_DIR = Path("data/outputs/s3_images") 
    IMAGE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


    if file_type == "docx":
        number_words_in_file, output_document_model = extract_docx_file_to_model(file_stream, IMAGE_OUTPUT_DIR)

    elif file_type == "pdf":
        number_words_in_file, output_document_model = extract_pdf_file_to_model(file_stream, IMAGE_OUTPUT_DIR)

    elif file_type == "pptx":
        number_words_in_file, output_document_model = extract_pptx_file_to_model(file_stream, IMAGE_OUTPUT_DIR)

    parameters.number_words_in_file = number_words_in_file

    #Write the list of dictionaries to the output JSON file
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(output_document_model.model_dump_json(indent=4, exclude_none=True))

    return output_document_model.model_dump(exclude_none=True)



