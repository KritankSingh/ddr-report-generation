"""Streamlit web UI for DDR Report Generation."""
import sys
import traceback

# Set up page config FIRST before any other Streamlit commands
import streamlit as st
st.set_page_config(
    page_title="DDR Report Generator",
    page_icon="📋",
    layout="wide"
)

# Now import other modules with error handling
import tempfile
import os
from pathlib import Path

try:
    from extractor import extract_text_and_images
    from llm_processor import process_documents
    from report_generator import generate_docx
except Exception as e:
    st.error(f"❌ Import error: {type(e).__name__}: {e}")
    st.stop()


# Cached extraction functions to avoid re-processing on reruns
@st.cache_data(show_spinner=False)
def cached_extract_inspection(file_bytes, filename):
    """Cache inspection report extraction."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(file_bytes)
        temp_path = f.name
    try:
        return extract_text_and_images(temp_path, max_images_per_area=2, min_image_size_kb=10)
    finally:
        os.unlink(temp_path)


@st.cache_data(show_spinner=False)
def cached_extract_thermal(file_bytes, filename):
    """Cache thermal report extraction."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(file_bytes)
        temp_path = f.name
    try:
        return extract_text_and_images(temp_path, max_images_per_area=5, min_image_size_kb=10)
    finally:
        os.unlink(temp_path)

# Page config already set above

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

# Check and load API key from Streamlit secrets
try:
    api_key = st.secrets["Anthropic_API_Key"]
    # Also set in environment for llm_processor compatibility
    os.environ["Anthropic_API_Key"] = api_key
except KeyError as e:
    st.error(
        f"❌ Anthropic API Key not found in Streamlit secrets. "
        f"\n\nPlease add your API key to `.streamlit/secrets.toml`:\n"
        f"```\nAnthropic_API_Key = 'sk-ant-...'\n```\n"
        f"Or set it via Streamlit Cloud settings (Settings → Secrets)"
    )
    st.stop()
except Exception as e:
    st.error(f"❌ Error loading API key: {e}")
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

    # Create progress container
    progress_container = st.container()
    progress_bar = progress_container.progress(0, text="🔄 Preparing...")

    try:
        # Step 1: Extract documents (with caching)
        with st.spinner("📖 Extracting documents..."):
            progress_bar.progress(10, text="📖 Extracting inspection report...")
            inspection_data = cached_extract_inspection(
                inspection_file.getbuffer().tobytes(),
                inspection_file.name
            )

            progress_bar.progress(30, text="📖 Extracting thermal report...")
            thermal_data = cached_extract_thermal(
                thermal_file.getbuffer().tobytes(),
                thermal_file.name
            )

            progress_bar.progress(50, text="✓ Extraction complete")
            st.success(
                f"✓ Extracted {len(inspection_data.get('images', []))} inspection images "
                f"and {len(thermal_data.get('images', []))} thermal images"
            )

        # Step 2: Analyze with Claude API
        with st.spinner("🤖 Analyzing with Claude API..."):
            progress_bar.progress(60, text="🤖 Structuring DDR...")
            try:
                ddr_data, insp_imgs, therm_imgs, area_mapping = process_documents(
                    inspection_data, thermal_data, api_key=api_key
                )
                progress_bar.progress(80, text="✓ Analysis complete")
                areas_mapped = len(area_mapping) if area_mapping else 0
                st.success(f"✓ DDR structure generated successfully ({areas_mapped} areas mapped)")
            except KeyError as e:
                st.error(f"❌ API Key error: {e}. Ensure `Anthropic_API_Key` is set correctly.")
                st.stop()
            except Exception as e:
                st.error(f"❌ Processing error: {e}")
                st.stop()

        # Step 3: Generate report
        with st.spinner("📝 Generating DOCX report..."):
            progress_bar.progress(90, text="📝 Generating report...")
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    output_docx = Path(tmpdir) / "DDR_Report.docx"
                    generate_docx(ddr_data, insp_imgs, therm_imgs, str(output_docx))

                    # Read the generated file
                    with open(output_docx, "rb") as f:
                        report_bytes = f.read()

                    st.session_state.report_generated = True
                    st.session_state.output_file = report_bytes

                    progress_bar.progress(100, text="✓ Report ready!")
                    st.success("✓ Report generated successfully!")
            except Exception as e:
                st.error(f"❌ Report generation error: {e}")
                st.stop()

    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
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

# Catch any unhandled exceptions for debugging
if __name__ == "__main__":
    pass  # Streamlit runs this file directly
