import json
import os

# --- Configuration ---
# Update these paths to match your exact file location
json_file_path = "data/outputs/hashmal.json"  # Input JSON
output_txt_path = "output_content.txt"         # Output Text File

def generate_readable_text_file(input_path, output_path):
    try:
        # 1. Read the JSON file
        if not os.path.exists(input_path):
            print(f"❌ Error: JSON file not found at {input_path}")
            return

        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 2. Write to the TXT file
        with open(output_path, 'w', encoding='utf-8') as outfile:
            
            # Iterate through the main list (pages and metadata)
            for item in data:
                
                # Case A: Metadata Block
                if item.get("type") == "file_meta_data":
                    outfile.write("=================================\n")
                    outfile.write("       📄 FILE METADATA          \n")
                    outfile.write("=================================\n")
                    # Loop through metadata fields
                    meta_content = item.get("text", {})
                    if isinstance(meta_content, dict):
                        for key, value in meta_content.items():
                            outfile.write(f"{key}: {value}\n")
                    outfile.write("\n\n")
                    continue

                # Case B: Page Content Block
                # Check if this item is a page (has page_number and content list)
                if "page_number" in item and "content" in item:
                    page_num = item["page_number"]
                    
                    outfile.write("---------------------------------\n")
                    outfile.write(f"          PAGE {page_num}       \n")
                    outfile.write("---------------------------------\n\n")
                    
                    # Iterate through the elements inside the page (paragraphs/headings/images)
                    for element in item["content"]:
                        
                        # Extract type and text/path
                        elem_type = element.get("type", "unknown").upper()
                        
                        if elem_type == "IMAGE":
                            image_path = element.get("image_path", "N/A")
                            outfile.write(f"[{elem_type}] Path: {image_path}\n")
                            
                        else: # Text (Paragraph / Heading)
                            text = element.get("text", "")
                            # Write the type label and then the text
                            outfile.write(f"[{elem_type}]:\n{text}\n")
                        
                        # Add spacing between elements
                        outfile.write("\n")
                    
                    # Add extra spacing between pages
                    outfile.write("\n\n")

        print(f"✅ Success! Readable content saved to: {output_path}")

    except json.JSONDecodeError:
        print(f"❌ Error: Failed to decode JSON. The file might be corrupted or empty.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

# --- Execution ---
generate_readable_text_file(json_file_path, output_txt_path)