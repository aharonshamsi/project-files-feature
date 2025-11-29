from docx import Document
from docx.text.paragraph import Paragraph
from docx.table import Table
import json
import os

from src.parsers.utils import file_size_check

MAX_FILE_DOCX_SIZE_BYTES = 20 * 1024 * 1024 # Size of file docx 20 MB 




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




def extract_docx_file_to_json(file_path_input, file_path_output):

    result = {"content": []}

    try:
        file_size_check(file_path_input, MAX_FILE_DOCX_SIZE_BYTES) # Import
        doc = Document(file_path_input)

        for block in iteration_block_items(doc):

            # Paragraph
            if isinstance(block, Paragraph):
                text = block.text.strip()
                style = block.style.name

                if not text:
                    continue

                # Heading detection
                if 'Heading' in style or 'title' in style or \
                   all(run.bold for run in block.runs if run.text.strip()):

                    result["content"].append({
                        "type": "heading",
                        "text": text
                    })

                else:
                    result["content"].append({
                        "type": "paragraph",
                        "text": text
                    })

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






# from docx import Document
# import json



# def extract_table(table):
#     extracted = []
    
#     for row in table.rows:
#         extracted_row = [cell.text.strip() for cell in row.cells]
#         extracted.append(extracted_row)

#     if extracted:
#         return {
#             "columns": extracted[0],
#             "rows": extracted[1:]
#         }
#     else:
#         return {"columns": [], "rows": []}

    



# def extract_docx_file(file_path_input, file_path_output):
            
#     result = { "sections": [] }

#     current_section = None 
#     found_heading = False 

#     try:

#         doc = Document(file_path_input)

#         for para in doc.paragraphs:
#             style = para.style.name
#             text = para.text.strip()
            
#             if not text:
#                 continue


#             if 'Heading' in style or 'title' in style \
#                 or all(run.bold for run in para.runs if run.text.strip()): # Check title if it is bold

#                 found_heading = True

#                 new_section = {
#                     "title": text,
#                     "Paragraph": ""
#                 }
#                 result["sections"].append(new_section)
#                 current_section = new_section


#             else:
#                 # file with title
#                 if found_heading:
#                     if current_section is not None:
#                         current_section["Paragraph"] += text

#                 # file without title
#                 else:
#                     if current_section is None:
#                         current_section = {"Paragraph": ""}
#                         result["sections"].append(current_section)

#                     current_section["Paragraph"] += text
        
        

#         # Table handling
#         if doc.tables:
#             result["tables"] = []
#             for table in doc.tables:
#                 table_data = extract_table(table)
#                 result["tables"].append(table_data)




#         # Create JSON file
#         with open(file_path_output, 'w', encoding='utf-8') as file:
#             json.dump(result, file, ensure_ascii=False, indent=4)


        
#     # Error detection
#     except FileNotFoundError:
#         print("Error: File not found")

#     except PermissionError:
#         print("Error: Permission denied. Make sure the file is not open")

#     except ValueError:
#         print("Error: The file is not a valid DOCX document")

#     except Exception as e:
#         print(f"Error: {e}")


