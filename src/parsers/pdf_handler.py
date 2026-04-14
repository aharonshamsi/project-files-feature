import fitz
import os
import io
import re
import hashlib

from src.parsers.utils import file_size_check, is_solid_color_image
from src.models.document_models import Metadata, ContentBlock, DocumentModel, ImageData
# =========================================================
HEADING = "heading"
PARAGRAPH = "paragraph"
URL = "url"
IMAGE = "image"
TABLE = "table"

PIXELS_LARGER_THAT_AVERAGE = 1.5 # Size of average pixels of the file
TEXT_BLOCK_TYPE = 0 
IMAGE_BLOCK_TYPE = 1
DEFAULT_FONT_SIZE = 12.0
MINI_WORDS = 40 
MIN_IMAGE_SIZE_BYTES = 2*1024  # Minimum image size threshold (2KB)


# ================  extract text (PARAGRAPH AND HEADING) ================================
def extract_pdf_file_to_model(file_stream: io.BytesIO, image_output_dir: str) -> tuple[int, DocumentModel]:
    """
    Main parser function for PDF files. Extracts text, headings, and images page by page.

    Args:
        file_stream (io.BytesIO): The raw binary stream of the PDF file.
        image_output_dir (str): Directory where extracted images should be saved.

    Returns:
        tuple[int, DocumentModel]: Total word count and the structured DocumentModel.

    Raises:
        ValueError: If the total word count is below the minimum threshold.
    """
    total_word_count = 0
    block_list = []

    try:

        file_size_check(file_stream)

        file_stream.seek(0)
        pdf_bytes = file_stream.read()


        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:

            metadata = add_meta_data(doc)

            for page_num in range(doc.page_count):
                page_word_count = parse_page(doc, page_num, block_list, image_output_dir)
                total_word_count += page_word_count

            # Check number of words
            if total_word_count < MINI_WORDS:
                raise ValueError(
            f"Content too short: {total_word_count} words. Minimum required: {MINI_WORDS}"
            )

            final_document = DocumentModel (
                metadata=metadata,
                content_blocks=block_list
            )

            return total_word_count, final_document


    except ValueError as ve:
        print(f"Validation error: {ve}")
        raise

    except Exception as e:
        print(f"Unexpected error while processing PDF: {e}")
        raise


# ===========================================
def add_meta_data(doc) -> Metadata:
    """
    Extracts embedded metadata from the PyMuPDF document.

    Args:
        doc: The parsed fitz (PyMuPDF) Document.

    Returns:
        Metadata: A model containing the document's basic info.
    """
    metadata = doc.metadata

    return Metadata(**metadata)


# =============================================
def combine_block_text(b):
    """
    Combines text spans inside a single PDF block into a cohesive string.

    Args:
        b (dict): A dictionary representing a single text block from the PDF.

    Returns:
        str: The combined and stripped text.
    """
    block_string = ""
    if b['type'] == 0:  # Check if text block
        for line in b["lines"]:
            for span in line["spans"]:
                block_string += span["text"]
    return block_string.strip()


# ===========================================================
def parse_page(doc, page_num, block_list, image_output_dir):
    """
    Parses a single PDF page for text blocks, urls, and images, appending them
    to the shared block_list array.

    Args:
        doc: The fitz Document object.
        page_num (int): The index of the current page being parsed.
        block_list (list): Reference to the master list of ContentBlocks.
        image_output_dir (str): Directory to save extracted images.

    Returns:
        int: The number of words parsed on this specific page.
    """
    page = doc.load_page(page_num)
    body_size = get_page_body_size(page) 
    blocks = page.get_text("dict")["blocks"]

    all_page_links = page.get_links()

    # Extract all images directly from the page at the canvas level.
    # This ensures background images and full-page overlays are captured, 
    # which are often bypassed by the standard text-block parser.
    for img in page.get_images(full=True):
        xref = img[0]
        base_image = doc.extract_image(xref) 
        
        img_path = save_pdf_image(base_image, page_num, len(block_list), image_output_dir)
        if img_path:
            block_list.append(ContentBlock(
                block_id=len(block_list) + 1,
                type=IMAGE,
                image_data=ImageData(image_path=img_path)
            ))

    current_paragraph_text = ""
    current_element_type = PARAGRAPH
    current_urls = []
    blocks.sort(key=lambda b: b['bbox'][1]) # Sort the blocks
    
    word_count = 0

    for b in blocks:

        # Images
        if b['type'] == IMAGE_BLOCK_TYPE: 
            # Skip inline images to prevent duplication, as all images 
            # (including inline) were already extracted via get_images() above.
            continue

        # text
        block_text = combine_block_text(b)

        if not block_text:
            continue
        
        if b['type'] == TEXT_BLOCK_TYPE: # Block of text

            urls_in_this_block = get_urls_from_block(block_text, b["bbox"], all_page_links)

            # Check the entire paragraph is bold.
            is_bold = is_block_fully_bold(b) 
            
            span = b["lines"][0]["spans"][0]
            first_span_size = round(span["size"], 1)

            # Decide if heading
            is_new_header_candidate = (
                first_span_size > body_size + PIXELS_LARGER_THAT_AVERAGE
                or is_bold
            )
            
            # Heading
            if is_new_header_candidate: 
                block_type = HEADING
            
            # Paragraph
            else:
                block_type = PARAGRAPH

            if block_type != current_element_type or block_type == HEADING: 

                if current_paragraph_text:
                    text_to_save = current_paragraph_text

                    for url in current_urls:
                        text_to_save = text_to_save.replace(url, "")

                    block_list.append(ContentBlock(
                        block_id=len(block_list) + 1,
                        type=current_element_type,
                        text=text_to_save.strip()
                    ))
                    word_count += len(text_to_save.split())

                    for url in current_urls:
                        block_list.append(ContentBlock(
                            block_id=len(block_list) + 1,
                            type=URL,
                            text=url
                        ))
                
                current_paragraph_text = block_text
                current_element_type = block_type
                current_urls = urls_in_this_block

            else:
                current_paragraph_text += "\n" + block_text
                current_urls.extend(urls_in_this_block)


    # Last block
    if current_paragraph_text:

        text_to_save = current_paragraph_text
        for url in current_urls:
            text_to_save = text_to_save.replace(url, "")

        text_to_save = re.sub(r' +', ' ', text_to_save).strip()

        block_list.append(ContentBlock(
            block_id=len(block_list) + 1,
            type=current_element_type,
            text=text_to_save.strip()
        ))
        
        word_count += len(text_to_save.split())

        for url in current_urls:
            block_list.append(ContentBlock(
                block_id=len(block_list) + 1,
                type=URL,
                text=url
            ))
    
    return word_count


