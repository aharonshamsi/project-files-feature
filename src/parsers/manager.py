
from src.parsers.docx_handler import extract_docx_file_to_json
from src.parsers.pdf_handler import extract_pdf_file_to_json
from src.parsers.utils import get_file_extension_type
#from src.utils.logger import logger
from src.parameters.config_model import AppConfig


#==================================
def handle_input_file(input_path: str, output_path: str, parameters: AppConfig):

    # Get input file name extension (DOCX || PDF)
    file_type = get_file_extension_type(input_path)
    
   # logger.info(f"Extracting content from file: {input_path}")

    if file_type == "docx":
        number_words_in_file = extract_docx_file_to_json(input_path, output_path)
    
    elif file_type == "pdf":
        number_words_in_file = extract_pdf_file_to_json(input_path, output_path)


    # Add parameter of number_words_in_file in dict
    parameters.number_words_in_file = number_words_in_file 
    

