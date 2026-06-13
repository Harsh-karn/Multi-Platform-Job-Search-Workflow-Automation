import httpx
import os
import hashlib
from app.models import JobListing

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

async def search_adzuna(profile: dict, num_results: int = 20) -> list[JobListing]:
    jobs = []
    
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        # print("Adzuna credentials not found.")
        return jobs
        
    query = " ".join(profile.get("roles", [])[:1] + profile.get("skills", [])[:2])
    location = profile.get("location", "India")
    
    # We use the 'in' country code for India by default, or could be made dynamic
    url = f"https://api.adzuna.com/v1/api/jobs/in/search/1"
    
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": num_results,
        "what": query,
        "where": location
    }
    
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"Adzuna API error: {e}")
            return []
            
    for item in data.get("results", []):
        jobs.append(JobListing(
            id=hashlib.md5(str(item.get("id")).encode()).hexdigest(),
            title=item.get("title"),
            company=item.get("company", {}).get("display_name"),
            location=item.get("location", {}).get("display_name", ""),
            description=item.get("description", ""),
            apply_url=item.get("redirect_url"),
            source="adzuna",
            posted_date=item.get("created"),
            salary=str(item.get("salary_max", ""))
        ))
        
    return jobs
