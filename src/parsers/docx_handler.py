from docx import Document
from docx.text.paragraph import Paragraph
from docx.table import Table
import json
import re
from docx.oxml.ns import qn
import base64




from src.parsers.utils import file_size_check

MAX_FILE_DOCX_SIZE_BYTES = 20 * 1024 * 1024 # Size of file docx 20 MB 




def extract_document_metadata(file_object):

    properties = file_object.core_properties

    metadata = {
        "title": properties.title, 
        "author": properties.author,
        "subject": properties.subject,
        "keywords": properties.keywords,
        "creation_date": str(properties.created),
    }

    return metadata





def extract_table(table):
    
    extracted = []
    for row in table.rows:
        extracted_row = [cell.text.strip() for cell in row.cells]
        extracted.append(extracted_row)

    if extracted:
        return {"columns": extracted[0], "rows": extracted[1:]}
    else:
        return {"columns": [], "rows": []}





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



def handle_embedded_image(doc ,block):

    for run in block.runs:
        image = []
        ns = run._element.nsmap

        # איתור אלמנטי drawing
        drawings = run._element.findall('.//w:drawing', namespaces=ns)
        if not drawings:
            continue

        # טיפול בכל תמונה בתוך ה-drawing
        for draw in drawings:
            blip = draw.find('.//a:blip', namespaces=ns)
            if blip is None:
                continue

            rId = blip.get(qn('r:embed'))
            image_part = doc.part.related_parts[rId]
            blob = image_part.blob

            image = {
                "type": "image",
                "name": image_part.partname.split("/")[-1]
                #"data_base64": base64.b64encode(blob).decode("utf-8")
            }

            return image







def extract_docx_file_to_json(file_path_input, file_path_output):

    result = {"metadata": [],
              "content": [],
              }

    try:
        file_size_check(file_path_input, MAX_FILE_DOCX_SIZE_BYTES) # Import
        doc = Document(file_path_input)

        metadata = extract_document_metadata(doc)
        result["metadata"].append(metadata)

        new_paragraph = False 


        for block in iteration_block_items(doc):

            # Paragraph
            if isinstance(block, Paragraph):
                text = block.text.strip()
                style = block.style.name

                if not text:
                    continue
                
                # Url
                urls = extract_urls_from_text(text)
                if urls:
                    for url in urls:
                        result["content"].append({
                            "type": "url",
                            "text": url
                        })
                    continue


                # Images of embedded
                object_image = handle_embedded_image(doc, block)
                if object_image:
                    result["content"].append(object_image)

                
                # Heading detection
                if 'Heading' in style or 'title' in style or \
                   all(run.bold for run in block.runs if run.text.strip()):
                    new_paragraph = True
                    

                    result["content"].append({
                        "type": "heading",
                        "text": text
                    })


                else:
                    # New paragraph
                    if new_paragraph or not result["content"] or result["content"][-1]["type"] != "paragraph":
                        result["content"].append({
                            "type": "paragraph",
                            "text": text
                        })

                    else:
                        result["content"][-1]["text"] += "\n\n" + text
                    
                new_paragraph = False

                
                


            # Table
            elif isinstance(block, Table):
                table_data = extract_table(block)
                result["content"].append({
                    "type": "table",
                    "data": table_data
                })


        # Write JSON
        with open(file_path_output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)


    # Error detection
    except FileNotFoundError:
        print("Error: File not found")

    except PermissionError:
        print("Error: Permission denied. Make sure the file is not open")

    except Exception as e:
        print(f"Error: {e}")