# =====================================================================
def get_page_body_size(page):
    """
    Calculates the most common font size (the mode) on a given PDF page to determine 
    the baseline body text size.

    Args:
        page: The fitz Page object.

    Returns:
        float: The most frequent font size, or DEFAULT_FONT_SIZE if none found.
    """
    font_counts = {}
    blocks = page.get_text("dict")["blocks"]

    for b in blocks:
        if b['type'] == TEXT_BLOCK_TYPE:  # Check if text block
            for line in b["lines"]:
                for span in line["spans"]:
                    size = round(span["size"], 1)
                    font_counts[size] = font_counts.get(size, 0) + 1
    
    # Return the size with the highest count (the mode), or default to 12
    if font_counts:
        return max(font_counts, key=font_counts.get)
    
    return DEFAULT_FONT_SIZE


# ===============================================================
def is_block_fully_bold(block):
    """
    Checks if every span of text within a block has bold styling applied.

    Args:
        block (dict): The text block dictionary from PyMuPDF.

    Returns:
        bool: True if the entire block is styled bold, False otherwise.
    """
    if block['type'] != TEXT_BLOCK_TYPE:
        return False
        
    # Check the entire paragraph is bold.
    for line in block["lines"]:
        for span in line["spans"]:

            is_bold_flag = bool(span["flags"] & 2)
            is_bold_font = "bold" in span["font"].lower()
            
            if not (is_bold_flag or is_bold_font):
                return False
    
    return True


# ==============================================================
def get_urls_from_block(block_text, block_bbox, page_links):
    """
    Extracts URLs from a PDF text block either by overlapping annotation rectangles 
    or by pure text regex matching.

    Args:
        block_text (str): The text content of the block.
        block_bbox (list): The coordinates of the block's bounding box.
        page_links (list): A list of hyperlink dicts extracted from the PDF page.

    Returns:
        list: A deduplicated list of URLs found within the block.
    """
    found_urls = set()

    # The coordinates of the rectangle surrounding the text [x0, y0, x1, y1]
    block_rect = fitz.Rect(block_bbox)

    for link in page_links:
        link_type = link.get("type")
        link_rect = link.get("from")
        link_uri = link.get("uri")

        if link_type == fitz.LINK_URI and link_rect and link_uri:
            if block_rect.intersects(link_rect):
                found_urls.add(link_uri)

    # Text search of link
    text_to_search = block_text.replace("\n", "")
    url_pattern = r'(https?://[^\s<>"]+|www\.[^\s<>"]+)'
    text_urls = re.findall(url_pattern, text_to_search)

    for url in text_urls:
        found_urls.add(url.rstrip('.,!?;:)'))

    return list(found_urls)


# =====================================================================
def save_pdf_image(image_block, page_num, block_id, image_output_dir):
    """
    Validates, hashes, and saves a PDF image to disk, skipping small or solid-color images.

    Args:
        image_block (dict): The image data dictionary extracted via PyMuPDF.
        page_num (int): The current page number (for logging).
        block_id (int): The current block identifier.
        image_output_dir (str): Directory where the image will be saved.

    Returns:
        str or None: The absolute path to the saved image, or None if skipped/failed.
    """
    try:
        image_bytes = image_block.get("image")

        if not image_bytes:
            return None

        # Skip saving if the image is smaller than the threshold
        if len(image_bytes) < MIN_IMAGE_SIZE_BYTES:
            return None    
        
        extension = image_block.get("ext", "png")
        if is_solid_color_image(image_bytes):
            print(f"Skipping solid color image found on PDF page {page_num+1}")
            return None # PDF handler returns None to indicate failure/skip
        
        # Generate unique hash from the image bytes
        image_hash = hashlib.sha256(image_bytes).hexdigest()
        image_filename = f"{image_hash}.{extension}"
        full_path = os.path.join(image_output_dir, image_filename)
        
        # Check if the image already exists on disk before saving
        if not os.path.exists(full_path):
            with open(full_path, "wb") as f:
                f.write(image_bytes)
            
        return full_path
    
    except Exception as e:
        print(f"Error saving PDF image: {e}")
        return None