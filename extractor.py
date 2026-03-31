"""Extract text and images from PDF documents."""
import fitz  # PyMuPDF
from pathlib import Path


def extract_text_and_images(pdf_path):
    """
    Extract text and images from a PDF.

    Returns:
        dict with 'text' (str) and 'images' (list of {page, image_index, bytes, image_ext})
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    doc = fitz.open(pdf_path)
    text_parts = []
    images = []

    # Extract text and images page by page
    for page_num in range(len(doc)):
        page = doc[page_num]

        # Extract text
        text = page.get_text()
        if text.strip():
            text_parts.append(f"--- Page {page_num + 1} ---\n{text}")

        # Extract images
        image_list = page.get_images(full=True)
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

                images.append({
                    "page": page_num + 1,
                    "image_index": img_index,
                    "bytes": image_bytes,
                    "ext": "png"
                })
            except Exception as e:
                print(f"Warning: Could not extract image on page {page_num + 1}: {e}")

    doc.close()

    return {
        "text": "\n".join(text_parts),
        "images": images,
        "pdf_name": pdf_path.name
    }
