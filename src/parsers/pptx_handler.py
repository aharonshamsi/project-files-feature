import json
import os
from pptx import Presentation

def extract_pptx_file_to_json(input_path, output_path):
    """
    Extracts text from a PPTX file and saves it as a structured JSON file.
    """
    try:
        # Load the PowerPoint presentation
        presentation = Presentation(input_path)
        slides_data = []

        # Iterate through slides
        for i, slide in enumerate(presentation.slides, start=1):
            slide_text_elements = []
            
            # Iterate through all shapes in the current slide
            for shape in slide.shapes:
                # Only extract from shapes that contain text
                if hasattr(shape, "text") and shape.text.strip():
                    slide_text_elements.append(shape.text.strip())
            
            # Store slide content with its number
            slides_data.append({
                "slide_number": i,
                "content": "\n".join(slide_text_elements)
            })

        # Prepare final JSON structure
        final_data = {
            "metadata": {
                "filename": os.path.basename(input_path),
                "total_slides": len(presentation.slides),
                "format": "pptx"
            },
            "slides": slides_data
        }

        # Write data to the output JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
            
        print(f"Successfully extracted {input_path} to {output_path}")

    except Exception as e:
        print(f"Error during PPTX extraction: {e}")
        raise