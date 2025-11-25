from docx import Document
import json



def extract_table(table):
    extracted = []
    
    for row in table.rows:
        extracted_row = [cell.text.strip() for cell in row.cells]
        extracted.append(extracted_row)

    if extracted:
        return {
            "columns": extracted[0],
            "rows": extracted[1:]
        }
    else:
        return {"columns": [], "rows": []}

    



def extract_docx_file(file_path_input, file_path_output):
            
    result = { "sections": [] }

    current_section = None 
    found_heading = False 

    try:

        doc = Document(file_path_input)

        for para in doc.paragraphs:
            style = para.style.name
            text = para.text.strip()
            
            if not text:
                continue


            if 'Heading' in style or 'title' in style \
                or all(run.bold for run in para.runs if run.text.strip()): # Check title if it is bold

                found_heading = True

                new_section = {
                    "title": text,
                    "Paragraph": ""
                }
                result["sections"].append(new_section)
                current_section = new_section


            else:
                # file with title
                if found_heading:
                    if current_section is not None:
                        current_section["Paragraph"] += text

                # file without title
                else:
                    if current_section is None:
                        current_section = {"Paragraph": ""}
                        result["sections"].append(current_section)

                    current_section["Paragraph"] += text
        
        

        # Table handling
        if doc.tables:
            result["tables"] = []
            for table in doc.tables:
                table_data = extract_table(table)
                result["tables"].append(table_data)




        # Create JSON file
        with open(file_path_output, 'w', encoding='utf-8') as file:
            json.dump(result, file, ensure_ascii=False, indent=4)


        
    # Error detection
    except FileNotFoundError:
        print("Error: File not found")

    except PermissionError:
        print("Error: Permission denied. Make sure the file is not open")

    except ValueError:
        print("Error: The file is not a valid DOCX document")

    except Exception as e:
        print(f"Error: {e}")



