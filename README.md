# DDR Generation System

**AI-powered Detailed Diagnostic Report (DDR) generator** that automatically analyzes property inspection PDFs and creates professional 7-section diagnostic reports.

## Quick Start

```bash
python main.py "inspection.pdf" "thermal.pdf" "output.docx"
```

## What This Does

Reads two property inspection documents (Inspection Report + Thermal Images) and generates a comprehensive diagnostic report with:

✅ Property issue summary
✅ Area-wise observations with thermal images
✅ Root cause analysis
✅ Severity assessment
✅ Recommended remediation actions
✅ Explicit data gap documentation

## Example Output

See **`DDR_Final.docx`** for a complete example report.

## Documentation

- **[QUICK_START.md](QUICK_START.md)** — 30-second guide to get running
- **[SYSTEM_SUMMARY.md](SYSTEM_SUMMARY.md)** — Complete technical overview
- **[DDR_README.md](DDR_README.md)** — Detailed feature documentation

## System Files

- **main.py** — Entry point (run this)
- **extractor.py** — PDF text/image extraction
- **llm_processor.py** — Claude AI integration
- **report_generator.py** — DOCX report generation

## Setup

```bash
uv sync
```

Add API key to `.env`:
```
Anthropic_API_Key = REDACTED Usage

```bash
# Basic usage (outputs to DDR_Report.docx)
python main.py "Sample Report.pdf" "Thermal Images.pdf"

# Custom output filename
python main.py "report1.pdf" "thermal1.pdf" "my_report.docx"
```

## Key Features

- **Automated** — No manual data entry
- **Intelligent** — Deduplicates findings, detects conflicts
- **Generalized** — Works on any inspection document pair
- **Professional** — Client-ready DOCX with embedded images
- **Traceable** — All claims verified against source documents

## Technology

- **LLM:** Claude Haiku 4.5 (fast, cost-efficient)
- **PDF Parsing:** PyMuPDF (fitz)
- **Report Generation:** python-docx
- **Orchestration:** Python 3.14+

## Performance

- ⏱ **Execution:** ~1 minute per report
- 💰 **Cost:** < $0.02 USD per report
- 📊 **Scale:** Process hundreds of reports daily

## For Questions

Refer to the documentation files or review the example output in `DDR_Final.docx`.

---

**Status:** ✅ Production-Ready | **Version:** 1.0 | **Last Updated:** 2026-03-31
