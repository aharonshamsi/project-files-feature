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
# def combine_block_text(b):
#     block_string = ""
#     if b['type'] == 0:  # Check if text block
#         for line in b["lines"]:
#             for span in line["spans"]:
#                 block_string += span["text"]
#     return block_string.strip()




# ===============================================================================
# def parse_page(doc, page_num, page_elements):
   
#     page = doc.load_page(page_num)
#     body_size = get_page_body_size(page) 
#     blocks = page.get_text("dict")["blocks"]

#     current_paragraph_text = ""
#     current_element_type = "paragraph"
    
#     blocks.sort(key=lambda b: b['bbox'][1])# costing alt of time raning

    
#     for b in blocks:
#         block_text = combine_block_text(b)
        
#         if not block_text:
#             continue

       
#         if b['type'] == 0: # Block of text
#             span = b["lines"][0]["spans"][0]

#             first_span_size = round(span["size"], 1)
#             first_span_flags = span["flags"]
#             font_name = span["font"].lower() 

#             # Bold detection
#             is_bold_flag = bool(first_span_flags & 2) # Title flags is 2 
#             is_bold_font = "bold" in font_name  # # Name of font is bold

#             is_bold = is_bold_flag or is_bold_font

#             # Decide if heading
#             is_new_header = (
#                 first_span_size > body_size + PIXELS_LARGER_THAT_AVERAGE
#                 or is_bold
#             )

#             if is_new_header:
#                 block_type = "heading"
#             else:
#                 block_type = "paragraph"

#             if block_type != current_element_type: 

#                 # Save the previously accumulated paragraph if it exists
#                 if current_paragraph_text:
#                     page_elements.append({
#                         "type": current_element_type,
#                         "text": current_paragraph_text
#                     })
                
#                 # Start the new element/paragraph
#                 current_paragraph_text = block_text
#                 current_element_type = block_type
                
#             else:
#                 # Continue the current paragraph (join with a new line)
#                 current_paragraph_text += "\n" + block_text

#     if current_paragraph_text:
#         page_elements.append({
#             "type": current_element_type,
#             "text": current_paragraph_text
#         })


# ===============================================================================
# Helper to extract text from a single line
def get_line_text(line):
    line_text = ""
    for span in line["spans"]:
        line_text += span["text"]
    return line_text.strip()

# =========================================================================

# def parse_page(doc, page_num, page_elements):
    
#     page = doc.load_page(page_num)
#     body_size = get_page_body_size(page) 
    
#     # Get blocks as dictionary
#     blocks = page.get_text("dict")["blocks"]

#     current_text_buffer = ""
#     current_element_type = None # Start with no type defined
    
#     # Sort blocks vertically to ensure reading order
#     blocks.sort(key=lambda b: b['bbox'][1])

#     for b in blocks:
#         if b['type'] != 0: # Skip images or non-text blocks
#             continue

#         # === CHANGE: Iterate through LINES instead of treating the whole block as one unit ===
#         for line in b["lines"]:
            
#             text_line = get_line_text(line)
#             if not text_line:
#                 continue

#             # Analyze the first span of the line to decide formatting
#             # (Assuming the whole line shares the style of the first span)
#             first_span = line["spans"][0]
#             span_size = round(first_span["size"], 1)
#             span_flags = first_span["flags"]
#             font_name = first_span["font"].lower()

#             # Logic to detect Heading vs Paragraph
#             is_bold_flag = bool(span_flags & 2) 
#             is_bold_font = "bold" in font_name
#             is_bold = is_bold_flag or is_bold_font

#             is_new_header = (
#                 span_size > body_size + PIXELS_LARGER_THAT_AVERAGE
#                 or is_bold
#             )

#             if is_new_header:
#                 line_type = "heading"
#             else:
#                 line_type = "paragraph"

#             # === Logic to merge lines or split based on type ===
            
#             # If it's the first element ever
#             if current_element_type is None:
#                 current_element_type = line_type
#                 current_text_buffer = text_line

#             # If the type matches the current buffer, append to it
#             elif line_type == current_element_type:
                
#                 current_text_buffer += "\n" + text_line 

#             # If type CHANGED (e.g., from Heading to Paragraph), save and switch
#             else:
#                 page_elements.append({
#                     "type": current_element_type,
#                     "text": current_text_buffer.strip()
#                 })
#                 current_element_type = line_type
#                 current_text_buffer = text_line
        

#     # Don't forget to save the last buffer after loops end
#     if current_text_buffer:
#         page_elements.append({
#             "type": current_element_type,
#             "text": current_text_buffer.strip()
#         })

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




def parse_page(doc, page_num, page_elements):

    page = doc.load_page(page_num)
    blocks = page.get_text("dict")["blocks"]

    # collect all font sizes
    all_sizes = []
    for b in blocks:
        if b["type"] == 0:
            for line in b["lines"]:
                for span in line["spans"]:
                    all_sizes.append(span["size"])

    avg_size = sum(all_sizes) / len(all_sizes) if all_sizes else 12

    blocks.sort(key=lambda b: b["bbox"][1])

    current_text = ""
    current_type = None
    last_y = None

    for b in blocks:
        if b["type"] != 0:
            continue

        for line in b["lines"]:

            text_line = "".join(s["text"] for s in line["spans"]).strip()
            if not text_line:
                continue

            first = line["spans"][0]
            size = first["size"]
            bold = (first["flags"] & 2) != 0 or "bold" in first["font"].lower()
            num_words = len(text_line.split())
            y0 = line["bbox"][1]

            # gap detection
            is_big_gap = False
            if last_y is not None:
                gap = y0 - last_y
                if gap > size * 2:   # <-- MUCH LESS SPLITTING
                    is_big_gap = True

            last_y = y0

            # detect heading
            is_heading = (
                size > avg_size * 1.25 or
                bold or
                num_words <= 6
            )
            line_type = "heading" if is_heading else "paragraph"

            # ---------------------- MERGING LOGIC ----------------------

            # first element ever
            if current_type is None:
                current_type = line_type
                current_text = text_line
                continue

            # SAME TYPE → MERGE ALWAYS
            if line_type == current_type:
                current_text += "\n" + text_line
                continue

            # TYPE CHANGED:
            # ----------------------
            # heading → paragraph   OR paragraph → heading
            # ----------------------
            # save current
            page_elements.append({
                "type": current_type,
                "text": current_text.strip()
            })

            # start new block
            current_type = line_type
            current_text = text_line

    # last block
    if current_text:
        page_elements.append({
            "type": current_type,
            "text": current_text.strip()
        })