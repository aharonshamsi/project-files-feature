import zipfile
from pathlib import Path
import zipfile
import io
from PIL import Image

MAX_FILE_DOCX_SIZE_BYTES = 20 * 1024 * 1024 # MAX 20 MB 
MINI_FILE_DOCX_SIZE_BYTES = 1 * 1024  # MINI 10 KB 

#===============================================================================
# CHECK SIZE OF THE FILE, MAX & MINI
def file_size_check(file_stream: io.BytesIO):
    """
    Validates if the provided file stream falls within the allowed size limits.

    Args:
        file_stream (io.BytesIO): The file stream to be checked.

    Raises:
        ValueError: If the file is larger than MAX_FILE_DOCX_SIZE_BYTES or 
                    smaller than MINI_FILE_DOCX_SIZE_BYTES.
    """
    file_size = file_stream.getbuffer().nbytes

    if file_size > MAX_FILE_DOCX_SIZE_BYTES:
        raise ValueError(f"The file size exceeds the maximum allowed size of {MAX_FILE_DOCX_SIZE_BYTES} bytes")
    
    elif file_size < MINI_FILE_DOCX_SIZE_BYTES:
        raise ValueError(f"The file size is smaller than the minimum required size of {MINI_FILE_DOCX_SIZE_BYTES} bytes")
    
#===============================================================================
# Check and return suffix type of the file
def get_file_extension_type(file_path):
    """
    Determines the file type (pdf, docx, or pptx) based on its binary header or ZIP structure.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: 'pdf', 'docx', or 'pptx' depending on the detected file format.

    Raises:
        ValueError: If the file format is unsupported or corrupted.
    """
    with open(file_path, 'rb') as f:
        header = f.read(5)

    # PDF
    if header.startswith(b'%PDF-'):
        return 'pdf'

    # Possible DOCX or PPTX (Both are ZIP archives)
    if header.startswith(b'PK\x03\x04'):
        try:
            with zipfile.ZipFile(file_path) as z:
                # Get the list of files inside the archive once
                file_list = z.namelist()

                # Check for Word document structure
                if 'word/document.xml' in file_list:
                    return 'docx'
                
                # Check for PowerPoint presentation structure
                if 'ppt/presentation.xml' in file_list:
                    return 'pptx'

        except zipfile.BadZipFile:
            pass

    raise ValueError(f"Unsupported or corrupted file type: '{file_path}'")

#===============================================================================
def is_solid_color_image(image_bytes: bytes, tolerance: int = 5) -> bool:
    """
    Checks if an image consists of only a single solid color or is fully transparent.
    Allows a small tolerance for compression artifacts.

    Args:
        image_bytes (bytes): The raw binary data of the image.
        tolerance (int, optional): The allowed variance across color channels. Defaults to 5.

    Returns:
        bool: True if the image is a solid color or completely transparent, False otherwise.
    """
    try:
        # 1. Wrap bytes in BytesIO
        image_file = io.BytesIO(image_bytes)
        
        # 2. Open the image using Pillow
        with Image.open(image_file) as img:
            
            # --- Check for transparency (Alpha channel) ---
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                rgba_img = img.convert('RGBA')
                extrema = rgba_img.getextrema()
                # extrema for RGBA is ((Rmin, Rmax), (Gmin, Gmax), (Bmin, Bmax), (Amin, Amax))
                
                # If the maximum Alpha value is 0 (or very close to it), the image is completely transparent/invisible
                if extrema[3][1] <= tolerance:
                    return True
                    
                # Otherwise, check if variance in all RGBA channels is within tolerance
                is_solid = all((max_val - min_val) <= tolerance for min_val, max_val in extrema)
                return is_solid
            
            # --- For regular, non-transparent images ---
            rgb_img = img.convert('RGB')
            extrema = rgb_img.getextrema()
            
            # Check if variance in all RGB channels is within the allowed tolerance
            is_solid = all((max_val - min_val) <= tolerance for min_val, max_val in extrema)
            return is_solid
            
    except Exception as e:
        # If Pillow cannot open the bytes as a valid image
        print(f"Warning: Could not analyze image for solid color. Error: {e}")
        return False