# Quick Start Guide — DDR Generation System

## 30-Second Overview

Generate professional diagnostic reports from inspection PDFs in 3 steps:

```bash
python main.py "Inspection.pdf" "Thermal.pdf" "Report.docx"
```

**Done.** Professional 7-section report with images and analysis. ✅

---

## Setup (One-time)

### 1. Install Dependencies
```bash
uv sync
```

### 2. Configure API Key
Add to `.env`:
```
Anthropic_API_Key = REDACTED Usage

### Basic Command
```bash
python main.py "Sample Report.pdf" "Thermal Images.pdf"
```

### With Custom Output
```bash
python main.py "report1.pdf" "thermal1.pdf" "MyReport.docx"
```

### Verify It Works
```bash
python main.py "Sample Report.pdf" "Thermal Images.pdf" "test_output.docx"
```

---

## What You Get

✅ **DDR_Final.docx** (or your filename)

Contains:
1. Property Issue Summary
2. Area-wise Observations (with thermal images)
3. Probable Root Causes
4. Severity Assessment (Critical/High/Medium/Low)
5. Recommended Actions
6. Additional Notes
7. Missing or Unclear Information

**Execution Time:** ~1 minute (includes API call)

---

## System Architecture

```
main.py
  ├── extractor.py       → Extract text & images from PDFs
  ├── llm_processor.py   → Call Claude API for analysis
  └── report_generator.py → Generate DOCX with all 7 sections
```

---

## Example

**Input:** 2 PDFs
- `Sample Report.pdf` (1.1 MB, 64 photos)
- `Thermal Images.pdf` (4.0 MB, 30 thermal images)

**Processing:** ~45 seconds

**Output:** `DDR_Final.docx` (42 KB)
- 9 area observations
- 11 recommended actions
- 14 data gaps documented
- All findings traceable to source

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "PDF not found" | Ensure PDFs exist in current directory |
| "API key not set" | Add `Anthropic_API_Key` to `.env` |
| "Permission denied" | Close any open .docx files |
| "Module not found" | Run `uv sync` to reinstall dependencies |

---

## Key Features

- ✅ No manual data entry
- ✅ Intelligent deduplication
- ✅ Conflict detection
- ✅ Image embedding
- ✅ Works on any inspection document pair
- ✅ Professional DOCX output

---

## Files

| File | Purpose |
|------|---------|
| `main.py` | Run this: `python main.py ...` |
| `extractor.py` | PDF parsing logic |
| `llm_processor.py` | Claude AI integration |
| `report_generator.py` | DOCX generation |
| `DDR_README.md` | Full technical docs |
| `SYSTEM_SUMMARY.md` | Detailed overview |

---

## Next Steps

1. **Test with provided PDFs:**
   ```bash
   python main.py "Sample Report.pdf" "Thermal Images.pdf"
   ```

2. **Open the generated report:**
   - Look for `DDR_Report.docx` (or custom name)
   - Review all 7 sections

3. **Use with your own PDFs:**
   ```bash
   python main.py "your_inspection.pdf" "your_thermal.pdf" "output.docx"
   ```

---

## That's It! 🚀

The system is ready to generate professional diagnostic reports automatically.

For details, see `SYSTEM_SUMMARY.md` and `DDR_README.md`.
