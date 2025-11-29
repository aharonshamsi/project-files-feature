import fitz  
import json
import os

def extract_basic_text_to_json(file_path_input, file_path_output):
    """
    PHASE 1: Extracts raw text from each page of a PDF and saves it as a JSON file.
    
    Args:
        file_path_input (str): The full path to the input PDF file.
        file_path_output (str): The full path where the output JSON file will be saved.
    """
    
    # Check 1: Verify the PDF file exists before processing
    if not os.path.exists(file_path_input):
        print(f"Error: Input file not found at: {file_path_input}")
        # Print current working directory to help debug
        print(f"   Current working directory: {os.getcwd()}")
        return

    extracted_data = []

    try:
        
        with fitz.open(file_path_input) as doc:
           
            
            # Loop through all pages in the document
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                
                # Extract raw text from the page
                raw_text = page.get_text("text")
                
                # Create a dictionary structure for the current page
                page_data = {
                    "page_number": page_num + 1,
                    "text": raw_text
                }
                
                extracted_data.append(page_data)

            # Write the list of dictionaries to the output JSON file
            with open(file_path_output, 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, ensure_ascii=False, indent=2)
            
        
    except Exception as e:
        print(f"Error: An unexpected error occurred during processing: {e}")

