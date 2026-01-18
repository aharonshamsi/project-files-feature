import json
import os
import re
from pptx import Presentation
from pptx.enum.shapes import PP_PLACEHOLDER

# =========================================================
# Constants
# =========================================================
HEADING_TYPE = "heading"
PARAGRAPH_TYPE = "paragraph"
TABLE_TYPE = "table"
URL_TYPE = "url"

DEFAULT_FONT_SIZE = 14.0
FONT_SIZE_DELTA = 5
TOP_HEADING_RATIO = 0.2
MAX_HEADING_WORDS = 10
EMPHASIZED_RATIO = 0.6
MINI_WORDS = 40 # i didnt do it yet

# =========================================================
def extract_pptx_metadata(prs):
    props = prs.core_properties
    return {
        "title": props.title or "",
        "author": props.author or "",
        "subject": props.subject or "",
        "creation_date": str(props.created) if props.created else None,
    }

# =========================================================
def normalize_text(text):
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

# =========================================================
def extract_urls(text):
    return re.findall(r'https?://[^\s)]+', text)

# =========================================================
def is_auto_slide_number(shape):
    if not shape.is_placeholder:
        return False
    try:
        return shape.placeholder_format.type == PP_PLACEHOLDER.SLIDE_NUMBER
    except KeyError:
        return False

# =========================================================
def get_slide_body_size(slide):
    font_counts = {}

    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for paragraph in shape.text_frame.paragraphs:
            for run in paragraph.runs:
                if run.font.size:
                    size = round(run.font.size.pt, 1)
                    font_counts[size] = font_counts.get(size, 0) + 1

    return max(font_counts, key=font_counts.get) if font_counts else DEFAULT_FONT_SIZE

# =========================================================
def shape_is_heading(shape, slide_height, body_font_size):
    if not shape.has_text_frame:
        return False

    text = normalize_text(shape.text_frame.text)
    if not text:
        return False

    words = text.split()

    # Placeholder title always wins
    if shape.is_placeholder:
        ph_type = shape.placeholder_format.type
        if ph_type in (PP_PLACEHOLDER.TITLE, PP_PLACEHOLDER.CENTER_TITLE):
            return True
        if ph_type in (PP_PLACEHOLDER.BODY, PP_PLACEHOLDER.OBJECT):
            return False

    shape_bottom = shape.top + shape.height

    if (
        shape_bottom < slide_height * TOP_HEADING_RATIO and
        len(words) <= MAX_HEADING_WORDS
    ):
        emphasized_runs = 0
        total_runs = 0

        for paragraph in shape.text_frame.paragraphs:
            for run in paragraph.runs:
                if not run.text.strip():
                    continue
                total_runs += 1
                if run.font.bold or (
                    run.font.size and run.font.size.pt > body_font_size + FONT_SIZE_DELTA
                ):
                    emphasized_runs += 1

        if total_runs and emphasized_runs / total_runs >= EMPHASIZED_RATIO:
            return True

    return False

# =========================================================
def extract_pptx_to_json(input_file, output_file):
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"File not found: {input_file}")

    prs = Presentation(input_file)
    slide_height = prs.slide_height
    total_word_count = 0
    result = {
        "metadata": extract_pptx_metadata(prs),
        "pages": []
    }

    for slide_index, slide in enumerate(prs.slides):
        page_elements = []
        body_font_size = get_slide_body_size(slide)

        shapes = sorted(slide.shapes, key=lambda s: (s.top, s.left))

        for shape in shapes:
            if is_auto_slide_number(shape):
                continue

            # ================= TABLE =================
            if shape.has_table:
                rows = []
                for row in shape.table.rows:

                    rows.append([
                        normalize_text(cell.text_frame.text)
                        for cell in row.cells
                    ])

                page_elements.append({
                    "type": TABLE_TYPE,
                    "headers": rows[0] if rows else [],
                    "rows": rows[1:] if len(rows) > 1 else []
                })
                continue

            # ================= TEXT =================
            if not shape.has_text_frame:
                continue

            element_type = (
                HEADING_TYPE
                if shape_is_heading(shape, slide_height, body_font_size)
                else PARAGRAPH_TYPE
            )

            collected_text = []

            for paragraph in shape.text_frame.paragraphs:
                text = normalize_text(paragraph.text)
                if text:
                    collected_text.append(text)

            if not collected_text:
                continue

            full_text = "\n".join(collected_text)

            urls = extract_urls(full_text)
            clean_text = full_text
            for url in urls:
                clean_text = clean_text.replace(url, "").strip()

            if clean_text:
                total_word_count += len(clean_text.split())
                # Merge consecutive paragraphs of same type
                if (
                    page_elements and
                    page_elements[-1]["type"] == element_type
                ):
                    page_elements[-1]["text"] += "\n" + clean_text
                else:
                    page_elements.append({
                        "type": element_type,
                        "text": clean_text
                    })

            for url in urls:
                total_word_count += 1
                
                page_elements.append({
                    "type": URL_TYPE,
                    "text": url
                })

        result["pages"].append({
            "page_number": slide_index + 1,
            "content": page_elements
        })

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    return total_word_count
    # return result
