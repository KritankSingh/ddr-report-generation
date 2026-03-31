# Detailed Diagnostic Report (DDR) Generation System

An AI-powered pipeline that reads two property inspection documents (Inspection Report + Thermal Report PDFs) and generates a structured, client-ready DDR with 7 mandatory sections and embedded images.

## Overview

```
[Inspection Report PDF] ──┐
                           ├──► Extraction ──► LLM Structuring ──► Report Generation ──► DDR.docx
[Thermal Report PDF]    ──┘
```

## Features

✓ **Automatic PDF parsing** — extracts text and images from both documents
✓ **LLM-powered structuring** — uses Claude API to organize findings into 7 sections
✓ **Intelligent deduplication** — merges overlapping observations, avoids duplicates
✓ **Conflict detection** — explicitly flags disagreements between documents
✓ **Image embedding** — places thermal images under relevant observations
✓ **Missing data handling** — marks gaps as "Not Available" rather than omitting
✓ **Severity assessment** — applies consistent rubric (Critical/High/Medium/Low)
✓ **Client-friendly output** — plain language, no jargon

## Installation

Dependencies are already in `pyproject.toml`. Install with:

```bash
uv add pymupdf python-docx reportlab anthropic
```

Or use:

```bash
uv sync
```

## Configuration

### .env File
Ensure your `.env` contains a valid Anthropic API key:

```
Anthropic_API_Key = REDACTED Usage

### Basic Command

```bash
python main.py <inspection_pdf> <thermal_pdf> [output.docx]
```

### Example

```bash
python main.py "Sample Report.pdf" "Thermal Images.pdf" "DDR_Output.docx"
```

**Arguments:**
- `inspection_pdf` — Path to the Inspection Report PDF (required)
- `thermal_pdf` — Path to the Thermal Report PDF (required)
- `output.docx` — Output file name (optional, defaults to `DDR_Report.docx`)

### Output Format

The generated DOCX contains 7 sections:

1. **Property Issue Summary** — High-level overview of all findings
2. **Area-wise Observations** — Per-location breakdown with thermal images
3. **Probable Root Cause** — Inferred causes based on evidence
4. **Severity Assessment** — Overall rating with reasoning
5. **Recommended Actions** — Actionable steps for the client
6. **Additional Notes** — Relevant information not captured above
7. **Missing or Unclear Information** — Explicitly listed gaps

## System Architecture

### Modules

**extractor.py**
- Parses PDF files using PyMuPDF (fitz)
- Extracts text blocks with page numbers
- Extracts embedded images with metadata
- Returns structured dict with text and image bytes

**llm_processor.py**
- Sends extracted text to Claude API
- System prompt defines DDR structure and rules
- Handles JSON parsing of structured output
- Maps findings to severity levels using rubric
- Returns structured DDR dict

**report_generator.py**
- Converts DDR dict to DOCX using python-docx
- Follows pattern from `.claude/Skills/docx.md`
- Embeds thermal images under observations
- Handles missing data gracefully

**main.py**
- CLI entry point
- Orchestrates extraction → LLM → report generation
- Loads environment variables
- Prints progress to console

## Severity Rubric

The system applies this rubric consistently:

| Level | Criteria |
|-------|----------|
| **Critical** | Immediate safety risk or structural failure likely |
| **High** | Significant damage requiring urgent attention |
| **Medium** | Moderate issue, action needed within weeks |
| **Low** | Minor, cosmetic, or monitor-only |

Each severity rating includes a one-sentence explanation.

## Key Rules

### Data Extraction
- **Extract only what is stated** — no invented facts
- **Mark gaps explicitly** — "Not Available" for missing data
- **Deduplicate intelligently** — if same issue in both docs, list once with "confirmed in both reports"
- **Flag conflicts** — if documents disagree, show both versions with ⚠️

### Language & Tone
- Plain, client-friendly English
- Short sentences, active voice
- No jargon or internal system notes
- Bullet points preferred for lists

### Image Handling
- Images placed under relevant area observations
- Missing images marked "Image Not Available"
- Each thermal image context explained

## Technical Details

**LLM Model:** `claude-haiku-4-5-20251001` (fast, cost-effective)

**PDF Parsing:** PyMuPDF (fitz) — handles text and embedded images

**Output Format:** DOCX (Microsoft Word format, widely compatible)

**Optional:** Use `.claude/Skills/pdf.md` pattern to generate PDF output with reportlab instead

## Workflow Example

```bash
# 1. Place your PDFs in the project directory
cp ~/Downloads/Sample\ Report.pdf .
cp ~/Downloads/Thermal\ Images.pdf .

# 2. Run the pipeline
python main.py "Sample Report.pdf" "Thermal Images.pdf" "Final_DDR.docx"

# 3. Check the output
open Final_DDR.docx  # or use your document viewer
```

## Troubleshooting

**Error: "PDF not found"**
- Ensure both input files exist in the current directory
- Check file names (case-sensitive on Linux/Mac)

**Error: "Anthropic_API_Key not set"**
- Add `Anthropic_API_Key = REDACTED to `.env`
- Reload the terminal session

**Error: "Could not extract image"**
- Some PDFs may have corrupted images — the system gracefully handles this
- Check that images are embedded (not just referenced)

**Output has "Not Available" everywhere**
- Verify input PDFs contain actual content (not scanned images without OCR)
- Check that the PDFs are not encrypted

## Generalization

This system is **not hardcoded** to any specific property or area names. It works on any similar inspection + thermal report pair by:

- Dynamically extracting text and images from input
- Using the LLM to intelligently categorize findings
- Not relying on regex patterns or fixed field names
- Handling various document formats and layouts

## Files in This Project

```
.
├── main.py                 # Entry point
├── extractor.py            # PDF parsing
├── llm_processor.py        # Claude API integration
├── report_generator.py     # DOCX generation
├── test_pipeline.py        # System verification
├── pyproject.toml          # Dependencies
├── .env                    # API key (not in repo)
└── DDR_README.md          # This file
```

## Next Steps

1. Place `Sample Report.pdf` and `Thermal Images.pdf` in this directory
2. Run: `python main.py "Sample Report.pdf" "Thermal Images.pdf"`
3. Open the generated `DDR_Report.docx`
4. Review all 7 sections and verify accuracy

## Support

For issues with:
- **PDF parsing** — check that files are valid PDFs, not corrupted
- **Claude API** — verify API key and rate limits
- **DOCX generation** — ensure write permissions in output directory

## License

This project is part of the "AI Generalist / Applied AI Builder" assignment.
