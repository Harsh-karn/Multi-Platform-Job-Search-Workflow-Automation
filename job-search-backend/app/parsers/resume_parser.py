import json
import os
from google import genai
from google.genai import types

PARSE_PROMPT = """
Extract structured data from this resume. Return ONLY valid JSON with these fields:
{
  "roles": ["Backend Developer", "Python Engineer"],
  "skills": ["Python", "FastAPI", "PostgreSQL"],
  "experience_years": 2,
  "location": "Bangalore",
  "remote_ok": true,
  "salary_min": 600000
}
No extra text, no markdown fences.
"""

def parse_resume(text: str) -> dict:
    client = genai.Client()
    # Assuming GEMINI_API_KEY is in the environment
    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents=f"{PARSE_PROMPT}\n\nRESUME:\n{text}",
    )
    
    response_text = response.text
    # Cleanup markdown json formatting if present
    if response_text.startswith("```json"):
        response_text = response_text.strip()[7:-3]
    elif response_text.startswith("```"):
        response_text = response_text.strip()[3:-3]
        
    return json.loads(response_text)
