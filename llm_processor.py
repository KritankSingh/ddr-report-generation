"""Process extracted documents using Claude API and structure into DDR format."""
import json
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("Anthropic_API_Key"))

# System prompt for DDR generation
SYSTEM_PROMPT = """You are an expert in analyzing property inspection and thermal reports.
Your task is to generate a structured Detailed Diagnostic Report (DDR) with 7 sections.

**Your output MUST be valid JSON** with this exact structure:
{
  "property_issue_summary": "High-level overview of all findings (2-3 sentences)",
  "area_observations": [
    {
      "area": "Location name (e.g., 'Hall Skirting', 'Master Bedroom')",
      "findings": "Detailed observations for this area",
      "severity": "Critical | High | Medium | Low",
      "severity_reason": "One sentence explaining the severity rating",
      "thermal_image_references": "Brief note on which thermal findings apply here, or 'None available'",
      "thermal_image_indices": [0, 1, 2]
    }
  ],
  "probable_root_causes": "Inferred causes based on evidence",
  "severity_assessment": {
    "overall_level": "Critical | High | Medium | Low",
    "reasoning": "Explanation of the overall severity"
  },
  "recommended_actions": [
    "Action 1",
    "Action 2"
  ],
  "additional_notes": "Anything relevant not covered above",
  "missing_or_unclear_info": [
    "Missing data point 1",
    "Missing data point 2"
  ]
}

**CRITICAL RULES:**
1. Extract ONLY what is explicitly stated in the documents. Do NOT invent facts.
2. If data is absent, list it in "missing_or_unclear_info", not in sections.
3. Use "Not Available" for any section where no information exists.
4. Severity ratings (Critical/High/Medium/Low):
   - Critical: Immediate safety risk or structural failure likely
   - High: Significant damage requiring urgent attention
   - Medium: Moderate issue, action needed within weeks
   - Low: Minor, cosmetic, or monitor-only
5. Always include a one-sentence reasoning for each severity rating.
6. If documents conflict on the same issue, explicitly state both versions in findings.
7. Deduplicate: if the same issue appears in both documents, mention it once with "confirmed in both reports".
8. Use plain, client-friendly language. Avoid jargon.
9. Keep findings concise but complete.

**THERMAL IMAGE MAPPING:**
10. For each area_observation, identify which thermal images are relevant (if any).
11. thermal_image_indices should be an array of zero-based image indices from the thermal PDF.
    Example: thermal_image_indices: [0, 2, 5] means use thermal images 0, 2, and 5 for this area.
12. If no thermal images correlate to an area, use thermal_image_indices: [] (empty array).
13. Look for references to specific thermal image numbers/names in the thermal report.
14. If the thermal report has named images (e.g., "RB02380X.JPG"), extract the index based on page order.
15. Never assign the same image index to multiple areas unless explicitly stated.
16. Each area should get DIFFERENT thermal images (not repeating the same image).
"""

def process_documents(inspection_data, thermal_data):
    """
    Process extracted inspection and thermal report data using Claude API.

    Args:
        inspection_data: dict with 'text' and 'images' from inspection PDF
        thermal_data: dict with 'text' and 'images' from thermal PDF

    Returns:
        dict with structured DDR content
    """
    # Prepare image metadata for reference
    thermal_image_info = ""
    if thermal_data['images']:
        thermal_image_info = "\n\n**THERMAL IMAGES EXTRACTED:** (total " + str(len(thermal_data['images'])) + " images)\n"
        thermal_image_info += "These are indexed 0-" + str(len(thermal_data['images']) - 1) + " based on their order in the PDF.\n"
        thermal_image_info += "Map each area_observation to relevant thermal_image_indices from this list.\n"

    # Prepare the user message with both documents
    user_message = f"""Please analyze these two property inspection documents and generate a DDR.

**INSPECTION REPORT:**
{inspection_data['text'][:8000]}

**THERMAL REPORT:**
{thermal_data['text'][:4000]}
{thermal_image_info}

IMPORTANT FOR IMAGE MAPPING:
- For each area in area_observations, assign thermal_image_indices (array of numbers)
- Use indices 0-{len(thermal_data['images']) - 1} to reference the thermal images
- Each area should reference DIFFERENT images (not the same image repeated)
- Use empty array [] if no thermal images apply to an area

Now generate the complete JSON DDR structure as specified."""

    print("Calling Claude API for DDR structuring...")
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,  # Increased to handle large DDRs with many area observations
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )

    # Parse the JSON response
    response_text = message.content[0].text
    print(f"[DEBUG] Raw LLM response:\n{response_text}\n")

    # Try to extract JSON from response
    try:
        # Strip markdown code blocks (```json ... ```)
        cleaned_text = response_text.strip()
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]  # Remove ```json
        elif cleaned_text.startswith('```'):
            cleaned_text = cleaned_text[3:]  # Remove ```

        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]  # Remove trailing ```

        cleaned_text = cleaned_text.strip()

        # Look for JSON block in response
        json_start = cleaned_text.find('{')
        json_end = cleaned_text.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = cleaned_text[json_start:json_end]
            ddr_data = json.loads(json_str)
        else:
            raise ValueError("No JSON found in response")
    except json.JSONDecodeError as e:
        print(f"ERROR: Could not parse JSON response: {e}")
        print(f"Cleaned text: {cleaned_text[:500]}")
        # Return a fallback structure
        ddr_data = {
            "property_issue_summary": response_text[:200],
            "area_observations": [],
            "probable_root_causes": "Not Available",
            "severity_assessment": {"overall_level": "Medium", "reasoning": "Unable to parse response"},
            "recommended_actions": [],
            "additional_notes": "Generated with parsing fallback",
            "missing_or_unclear_info": ["Complete structured analysis"]
        }

    return ddr_data, inspection_data['images'], thermal_data['images']
