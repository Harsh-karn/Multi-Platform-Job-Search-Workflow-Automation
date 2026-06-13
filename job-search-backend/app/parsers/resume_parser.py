import json
import httpx

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
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3",
        "prompt": f"{PARSE_PROMPT}\n\nRESUME:\n{text}",
        "stream": False,
        "format": "json"
    }
    
    try:
        response = httpx.post(url, json=payload, timeout=60.0)
        response.raise_for_status()
        result = response.json()
        response_text = result.get("response", "{}")
        
        # Cleanup markdown json formatting if present
        if response_text.startswith("```json"):
            response_text = response_text.strip()[7:-3]
        elif response_text.startswith("```"):
            response_text = response_text.strip()[3:-3]
            
        return json.loads(response_text)
    except Exception as e:
        print(f"Ollama parsing error: {e}")
        # Return fallback empty profile
        return {
            "roles": [],
            "skills": [],
            "experience_years": 0,
            "location": "",
            "remote_ok": True,
            "salary_min": None
        }
