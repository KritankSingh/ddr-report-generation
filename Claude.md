# CLAUDE.md — DDR Report Generation System

## Project Overview

This system reads raw site inspection documents (Inspection Report + Thermal Report) and generates a structured, client-ready **Detailed Diagnostic Report (DDR)**. The output must be accurate, well-organised, and free of invented facts.

---

## Task Summary

| Item | Detail |
|------|--------|
| Input | Inspection Report (PDF) + Thermal Report with images (PDF) |
| Output | Structured DDR report (PDF or DOCX) with embedded images |
| Core Challenge | Merge two imperfect documents logically, handle missing/conflicting data |

---

## Required DDR Output Structure

The generated report **must** contain these seven sections, in order:

1. **Property Issue Summary** — High-level overview of all findings
2. **Area-wise Observations** — Per-location breakdown with supporting images
3. **Probable Root Cause** — Inferred causes based on evidence in the documents
4. **Severity Assessment** — Rating (Critical / High / Medium / Low) with written reasoning
5. **Recommended Actions** — Clear, actionable steps for the client
6. **Additional Notes** — Anything relevant not captured above
7. **Missing or Unclear Information** — Explicitly state `"Not Available"` for any gaps

---

## Extraction Rules

### Text Extraction
- Extract all observations from both documents
- Merge overlapping observations logically — **do not duplicate**
- If the same issue appears in both documents with conflicting details → note the conflict explicitly, present both versions
- If data is absent → write `"Not Available"` — never invent or infer beyond what is stated

### Image Extraction
- Extract images directly from source PDFs (use `pdfplumber`, `PyMuPDF`, or equivalent)
- Place each image **under the relevant area-wise observation** in the DDR
- Only include images that are directly relevant to a finding
- If an expected image is missing → write `"Image Not Available"` in that section

---

## Processing Pipeline

```
[Inspection Report PDF] ──┐
                           ├──► [Extraction Layer] ──► [Merge & Deduplicate] ──► [DDR Generator] ──► [Final Report]
[Thermal Report PDF]    ──┘
```

### Step-by-step

1. **Parse both PDFs** — extract text blocks and images with page/location metadata
2. **Classify observations** — map each finding to an area/location if mentioned
3. **Merge documents** — combine related findings, flag conflicts, drop duplicates
4. **Assess severity** — apply a consistent rubric (see below)
5. **Generate report** — structure into DDR format with images placed contextually
6. **Flag gaps** — populate Section 7 with anything missing or unclear

---

## Severity Rubric

Use this consistent scale when assessing issues:

| Level | Criteria |
|-------|----------|
| **Critical** | Immediate safety risk or structural failure likely |
| **High** | Significant damage requiring urgent attention |
| **Medium** | Moderate issue, action needed within weeks |
| **Low** | Minor, cosmetic, or monitor-only |

Always include a one-sentence reasoning for each severity rating.

---

## Language & Tone Guidelines

- Write in **plain, client-friendly English** — avoid jargon
- Use short sentences and active voice
- Do not include internal system notes or model commentary in the output
- Tables and bullet points are preferred for observations and actions

---

## Conflict Handling

If the Inspection Report and Thermal Report disagree on the same data point:

```
⚠️ Conflict Noted: The Inspection Report states [X], while the Thermal Report indicates [Y].
Further verification is recommended.
```

---

## Missing Data Handling

For any field where information is absent:

- Text field → `"Not Available"`
- Image field → `"Image Not Available"`
- Never leave a section blank or omit it from the output

---

## Generalisation Requirement

The system must work on **any similar inspection + thermal report pair**, not just the provided samples. Avoid hardcoding area names, issue types, or thresholds. All extraction must be document-driven.

---

## Suggested Tech Stack

| Layer | Options |
|-------|---------|
| PDF parsing | `PyMuPDF (fitz)`, `pdfplumber` |
| Image extraction | `PyMuPDF` (renders pages, extracts embedded images) |
| LLM for structuring | Anthropic Claude API (`claude-sonnet-4-20250514`) |
| Report output | `python-docx` (DOCX) or `reportlab` / `fpdf2` (PDF) |
| Orchestration | Python script or LangChain/LlamaIndex pipeline |

---

## Evaluation Checklist (Self-Review Before Submission)

- [ ] All seven DDR sections present
- [ ] No invented facts — every claim traceable to a source document
- [ ] Conflicts explicitly flagged, not silently resolved
- [ ] Missing data marked `"Not Available"` / `"Image Not Available"`
- [ ] Images placed under the correct area-wise observation
- [ ] No duplicate observations
- [ ] Severity rating includes written reasoning
- [ ] Language is plain and client-friendly
- [ ] System works on a new, unseen inspection document pair

---

## Submission Checklist

- [ ] Working output: live link / repo / screenshots
- [ ] Loom video (3–5 min): what you built, how it works, limitations, improvements
- [ ] GitHub repository link
- [ ] All files in a Google Drive folder named with your full name
- [ ] Single Google Drive folder link submitted
