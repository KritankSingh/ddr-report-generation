"""Process extracted documents using Claude API and structure into DDR format."""
import json
import os
from anthropic import Anthropic

SYSTEM_PROMPT = """You are an expert in analyzing property inspection and thermal reports.
Generate a structured Detailed Diagnostic Report (DDR) as valid JSON with this exact structure:
{
  "property_issue_summary": "High-level overview (2-3 sentences)",
  "area_observations": [
    {
      "area": "Location name",
      "findings": "Detailed observations",
      "severity": "Critical | High | Medium | Low",
      "severity_reason": "One sentence explaining severity",
      "thermal_image_references": "Thermal findings or 'None available'",
      "thermal_image_indices": [0, 1]
    }
  ],
  "probable_root_causes": "Inferred causes based on evidence",
  "severity_assessment": {
    "overall_level": "Critical | High | Medium | Low",
    "reasoning": "Explanation"
  },
  "recommended_actions": ["Action 1", "Action 2"],
  "additional_notes": "Relevant context",
  "missing_or_unclear_info": ["Missing data point 1"]
}

RULES:
1. Only use facts from the documents. Never invent.
2. Mark missing data as "Not Available" in missing_or_unclear_info.
3. Severity: Critical=immediate safety risk, High=urgent, Medium=weeks, Low=minor.
4. Assign different thermal_image_indices to different areas.
5. Use plain client-friendly language.
6. Output ONLY the JSON, no explanation text."""


def process_documents(inspection_data, thermal_data, api_key=None):
    """Process inspection and thermal data using Claude API."""
    if api_key is None:
        api_key = os.getenv("Anthropic_API_Key")
    if not api_key:
        raise ValueError("Anthropic API key not found")

    client = Anthropic(api_key=api_key)

    # Keep input small to avoid timeouts
    inspection_text = inspection_data['text'][:5000]
    thermal_text = thermal_data['text'][:2000]
    num_thermal_images = len(thermal_data.get('images', []))

    user_message = f"""Analyze these property inspection documents and generate a DDR JSON.

INSPECTION REPORT:
{inspection_text}

THERMAL REPORT:
{thermal_text}

THERMAL IMAGES AVAILABLE: {num_thermal_images} images (indices 0-{max(0, num_thermal_images-1)})
Assign different thermal_image_indices to each area. Use empty [] if none apply.

Return ONLY valid JSON, no other text."""

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=3000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}]
        )
    except Exception as e:
        raise RuntimeError(f"Claude API call failed: {str(e)}")

    response_text = message.content[0].text

    # Strip markdown code blocks
    cleaned = response_text.strip()
    for prefix in ['```json', '```']:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):]
    if cleaned.endswith('```'):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    # Extract JSON
    try:
        start = cleaned.find('{')
        end = cleaned.rfind('}') + 1
        if start >= 0 and end > start:
            ddr_data = json.loads(cleaned[start:end])
        else:
            raise ValueError("No JSON found")
    except json.JSONDecodeError:
        ddr_data = {
            "property_issue_summary": "Unable to parse response",
            "area_observations": [],
            "probable_root_causes": "Not Available",
            "severity_assessment": {"overall_level": "Medium", "reasoning": "Parse error"},
            "recommended_actions": [],
            "additional_notes": "Parsing fallback used",
            "missing_or_unclear_info": ["Complete structured analysis"]
        }

    return (
        ddr_data,
        inspection_data.get('images', []),
        thermal_data.get('images', []),
        inspection_data.get('area_to_images', {})
    )