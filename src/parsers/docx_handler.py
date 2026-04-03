from docx import Document
from docx.text.paragraph import Paragraph
from docx.table import Table
import re
import io
import os

from src.models.document_models import Metadata, ContentBlock, DocumentModel, TableData, ImageData
from src.parsers.utils import file_size_check, is_solid_color_image
import hashlib

# =========================================================
# Heading style keywords used for identifying heading paragraphs.
HEADING = "heading"
PARAGRAPH = "paragraph"
URL = "url"
IMAGE = "image"
TABLE = "table"
TITLE = "title"
HEBREW_HEADING = "כותרת"

MINI_WORDS = 40 
MIN_IMAGE_SIZE_BYTES = 2*1024 # Minimum image size threshold (2KB)
# =========================================================
def extract_document_metadata(file_object) -> Metadata:

    properties = file_object.core_properties

    metadata = {
        "title": properties.title, 
        "author": properties.author,
        "creation_date": properties.created.isoformat() if properties.created else None
    }
    return Metadata(**metadata)



# =========================================================
# data table and also count words
def extract_table(table, count_words):
    
    extracted = []

    for row in table.rows:
        extracted_row = []
        for cell in row.cells:
            text = cell.text.strip()
            extracted_row.append(text)
            count_words += len(text.split())
        extracted.append(extracted_row)

    if extracted:
        return {"headers": extracted[0], "rows": extracted[1:]}, count_words 
    else:
        return {"headers": [], "rows": []}, count_words


# =========================================================
def iteration_block_items(parent):

    for child in parent.element.body:
        if child.tag.endswith("p"):
            yield Paragraph(child, parent)

        elif child.tag.endswith("tbl"):
            yield Table(child, parent)


# =========================================================
def extract_urls_from_text(text):
    pattern = r'https?://[^\s)]+'
    return re.findall(pattern, text)




#==================================================================
def extract_docx_file_to_model(file_stream: io.BytesIO, image_output_dir: str) -> tuple[int, DocumentModel]:
    
    count_words = 0
    block_list = [] 
    block_id_counter = 1

    try:
        file_size_check(file_stream)

        file_stream.seek(0) 
        doc = Document(file_stream)
        
        metadata_dict = extract_document_metadata(doc)

        new_paragraph = False 

        for block in iteration_block_items(doc):

            if isinstance(block, Paragraph):
                text = block.text.strip()
                
                # Images
                saved_images = extract_and_save_image(block, block_id_counter, image_output_dir)
                
                for img_path in saved_images:
                    block_list.append(ContentBlock(
                        block_id=block_id_counter,
                        type=IMAGE,
                        image_data=ImageData(image_path=img_path)
                    ))
                    block_id_counter += 1

                if not text and not saved_images: continue
                if not text: continue


                count_words += len(text.split())

                urls = extract_urls_from_text(text) # If the link is actually part of the text
                
                if urls:
                    for url in urls:
                        text = text.replace(url, "").strip()


                # Heading
                style_lower = block.style.name.lower()
                is_heading_style = (HEADING in style_lower or TITLE in style_lower or HEBREW_HEADING in style_lower)

                if (is_heading_style or all(run.bold for run in block.runs if run.text.strip())) and not urls:
                    is_break = is_real_section_break(block)

                    
                    if (block_list and block_list[-1].type == HEADING and not is_break):
                        block_list[-1].text += "\n" + text
                    else:
                        block_list.append(ContentBlock(
                            block_id=block_id_counter,
                            type=HEADING,
                            text=text
                        ))
                        block_id_counter += 1
                    new_paragraph = True


                else:
                    # Paragraph chaining logic
                    if not new_paragraph and block_list and block_list[-1].type == PARAGRAPH:
                        block_list[-1].text += "\n" + text
                    else:
                        block_list.append(ContentBlock(
                            block_id=block_id_counter,
                            type=PARAGRAPH,
                            text=text
                        ))
                        block_id_counter += 1
                    new_paragraph = False

                #  urls
                if urls:
                    for url in urls:
                        block_list.append(ContentBlock(
                            block_id=block_id_counter,
                            type=URL,
                            text=url
                        ))
                        block_id_counter += 1

            # Table
            elif isinstance(block, Table):
                table_obj, count_words = extract_table(block, count_words)
                block_list.append(ContentBlock(
                    block_id=block_id_counter,
                    type=TABLE,
                    table_data=TableData(**table_obj)
                ))
                block_id_counter += 1

       
        if count_words < MINI_WORDS:
            raise ValueError(f"Content too short: {count_words} words.")

        final_document = DocumentModel(
            metadata=metadata_dict,
            content_blocks=block_list
        )
        
        return count_words, final_document

    except Exception as e:
        print(f"Error: {e}")
        raise




#=============================================================
def is_real_section_break(block):

    # 1. Check paragraph formatting (Instance)
    if block.paragraph_format.page_break_before:
        return True

    # 2. Check the style formatting (if style exists)
    if block.style and block.style.paragraph_format.page_break_before:
        return True

    # 3. Hard XML-based checks (section/hard breaks)
    xml_str = block._element.xml
    if 'w:sectPr' in xml_str or 'w:br' in xml_str:
        return True
    
    if 'lastRenderedPageBreak' in xml_str:
        return True

    return False



#=============================================================
def extract_and_save_image(paragraph, block_id,  image_output_dir: str):
    image_paths = []

    # Get rId of image
    blips = paragraph._element.xpath('.//*[local-name()="blip"]')
    
    for i, blip in enumerate(blips):

        embed_attr = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed'
        rId = blip.get(embed_attr)
        
        if rId:
            try:
                # Access binary image
                image_part = paragraph.part.related_parts[rId]
                image_bytes = image_part.blob
                
                # Skip saving if the image is smaller than the threshold
                if len(image_bytes) < MIN_IMAGE_SIZE_BYTES:
                    continue   
                
                if is_solid_color_image(image_bytes):
                    #logger.info(f"Skipping solid color image found in block {block_id}")
                    print(f"Skipping solid color image found in block {block_id}")
                    continue               
                          
               # Build file path
                extension = image_part.content_type.split('/')[-1].replace('x-', '')
                
                # Generate unique hash from the image bytes
                image_hash = hashlib.sha256(image_bytes).hexdigest()
                image_filename = f"{image_hash}.{extension}"
                full_path = os.path.join(image_output_dir, image_filename)
                
                # Check if the image already exists on disk before saving
                if not os.path.exists(full_path):
                    with open(full_path, "wb") as f:
                        f.write(image_bytes)
                
                # Append the path to the list for JSON output or further use
                image_paths.append(full_path)
            except Exception as e:
                raise RuntimeError(f"Image extraction failed for block {block_id}, image {i+1}: {e}") from e

                
    return image_paths