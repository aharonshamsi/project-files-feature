from docx import Document
import json


def parse_docx_file(file_path_input, file_path_output):
            
    result = { "lessons": [] }

    current_section = None 
    found_heading = False 

    try:

        doc = Document(file_path_input)

        for para in doc.paragraphs:
            style = para.style.name
            text = para.text.strip()
            
            if not text:
                continue

            if 'Heading' in style or 'title' in style:
                found_heading = True

                new_section = {
                    "title": text,
                    "Paragraph": ""
                }
                result["lessons"].append(new_section)
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
                        result["lessons"].append(current_section)

                    current_section["Paragraph"] += text


        # Create JSON file
        with open(file_path_output, 'w', encoding='utf-8') as file:
            json.dump(result, file, ensure_ascii=False, indent=4)

        
    # Error detection
    except FileNotFoundError:
        print("Error: Input file not found")

    except PermissionError:
        print("Error: Permission denied. Make sure the file is not open")

    except ValueError:
        print("Error: The file is not a valid DOCX document")

    except Exception as e:
        print(f"Error: {e}")




