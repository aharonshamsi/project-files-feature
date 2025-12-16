import os
import json

# 
def file_size_check(file_path_input, max_file_size_bytes):
    file_size = os.path.getsize(file_path_input)

    if file_size > max_file_size_bytes:
        raise ValueError(f"The file size exceeds the maximum allowed size of {max_file_size_bytes} bytes")
    



def read_file_json(file_path):

    try:
        with open(file_path, "r", encoding='utf-8') as file:
            return json.load(file)
            
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        raise 
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise