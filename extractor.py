"""Extract text and images from PDF documents with intelligent area mapping."""
import fitz  # PyMuPDF
from pathlib import Path
import re


def parse_area_structure(full_text):
    """
    Parse the PDF text to extract area boundaries and photo ranges.

    Returns:
        dict mapping area names to photo ranges, e.g.:
        {"Hall Skirting": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], ...}
    """
    area_mapping = {}

    # Split by "Impacted Area" to isolate each section
    parts = re.split(r'Impacted Area\s+\d+\s*\n', full_text)

    for part in parts[1:]:  # Skip first part (before first Impacted Area)
        if not part.strip():
            continue

        # Extract area description (first line after "Impacted Area X")
        lines = part.strip().split("\n")

        # The area name is typically in a line with "Description"
        # Look for lines containing area description
        area_name = None
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            # Skip empty lines and generic headers
            if line and not line.startswith("Negative") and not line.startswith("Positive") and not line.startswith("Photo"):
                area_name = line
                break

        if not area_name or area_name.startswith("Image"):
            continue

        # Find all photo numbers in this section
        photo_nums = re.findall(r'Photo\s+(\d+)', part)
        if photo_nums:
            photo_nums = sorted(set([int(p) for p in photo_nums]))
            area_mapping[area_name] = photo_nums

    return area_mapping


def extract_text_and_images(pdf_path, max_images_per_area=2, min_image_size_kb=10):
    """
    Extract text and images from a PDF with intelligent area mapping.

    Parses the PDF structure to understand which images belong to which areas,
    avoiding duplicate image assignment.

    Args:
        pdf_path: Path to PDF file
        max_images_per_area: Max images to keep per area (default 2)
        min_image_size_kb: Skip images smaller than this (default 10KB)

    Returns:
        dict with 'text', 'images', 'area_to_images' (intelligent mapping)
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    doc = fitz.open(pdf_path)
    text_parts = []
    images = []
    min_size_bytes = min_image_size_kb * 1024
    total_pages = len(doc)

    # Extract text and images
    for page_num in range(total_pages):
        page = doc[page_num]

        # Extract text
        text = page.get_text()
        if text.strip():
            text_parts.append(f"--- Page {page_num + 1} ---\n{text}")

        # Extract images in order (critical for photo mapping)
        image_list = page.get_images(full=True)
        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]
            try:
                pix = fitz.Pixmap(doc, xref)
                # Convert to PNG
                if pix.n - pix.alpha < 4:  # Grayscale or RGB
                    image_bytes = pix.tobytes("png")
                else:  # CMYK
                    rgb_pix = fitz.Pixmap(fitz.csRGB, pix)
                    image_bytes = rgb_pix.tobytes("png")

                # Skip tiny images
                if len(image_bytes) < min_size_bytes:
                    continue

                images.append({
                    "page": page_num + 1,
                    "global_index": len(images),  # Photo number (1-indexed)
                    "bytes": image_bytes,
                    "ext": "png",
                    "size_kb": len(image_bytes) / 1024
                })
            except Exception as e:
                print(f"Warning: Could not extract image on page {page_num + 1}: {e}")

    full_text = "\n".join(text_parts)

    # Parse area structure from text to map images to areas
    area_photo_mapping = parse_area_structure(full_text)
    area_to_images = {}

    # Map actual image objects to areas
    for area_name, photo_numbers in area_photo_mapping.items():
        area_images = []
        # Photo numbers are 1-indexed, but we need to match with our image list
        for photo_num in photo_numbers[:max_images_per_area]:  # Limit to max per area
            if 0 <= photo_num - 1 < len(images):
                area_images.append(images[photo_num - 1])

        if area_images:
            area_to_images[area_name] = area_images

    doc.close()

    return {
        "text": full_text,
        "images": images,  # All images in order
        "area_to_images": area_to_images,  # Intelligent mapping: area → images
        "pdf_name": pdf_path.name,
        "total_pages": total_pages
    }
