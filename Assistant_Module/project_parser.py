import os
import json
import google.generativeai as genai

def parse_project_description(text):
    """
    Calls the Gemini API to extract structured electrical design parameters
    from an English or Arabic natural language description of a building project.
    
    Returns a dictionary matching the required schema, or raises/returns default schema on failure.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {
            "error": "GEMINI_API_KEY is not set in environment variables.",
            "building_type": None,
            "rooms": None,
            "ac_units": None,
            "lighting_points": None,
            "socket_outlets": None,
            "kitchen": None,
            "future_equipment": {
                "generators": None,
                "elevators": None,
                "pumps": None,
                "industrial_machines": None,
                "solar_systems": None
            }
        }

    genai.configure(api_key=api_key)
    # Using gemini-flash-lite-latest as it is fast and suitable for extraction
    model = genai.GenerativeModel('gemini-flash-lite-latest')

    prompt = f"""
You are a precise structured data extraction engine for an electrical engineering assistant.
Your task is to extract building parameters from the user's natural language project description (which could be in English or Arabic).

### RULES:
1. Return ONLY a raw JSON object string matching the SCHEMA below.
2. DO NOT wrap the output in markdown block code syntax (such as ```json ... ```).
3. Do not include any explanations, warnings, introductions, or trailing text.
4. Extract only the quantities explicitly mentioned or clearly implied by context.
5. If a property is not mentioned, set its value to null.
6. Translate all Arabic terms to the corresponding English values in the schema (e.g., "فيلا" -> "villa", "شقة" -> "apartment", "مطبخ" -> true).
7. Never perform any electrical calculations (do not estimate current, cable sizes, MCBs, or voltage drops).
8. Handle Arabic dual form words correctly (e.g. "تكييفين" or "جهازين تكييف" -> 2 ac_units; "غرفتين" -> 2 rooms).

### SCHEMA:
{{
  "building_type": "apartment" | "villa" | "office" | "shop" | "warehouse" | "hospital" | "school" | null,
  "rooms": int | null,
  "ac_units": int | null,
  "lighting_points": int | null,
  "socket_outlets": int | null,
  "kitchen": bool | null,
  "future_equipment": {{
    "generators": int | null,
    "elevators": int | null,
    "pumps": int | null,
    "industrial_machines": int | null,
    "solar_systems": bool | null
  }}
}}

### USER INPUT DESCRIPTION:
"{text}"
"""

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up in case the model ignored constraints and wrapped it in markdown code blocks
        if response_text.startswith("```"):
            lines = response_text.splitlines()
            if lines[0].startswith("```json") or lines[0].startswith("```"):
                response_text = "\n".join(lines[1:-1]).strip()
        
        data = json.loads(response_text)
        return data
    except Exception as e:
        return {
            "error": f"Failed to parse description: {str(e)}",
            "building_type": None,
            "rooms": None,
            "ac_units": None,
            "lighting_points": None,
            "socket_outlets": None,
            "kitchen": None,
            "future_equipment": {
                "generators": None,
                "elevators": None,
                "pumps": None,
                "industrial_machines": None,
                "solar_systems": None
            }
        }
