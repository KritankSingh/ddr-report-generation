"""Streamlit web UI for DDR Report Generation."""
import streamlit as st
import tempfile
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from extractor import extract_text_and_images
from llm_processor import process_documents
from report_generator import generate_docx

# Page config
st.set_page_config(
    page_title="DDR Report Generator",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 30px;
    }
    .status-success {
        color: #27ae60;
        font-weight: bold;
    }
    .status-error {
        color: #e74c3c;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.markdown("# 📋 DDR Report Generator", unsafe_allow_html=True)
st.markdown("Generate structured Detailed Diagnostic Reports from inspection and thermal PDFs")
st.divider()

# Check API key
if not os.getenv("Anthropic_API_Key"):
    st.error("❌ Anthropic API Key not found. Please add `Anthropic_API_Key` to your `.env` file.")
    st.stop()

# Initialize session state for managing uploads and generation state
if "report_generated" not in st.session_state:
    st.session_state.report_generated = False
    st.session_state.output_file = None

# File upload section
st.subheader("📁 Upload Documents", divider=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Inspection Report (PDF)**")
    inspection_file = st.file_uploader(
        "Upload Inspection Report",
        type=["pdf"],
        key="inspection_upload",
        label_visibility="collapsed"
    )

with col2:
    st.markdown("**Thermal Report (PDF)**")
    thermal_file = st.file_uploader(
        "Upload Thermal Report",
        type=["pdf"],
        key="thermal_upload",
        label_visibility="collapsed"
    )

st.divider()

# Generate Report button
col_button, col_spacer = st.columns([1, 4])

with col_button:
    generate_button = st.button(
        "🚀 Generate Report",
        type="primary",
        use_container_width=True
    )

# Process documents when button is clicked
if generate_button:
    # Validate file uploads
    if not inspection_file or not thermal_file:
        st.error("❌ Please upload both documents before generating the report.")
        st.stop()

    # Show progress
    with st.spinner("Processing your documents..."):
        try:
            # Create temporary directory for uploaded files
            with tempfile.TemporaryDirectory() as tmpdir:
                # Save uploaded files temporarily
                inspection_path = Path(tmpdir) / "inspection.pdf"
                thermal_path = Path(tmpdir) / "thermal.pdf"

                with open(inspection_path, "wb") as f:
                    f.write(inspection_file.getbuffer())

                with open(thermal_path, "wb") as f:
                    f.write(thermal_file.getbuffer())

                # Step 1: Extract text and images
                st.info("📖 Step 1/3: Extracting documents...")
                try:
                    inspection_data = extract_text_and_images(str(inspection_path))
                    thermal_data = extract_text_and_images(str(thermal_path))
                    st.success(
                        f"✓ Extracted {len(inspection_data['images'])} images from inspection report "
                        f"and {len(thermal_data['images'])} images from thermal report"
                    )
                except FileNotFoundError as e:
                    st.error(f"❌ File error: {e}")
                    st.stop()
                except Exception as e:
                    st.error(f"❌ Extraction error: {e}")
                    st.stop()

                # Step 2: Process with Claude API
                st.info("🤖 Step 2/3: Processing with Claude API...")
                try:
                    ddr_data, insp_imgs, therm_imgs = process_documents(inspection_data, thermal_data)
                    st.success("✓ DDR structure generated successfully")
                except KeyError as e:
                    st.error(f"❌ API Key error: {e}. Ensure `Anthropic_API_Key` is set correctly.")
                    st.stop()
                except Exception as e:
                    st.error(f"❌ Processing error: {e}")
                    st.stop()

                # Step 3: Generate DOCX report
                st.info("📝 Step 3/3: Generating DOCX report...")
                try:
                    output_docx = Path(tmpdir) / "DDR_Report.docx"
                    generate_docx(ddr_data, insp_imgs, therm_imgs, str(output_docx))

                    # Read the generated file
                    with open(output_docx, "rb") as f:
                        report_bytes = f.read()

                    st.session_state.report_generated = True
                    st.session_state.output_file = report_bytes

                    st.success("✓ Report generated successfully!")
                except Exception as e:
                    st.error(f"❌ Report generation error: {e}")
                    st.stop()

# Download section (only show if report was generated)
if st.session_state.report_generated and st.session_state.output_file:
    st.divider()
    st.subheader("📥 Download Report", divider=True)

    st.download_button(
        label="⬇️ Download DDR Report (DOCX)",
        data=st.session_state.output_file,
        file_name="DDR_Report.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True
    )

    st.success("Your report is ready to download!")

# Footer
st.divider()
st.markdown("""
    ---
    **About DDR Reports**: Detailed Diagnostic Reports provide a structured analysis of property
    inspection findings with thermal imaging data integration, severity assessments, and actionable recommendations.
    """)
