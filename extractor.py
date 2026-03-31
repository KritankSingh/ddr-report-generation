"""Extract text and images from PDF documents."""
import fitz  # PyMuPDF
from pathlib import Path


def extract_text_and_images(pdf_path, max_images_per_area=2, min_image_size_kb=10):
    """
    Extract text and images from a PDF with smart filtering.

    Args:
        pdf_path: Path to PDF file
        max_images_per_area: Max images to keep per area (default 2)
        min_image_size_kb: Skip images smaller than this (default 10KB)

    Returns:
        dict with 'text' (str), 'images' (list), 'images_by_page' (dict)
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    doc = fitz.open(pdf_path)
    text_parts = []
    images = []
    images_by_page = {}
    min_size_bytes = min_image_size_kb * 1024

    # Extract text and images page by page
    for page_num in range(len(doc)):
        page = doc[page_num]

        # Extract text
        text = page.get_text()
        if text.strip():
            text_parts.append(f"--- Page {page_num + 1} ---\n{text}")

        # Extract images
        image_list = page.get_images(full=True)
        page_images = []

        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]
            try:
                pix = fitz.Pixmap(doc, xref)
                # Convert to PNG if needed
                if pix.n - pix.alpha < 4:  # Grayscale or RGB
                    image_bytes = pix.tobytes("png")
                else:  # CMYK
                    rgb_pix = fitz.Pixmap(fitz.csRGB, pix)
                    image_bytes = rgb_pix.tobytes("png")

                # Skip tiny images (thumbnails, etc.)
                if len(image_bytes) < min_size_bytes:
                    continue

                image_dict = {
                    "page": page_num + 1,
                    "image_index": len(images),  # Global index
                    "bytes": image_bytes,
                    "ext": "png",
                    "size_kb": len(image_bytes) / 1024
                }

                images.append(image_dict)
                page_images.append(image_dict)

            except Exception as e:
                print(f"Warning: Could not extract image on page {page_num + 1}: {e}")

        # Store per-page mapping for area assignment
        if page_images:
            images_by_page[page_num + 1] = page_images[:max_images_per_area]

    doc.close()

    return {
        "text": "\n".join(text_parts),
        "images": images,
        "images_by_page": images_by_page,
        "pdf_name": pdf_path.name,
        "total_pages": len(doc)
    }
