"""Extract text and images from PDF documents with intelligent area mapping."""
import fitz  # PyMuPDF
from pathlib import Path
import re

# Hard limits to prevent Streamlit Cloud timeout
MAX_PAGES = 15          # Only read first 15 pages
MAX_TOTAL_IMAGES = 20   # Max images total per PDF
MAX_IMAGES_PER_AREA = 2 # Max images per area in report
MIN_IMAGE_SIZE_KB = 15  # Skip small/decorative images


def parse_area_structure(full_text):
    """Parse PDF text to extract area boundaries and photo ranges."""
    area_mapping = {}
    parts = re.split(r'Impacted Area\s+\d+\s*\n', full_text)

    for part in parts[1:]:
        if not part.strip():
            continue

        lines = part.strip().split("\n")
        area_name = None
        for line in lines[:10]:
            line = line.strip()
            if line and not line.startswith("Negative") and not line.startswith("Positive") and not line.startswith("Photo"):
                area_name = line
                break

        if not area_name or area_name.startswith("Image"):
            continue

        photo_nums = re.findall(r'Photo\s+(\d+)', part)
        if photo_nums:
            photo_nums = sorted(set([int(p) for p in photo_nums]))
            area_mapping[area_name] = photo_nums

    return area_mapping


def extract_text_and_images(pdf_path, max_images_per_area=MAX_IMAGES_PER_AREA, min_image_size_kb=MIN_IMAGE_SIZE_KB):
    """
    Extract text and images from a PDF with strict limits for cloud deployment.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    doc = fitz.open(pdf_path)
    text_parts = []
    images = []
    min_size_bytes = min_image_size_kb * 1024
    total_pages = len(doc)

    # LIMIT: only process first MAX_PAGES pages
    pages_to_process = min(total_pages, MAX_PAGES)

    for page_num in range(pages_to_process):
        page = doc[page_num]

        # Extract text
        text = page.get_text()
        if text.strip():
            text_parts.append(f"--- Page {page_num + 1} ---\n{text}")

        # LIMIT: stop collecting images once we hit MAX_TOTAL_IMAGES
        if len(images) >= MAX_TOTAL_IMAGES:
            continue

        image_list = page.get_images(full=True)
        for img_info in image_list:
            if len(images) >= MAX_TOTAL_IMAGES:
                break

            xref = img_info[0]
            try:
                pix = fitz.Pixmap(doc, xref)
                if pix.n - pix.alpha < 4:
                    image_bytes = pix.tobytes("png")
                else:
                    rgb_pix = fitz.Pixmap(fitz.csRGB, pix)
                    image_bytes = rgb_pix.tobytes("png")

                if len(image_bytes) < min_size_bytes:
                    continue

                images.append({
                    "page": page_num + 1,
                    "global_index": len(images),
                    "bytes": image_bytes,
                    "ext": "png",
                    "size_kb": len(image_bytes) / 1024
                })
            except Exception:
                pass

    full_text = "\n".join(text_parts)

    # Map images to areas
    area_photo_mapping = parse_area_structure(full_text)
    area_to_images = {}

    for area_name, photo_numbers in area_photo_mapping.items():
        area_images = []
        for photo_num in photo_numbers[:max_images_per_area]:
            if 0 <= photo_num - 1 < len(images):
                area_images.append(images[photo_num - 1])
        if area_images:
            area_to_images[area_name] = area_images

    doc.close()

    return {
        "text": full_text,
        "images": images,
        "area_to_images": area_to_images,
        "pdf_name": pdf_path.name,
        "total_pages": total_pages
    }