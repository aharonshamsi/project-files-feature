import fitz
import json
import os
from src.parsers.utils import file_size_check
import io

PIXELS_LARGER_THAT_AVERAGE = 1.5


PIXELS_LARGER_THAT_AVERAGE = 1.5 # Size of average pixels of the file
TEXT_BLOCK_TYPE = 0 
DEFAULT_FONT_SIZE = 12.0

MINI_WORDS = 40 # Minimal words in content

# ================  extract text (PARAGRAPH AND HEADING) ================================
def extract_pdf_file_to_json(file_stream: io.BytesIO) -> tuple[int, dict]: # DocumentModel פה נותר לעבוד שיחזיר במקום מילון יחזיר מודל 

    total_word_count = 0

    extracted_data = {
    "metadata": None,
    "pages": []
    }


    try:

        file_size_check(file_stream)

        file_stream.seek(0)
        pdf_bytes = file_stream.read()


        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:

            add_meta_data(doc, extracted_data)

            for page_num in range(doc.page_count):
                page_elements = []
                page_word_count = parse_page(doc, page_num, page_elements)
                total_word_count += page_word_count

                add_page(extracted_data, page_num, page_elements)

            # Check number of words
            if total_word_count < MINI_WORDS:
                raise ValueError(
            f"Content too short: {total_word_count} words. Minimum required: {MINI_WORDS}"
            )

            return total_word_count, extracted_data


    except ValueError as ve:
        print(f"Validation error: {ve}")
        raise

    except Exception as e:
        print(f"Unexpected error while processing PDF: {e}")
        raise





# =============== adding the file meta data to the output file =============
def add_meta_data(doc, extracted_data):
    extracted_data["metadata"] = doc.metadata


# ====================== Adding page to the json output ====================
def add_page(extracted_data, page_num, page_elements):
    extracted_data["pages"].append({
        "page_number": page_num + 1,
        "content": page_elements
    })



# =========================================================================
def combine_block_text(b):
    block_string = ""
    if b['type'] == 0:  # Check if text block
        for line in b["lines"]:
            for span in line["spans"]:
                block_string += span["text"]
    return block_string.strip()




# =========================================================================
def parse_page(doc, page_num, page_elements):
   
    page = doc.load_page(page_num)
    body_size = get_page_body_size(page) 
    blocks = page.get_text("dict")["blocks"]

    current_paragraph_text = ""
    current_element_type = "paragraph"
    blocks.sort(key=lambda b: b['bbox'][1]) # Sort the blocks
    
    word_count = 0

    for b in blocks:
        block_text = combine_block_text(b)

        if not block_text:
            continue

        if b['type'] == TEXT_BLOCK_TYPE: # Block of text
            
            # Check the entire paragraph is bold.
            is_bold = is_block_fully_bold(b) 
            
            span = b["lines"][0]["spans"][0]
            first_span_size = round(span["size"], 1)

            # Decide if heading
            is_new_header_candidate = (
                first_span_size > body_size + PIXELS_LARGER_THAT_AVERAGE
                or is_bold
            )
            
            # Heading
            if is_new_header_candidate: 
                block_type = "heading"
            
            # Paragraph
            else:
                block_type = "paragraph"

            if block_type != current_element_type: 

                # Save the previously accumulated paragraph if it exists
                if current_paragraph_text:
                    page_elements.append({
                        "type": current_element_type,
                        "text": current_paragraph_text
                    })
                    word_count += len(current_paragraph_text.split()) # Count number of words in this block

                
                # Start the new element/paragraph
                current_paragraph_text = block_text
                current_element_type = block_type
                
            else:
                # Continue the current paragraph (join with a new line)
                current_paragraph_text += "\n" + block_text

    # Last block
    if current_paragraph_text:
        page_elements.append({
            "type": current_element_type,
            "text": current_paragraph_text
        })
        word_count += len(current_paragraph_text.split()) 
    
    return word_count



# =====================================================================
def get_page_body_size(page):
   
    font_counts = {}
    blocks = page.get_text("dict")["blocks"]

    for b in blocks:
        if b['type'] == TEXT_BLOCK_TYPE:  # Check if text block
            for line in b["lines"]:
                for span in line["spans"]:
                    size = round(span["size"], 1)
                    font_counts[size] = font_counts.get(size, 0) + 1
    
    # Return the size with the highest count (the mode), or default to 12
    if font_counts:
        return max(font_counts, key=font_counts.get)
    
    return DEFAULT_FONT_SIZE




# ===============================================================
def is_block_fully_bold(block):

    if block['type'] != TEXT_BLOCK_TYPE:
        return False
        
    # Check the entire paragraph is bold.
    for line in block["lines"]:
        for span in line["spans"]:

            is_bold_flag = bool(span["flags"] & 2)
            is_bold_font = "bold" in span["font"].lower()
            
            if not (is_bold_flag or is_bold_font):
                return False
    
    return True