import fitz
import json
import os

IMAGE_NUM = 0

MAX_FILE_DOCX_SIZE_BYTES = 20 * 1024 * 1024 # Size of file docx 20 MB 

def extract_basic_text_to_json(file_path_input, file_path_output):

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

    try:
        extracted_data = []
        
     #file_size_check(file_path_input, MAX_FILE_DOCX_SIZE_BYTES)
    
        with fitz.open(file_path_input) as doc:

            add_meta_data(doc, extracted_data)

            for page_num in range(doc.page_count):
                page_elements = []
                parse_page(doc, page_num, page_elements)

                add_page(extracted_data, page_num, page_elements)
             # Write the list of dictionaries to the output JSON file
            with open(file_path_output, 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"Error: An unexpected error occurred during processing: {e}")


# =========================== chacking if the fileexisting ================
def chack_if_file_exists(file_path_input):

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
def combine_block_text(b):
    block_string = ""
    if b['type'] == 0:  # Check if text block
        for line in b["lines"]:
            for span in line["spans"]:
                block_string += span["text"]
    return block_string.strip()
# ===============================================================================
def is_terminal_punctuation(text):
    # We strip whitespace first to ignore trailing spaces or line breaks
    return text.endswith('.') or text.endswith('?') or text.endswith('!') or text.endswith(':')
# ===============================================================================
def parse_page(doc, page_num, page_elements):
   
    page = doc.load_page(page_num)

    body_size = get_page_body_size(page) 
    blocks = page.get_text("dict")["blocks"]

    current_paragraph_text = ""
    current_element_type = "paragraph"
    blocks.sort(key=lambda b: b['bbox'][1])# costing alt of time raning
    
    for b in blocks:
       
        
        if b['type'] == 0:
            block_text = combine_block_text(b)
            first_span_size = round(b["lines"][0]["spans"][0]["size"], 1)
            
            # Simple header logic: if size is significantly larger than body text
            is_new_header = (first_span_size > body_size + 1.5)
            
            if is_new_header:
                block_type = "heading" 
            else:
                block_type = "paragraph"
            
            
            # If the type is changing OR the previous element ended, save the accumulated text.
            is_terminal = is_terminal_punctuation(current_paragraph_text)
            
            if is_terminal or block_type != current_element_type:
                # Save the previously accumulated paragraph if it exists
                if current_paragraph_text:
                    page_elements.append({
                        "type": current_element_type,
                        "text": current_paragraph_text
                    })
                
                # Start the new element/paragraph
                current_paragraph_text = block_text
                current_element_type = block_type
                
            else:
                # Continue the current paragraph (join with a new line)
                current_paragraph_text += "\n" + block_text
        elif  b['type'] == 1:
            if current_paragraph_text:
                page_elements.append({
                    "type": current_element_type,
                    "text": current_paragraph_text
                })      

                current_paragraph_text = ""
                     
            
            image_info = extrect_image(b)
            if image_info:
                page_elements.append(image_info)


          
    if current_paragraph_text:
        page_elements.append({
            "type": current_element_type,
            "text": current_paragraph_text
        })

# ===============================================================================
def get_page_body_size(page):
   
    font_counts = {}
    blocks = page.get_text("dict")["blocks"]

    for b in blocks:
        if b['type'] == 0:  # Check if text block
            for line in b["lines"]:
                for span in line["spans"]:
                    size = round(span["size"], 1)
                    font_counts[size] = font_counts.get(size, 0) + 1
    
    # Return the size with the highest count (the mode), or default to 12
    if font_counts:
        return max(font_counts, key=font_counts.get)
    return 12.0

# ===============================================================================
def extrect_image(b):
    try: 
      global IMAGE_NUM
      IMAGE_NUM += 1      
      image_data = b['image']
      extension = b['ext']
      file_name = f"data/outputs/images/{IMAGE_NUM}.{extension}"

      with open(file_name, "wb") as f:
        f.write(image_data)

    except Exception as e:
        print(f"Error extractiong image: {e}")
        return None
    
    return{
        "type": "images",
        "image_name" : f"{IMAGE_NUM}.{extension}",
        "with" : b['width'],
        "height": b['height']
    }
