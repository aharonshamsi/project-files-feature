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
    if chack_if_file_exists(file_path_input) == False:
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


# ================  extract text (PARAGRAPH AND HEADING) ================================
def extract_paragraph_and_heading_to_json(file_path_input, file_path_output):

    if chack_if_file_exists(file_path_input) == False:
        return

    extracted_data = []

    try:

        with fitz.open(file_path_input) as doc:

            add_meta_data(doc, extracted_data)

            for page_num in range(doc.page_count):
                page_elements = []
                parse_page(doc, page_num, page_elements)

                add_page(extracted_data, page_num, page_elements)
             # Write the list of dictionaries to the output JSON file
            with open(file_path_output, 'a', encoding='utf-8') as f:
                json.dump(extracted_data, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"Error: An unexpected error occurred during processing: {e}")


# =========================== chacking if the fileexisting ================
def chack_if_file_exists(file_path_input):
 # Check 1: Verify the PDF file exists before processing
    if not os.path.exists(file_path_input):
        print(f"Error: Input file not found at: {file_path_input}")
        # Print current working directory to help debug
        print(f"   Current working directory: {os.getcwd()}")
        return False

    return True

# =============== adding the file meta data to the output file =============
def add_meta_data(doc, extracted_data):

    fileMetadata = doc.metadata
    page_data = {
        "type": " file_meta_data",
        "text": fileMetadata
    }

    extracted_data.append(page_data)
# ====================== Adding page to the json output =========================
def add_page(extracted_data, page_num, page_elements):
    page_object = {
        "page_number": page_num + 1,
        "content": page_elements
    }
    extracted_data.append(page_object)

# ===============================================================================
def parse_page(doc, page_num, page_elements):
    page = doc.load_page(page_num)

    raw_text = page.get_text("text")

    text_data = {
        "type": "paragraph",
        "text": raw_text
    }
    page_elements.append(text_data)


