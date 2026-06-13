import httpx
from app.models import JobListing
import hashlib

async def search_jobicy(profile: dict, num_results: int = 50) -> list[JobListing]:
    jobs = []
    
    # We'll use the first role as the main tag, or fallback to first skill
    tag = ""
    if profile.get("roles"):
        tag = profile["roles"][0]
    elif profile.get("skills"):
        tag = profile["skills"][0]
        
    location = profile.get("location", "")
    
    # Jobicy API v2 for remote jobs
    url = f"https://jobicy.com/api/v2/remote-jobs?count={num_results}"
    if tag:
        url += f"&tag={tag}"
    if location:
        url += f"&location={location}"
        
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"Jobicy API error: {e}")
            return []
            
    for item in data.get("jobs", []):
        jobs.append(JobListing(
            id=hashlib.md5(f"{item.get('jobTitle')}{item.get('companyName')}".encode()).hexdigest(),
            title=item.get("jobTitle"),
            company=item.get("companyName"),
            location=item.get("jobGeo", ""),
            description=item.get("jobDescription", ""),
            apply_url=item.get("url"),
            source="jobicy",
            posted_date=item.get("pubDate"),
            salary=item.get("annualSalaryMax")
        ))
        
    return jobs
