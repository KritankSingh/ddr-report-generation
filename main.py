"""Main entry point for DDR (Detailed Diagnostic Report) generation."""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Fix encoding on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables
load_dotenv()

from extractor import extract_text_and_images
from llm_processor import process_documents
from report_generator import generate_docx


def main():
    """Generate a DDR from inspection and thermal PDF reports."""
    # Parse command-line arguments
    if len(sys.argv) < 3:
        print("Usage: python main.py <inspection_pdf> <thermal_pdf> [output.docx]")
        sys.exit(1)

    inspection_pdf = sys.argv[1]
    thermal_pdf = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else "DDR_Report.docx"

    # Verify input files exist
    if not Path(inspection_pdf).exists():
        print(f"Error: Inspection PDF not found: {inspection_pdf}")
        sys.exit(1)
    if not Path(thermal_pdf).exists():
        print(f"Error: Thermal PDF not found: {thermal_pdf}")
        sys.exit(1)

    # Verify API key is set
    if not os.getenv("Anthropic_API_Key"):
        print("Error: Anthropic_API_Key not set in .env file")
        sys.exit(1)

    print(f"Extracting from: {inspection_pdf}")
    print(f"Extracting from: {thermal_pdf}")

    # Step 1: Extract text and images
    print("\n[1/3] Extracting documents...")
    inspection_data = extract_text_and_images(inspection_pdf)
    thermal_data = extract_text_and_images(thermal_pdf)
    print(f"  [OK] Extracted {len(inspection_data['images'])} images from inspection report")
    print(f"  [OK] Extracted {len(thermal_data['images'])} images from thermal report")

    # Step 2: Process with Claude API
    print("\n[2/3] Processing with Claude API...")
    ddr_data, insp_imgs, therm_imgs = process_documents(inspection_data, thermal_data)
    print("  [OK] DDR structured successfully")

    # Step 3: Generate DOCX report
    print(f"\n[3/3] Generating DOCX report...")
    generate_docx(ddr_data, insp_imgs, therm_imgs, output_path)
    print(f"  [OK] Report saved: {output_path}")

    print("\n[SUCCESS] DDR generation complete!")


if __name__ == "__main__":
    main()
