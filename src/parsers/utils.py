import os


def file_size_check(file_path_input, max_file_size_bytes):
    file_size = os.path.getsize(file_path_input)

    if file_size > max_file_size_bytes:
        raise ValueError(f"Input DOCX exceeds max allowed size of {max_file_size_bytes} bytes")
    
    