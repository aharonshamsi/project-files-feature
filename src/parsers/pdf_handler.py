import fitz
import json
import os


PIXELS_LARGER_THAT_AVERAGE = 1.5


# ================  extract text (PARAGRAPH AND HEADING) ================================
def extract_paragraph_and_heading_to_json(file_path_input, file_path_output):

    extracted_data = []

    try:

        with fitz.open(file_path_input) as doc:

            add_meta_data(doc, extracted_data)

            for page_num in range(doc.page_count):
                page_elements = []
                parse_page(doc, page_num, page_elements)

                add_page(extracted_data, page_num, page_elements)

             # Write the list of dictionaries to the output JSON file
            with open(file_path_output, 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, ensure_ascii=False, indent=2)


    except FileNotFoundError:
        print(f"Error: Input file not found at: {file_path_input}")
        print(f"Current working directory: {os.getcwd()}")
        return

    except Exception as e:
        print(f"Unexpected error while reading PDF: {e}")
        return
    
    except Exception as e:
        print(f"Error: An unexpected error occurred during processing: {e}")





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
def parse_page(doc, page_num, page_elements):
   
    page = doc.load_page(page_num)
    body_size = get_page_body_size(page) 
    blocks = page.get_text("dict")["blocks"]

    current_paragraph_text = ""
    current_element_type = "paragraph"
    
    blocks.sort(key=lambda b: b['bbox'][1])# costing alt of time raning

    
    for b in blocks:
        block_text = combine_block_text(b)
        
        if not block_text:
            continue

       
        if b['type'] == 0: # Block of text
            span = b["lines"][0]["spans"][0]

            first_span_size = round(span["size"], 1)
            first_span_flags = span["flags"]
            font_name = span["font"].lower() 

            # Bold detection
            is_bold_flag = bool(first_span_flags & 2) # Title flags is 2 
            is_bold_font = "bold" in font_name  # # Name of font is bold

            is_bold = is_bold_flag or is_bold_font

            # Decide if heading
            is_new_header = (
                first_span_size > body_size + PIXELS_LARGER_THAT_AVERAGE
                or is_bold
            )

            if is_new_header:
                block_type = "heading"
            else:
                block_type = "paragraph"

            if block_type != current_element_type: 

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

