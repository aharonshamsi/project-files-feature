import os
import json
from pathlib import Path


MAX_FILE_DOCX_SIZE_BYTES = 20 * 1024 * 1024 # MAX 20 MB 
MINI_FILE_DOCX_SIZE_BYTES = 10 * 1024  # MINI 10 KB 


# CHECK SIZE OF THE FILE, MAX & MINI
def file_size_check(file_path_input):
    file_size = os.path.getsize(file_path_input)

    if file_size > MAX_FILE_DOCX_SIZE_BYTES:
        raise ValueError(
            f"The file size exceeds the maximum allowed size of {MAX_FILE_DOCX_SIZE_BYTES} bytes"
        )
    
    if file_size < MINI_FILE_DOCX_SIZE_BYTES:
        raise ValueError(
            f"The file size is smaller than the minimum required size of {MINI_FILE_DOCX_SIZE_BYTES} bytes"
        )



# Reads a json file and returns a dictionary
def load_json_to_dict(file_path):

    try:
        with open(file_path, "r", encoding='utf-8') as file:
            return json.load(file)
            
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        raise 
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise




# Check and return suffix type of the file
def get_file_extension_type(file_path):

    extension = Path(file_path.strip()).suffix.lower()


    if extension == ".pdf":
        file_type = "pdf"

    elif extension == ".docx":
        file_type = "docx"
    
    else:
        raise ValueError(f"Unsupported file type: '{extension}'")
    
    return file_type