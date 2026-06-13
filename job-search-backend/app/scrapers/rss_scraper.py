import httpx
import hashlib
from app.models import JobListing

async def search_rss(profile: dict, num_results: int = 50) -> list[JobListing]:
    """
    Pulls data from open APIs/Feeds like Himalayas (public JSON).
    """
    jobs = []
    
    tag = ""
    if profile.get("roles"):
        tag = profile["roles"][0].lower().replace(" ", "-")
    elif profile.get("skills"):
        tag = profile["skills"][0].lower().replace(" ", "-")
        
    url = f"https://himalayas.app/jobs/api?limit={num_results}"
    
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"Himalayas RSS error: {e}")
            return jobs
            
    for item in data.get("jobs", []):
        # Optional basic filtering by keyword locally since the API isn't purely keyword based
        job_title = item.get("title", "").lower()
        company = item.get("companyName", "")
        
        if tag and tag not in job_title and tag.replace("-", " ") not in job_title:
            # Check skills or categories
            categories = [c.get("name", "").lower() for c in item.get("categories", [])]
            if not any(tag in cat for cat in categories):
                continue
                
        jobs.append(JobListing(
            id=hashlib.md5(f"{item.get('title')}{company}".encode()).hexdigest(),
            title=item.get("title"),
            company=company,
            location=item.get("locationRestrictions", ["Remote"])[0] if item.get("locationRestrictions") else "Remote",
            description=item.get("excerpt", ""),
            apply_url=item.get("applicationLink", item.get("jobUri")),
            source="himalayas (rss)",
            posted_date=str(item.get("pubDate", ""))
        ))
        
    return jobs
