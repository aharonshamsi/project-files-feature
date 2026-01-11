from docx import Document
from docx.text.paragraph import Paragraph
from docx.table import Table
import json
import re
import io

from typing import Dict, Any
from src.models.document_models import Metadata, ContentBlock, DocumentModel


from src.parsers.utils import file_size_check


# Heading style keywords used for identifying heading paragraphs.
HEADING = "heading"
TITLE = "title"
HEBREW_HEADING = "כותרת"

MINI_WORDS = 40 


def extract_document_metadata(file_object) -> Metadata:

    properties = file_object.core_properties

    metadata = {
        "title": properties.title, 
        "author": properties.author,
        "creation_date": properties.created.isoformat() if properties.created else None
    }
    return Metadata(**metadata)




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
        return {"columns": extracted[0], "rows": extracted[1:]}, count_words # Return also count words
    else:
        return {"columns": [], "rows": [], "word_count": 0}, count_words # Return also count words





def iteration_block_items(parent):

    for child in parent.element.body:
        if child.tag.endswith("p"):
            yield Paragraph(child, parent)

        elif child.tag.endswith("tbl"):
            yield Table(child, parent)




def paragraph_contains_image(paragraph):
    images = []

    for run in paragraph.runs:
        drawing_elements = run._r.findall('.//w:drawing', paragraph._element.nsmap)
        
        if drawing_elements:
            images.append(run)
    
    return images




def extract_urls_from_text(text):
    pattern = r'https?://[^\s)]+'
    return re.findall(pattern, text)




#==================================================================
def extract_docx_file_to_json(file_stream: io.BytesIO) -> tuple[int, DocumentModel]:
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
                if not text: continue
                
                count_words += len(text.split()) 
                urls = extract_urls_from_text(text)
                
                if urls:
                    for url in urls:
                        text = text.replace(url, "").strip()

                style_lower = block.style.name.lower()
                is_heading_style = (HEADING in style_lower or TITLE in style_lower or HEBREW_HEADING in style_lower)

                if (is_heading_style or all(run.bold for run in block.runs if run.text.strip())) and not urls:
                    is_break = is_real_section_break(block)

                    
                    if (block_list and block_list[-1].type == "heading" and not is_break):
                        block_list[-1].text += "\n" + text
                    else:
                        block_list.append(ContentBlock(
                            block_id=block_id_counter,
                            type="heading",
                            text=text
                        ))
                        block_id_counter += 1
                    new_paragraph = True

                else:
                    # Paragraph chaining logic
                    if not new_paragraph and block_list and block_list[-1].type == "paragraph":
                        block_list[-1].text += "\n" + text
                    else:
                        block_list.append(ContentBlock(
                            block_id=block_id_counter,
                            type="paragraph",
                            text=text
                        ))
                        block_id_counter += 1
                    new_paragraph = False

                #  urls
                if urls:
                    for url in urls:
                        block_list.append(ContentBlock(
                            block_id=block_id_counter,
                            type="url",
                            text=url
                        ))
                        block_id_counter += 1

            # Table
            elif isinstance(block, Table):
                table_obj, count_words = extract_table(block, count_words)
                block_list.append(ContentBlock(
                    block_id=block_id_counter,
                    type="table",
                    text="Table Data", 
                    table_data=table_obj
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

    # 1. בדיקת הפיסקה עצמה (Instance)
    if block.paragraph_format.page_break_before:
        return True

    if block.style and block.style.paragraph_format.page_break_before:
        return True

    # 3. בדיקות XML קשיחות (Section Break / Hard Break)
    xml_str = block._element.xml
    if 'w:sectPr' in xml_str or 'w:br' in xml_str:
        return True
    
    if 'lastRenderedPageBreak' in xml_str:
        return True

    return False