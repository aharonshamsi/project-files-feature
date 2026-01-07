import json
import os
import re
from pptx import Presentation
from pptx.enum.shapes import PP_PLACEHOLDER

# Constants for better readability
HEADING_TYPE = "heading"
PARAGRAPH_TYPE = "paragraph"
TABLE_TYPE = "table"  # <--- הוספתי את זה
URL_TYPE = "url"

# =========================================================================
def extract_pptx_metadata(prs):
    """
    Extracts core properties from the pptx file.
    """
    props = prs.core_properties
    return {
        "title": props.title or "",
        "author": props.author or "",
        "subject": props.subject or "",
        "creation_date": str(props.created) if props.created else None,
    }

# =========================================================================
def extract_urls(text):
    """
    Finds all URLs within a text string.
    """
    return re.findall(r'https?://[^\s)]+', text)

# =========================================================================
def is_strictly_a_heading(shape, paragraph):
    """
    Advanced logic to distinguish between a real title and a bold bullet point.
    """
    # 1. Check if the shape is defined as a Title placeholder in the slide layout
    if shape.is_placeholder:
        if shape.placeholder_format.type in [PP_PLACEHOLDER.TITLE, PP_PLACEHOLDER.CENTER_TITLE]:
            return True
        # If it's a body placeholder, it's usually a list, even if bolded.
        if shape.placeholder_format.type == PP_PLACEHOLDER.BODY:
            return False

    # 2. Fallback for manual textboxes: Use font size.
    # Most slide titles are > 32pt. Bullet points are usually < 24pt.
    if paragraph.runs:
        font_size = paragraph.runs[0].font.size
        if font_size and font_size.pt > 30:
            return True
            
    return False

# =========================================================================
def extract_pptx_to_json(input_file, output_file):
    """
    Main logic to convert PPTX to a structured JSON format.
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    try:
        prs = Presentation(input_file)
        slide_height = prs.slide_height
        
        result = {
            "metadata": extract_pptx_metadata(prs),
            "pages": []
        }

        for i, slide in enumerate(prs.slides):
            page_elements = []
            # Sort shapes by vertical position (top-to-bottom)
            shapes = sorted(slide.shapes, key=lambda s: (s.top, s.left))

            for shape in shapes:
                
                # --- START: TABLE HANDLING LOGIC ---
                if shape.has_table:
                    table_data = {
                        "type": TABLE_TYPE,
                        "headers": [],
                        "rows": []
                    }
                    tbl = shape.table
                    
                    # Extract all rows text
                    all_rows_text = []
                    for row in tbl.rows:
                        # List comprehension to get text from each cell in the row
                        row_cells = [cell.text_frame.text.strip() for cell in row.cells]
                        all_rows_text.append(row_cells)

                    # Logic: First row is headers, rest are data
                    if all_rows_text:
                        table_data["headers"] = all_rows_text[0]
                        table_data["rows"] = all_rows_text[1:]
                        page_elements.append(table_data)
                    
                    # Skip to next shape (don't process as text frame)
                    continue
                # --- END: TABLE HANDLING LOGIC ---


                # Validate if the shape contains text and isn't a tiny footer number
                if not shape.has_text_frame: 
                    continue

                for paragraph in shape.text_frame.paragraphs:
                    raw_text = paragraph.text.strip()
                    if not raw_text:
                        continue

                    # Handle URLs
                    urls = extract_urls(raw_text)
                    clean_text = raw_text
                    for url in urls:
                        clean_text = clean_text.replace(url, "").strip()

                    # Determine type using the smart logic
                    element_type = HEADING_TYPE if is_strictly_a_heading(shape, paragraph) else PARAGRAPH_TYPE

                    # Append text element
                    if clean_text:
                        # Optimization: If the previous element was a paragraph and this is too, merge them
                        if (page_elements and 
                            page_elements[-1]["type"] == PARAGRAPH_TYPE and 
                            element_type == PARAGRAPH_TYPE):
                            page_elements[-1]["text"] += "\n" + clean_text
                        else:
                            page_elements.append({
                                "type": element_type,
                                "text": clean_text
                            })

                    # Append URL elements separately
                    for url in urls:
                        page_elements.append({
                            "type": URL_TYPE,
                            "text": url
                        })

            result["pages"].append({
                "page_number": i + 1,
                "content": page_elements
            })

        # Save the result to a JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

        return result

    except Exception as e:
        print(f"Error processing PPTX: {e}")
        raise