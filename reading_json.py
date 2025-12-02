import json

file_path = "./data/outputs/pdf_text.json"
output_file_path = "output_content.txt"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Open the output file for writing ('w')
    with open(output_file_path, 'w', encoding='utf-8') as outfile:
        
        # Iterate over the main list (each element is usually a page or section)
        for item in data:
            
            # We are interested in items that have the 'content' key
            if 'content' in item and isinstance(item['content'], list):
                page_number = item.get('page_number', 'N/A')
                
                # Write a page separator for clarity in the output file
                outfile.write(f"\n=================================\n")
                outfile.write(f"           PAGE {page_number}           \n")
                outfile.write(f"=================================\n\n")

                # Iterate over the 'content' list
                for content_item in item['content']:
                    
                    # Check if the item has a 'text' key with a string value
                    if 'text' in content_item and isinstance(content_item['text'], str):
                        # The write function automatically handles the \n characters
                        outfile.write(content_item['text'])
                        
                        # Add an extra blank line for separation between paragraphs/headings
                        outfile.write("\n\n")

    print(f"Success: Content written to file: {output_file_path}")
    
except FileNotFoundError:
    print(f"Error: JSON file not found at path: {file_path}")
except json.JSONDecodeError:
    print(f"Error: Failed to decode JSON from file: {file_path}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")