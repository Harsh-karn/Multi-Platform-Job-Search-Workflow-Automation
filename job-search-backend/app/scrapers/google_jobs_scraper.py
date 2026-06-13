import httpx
from bs4 import BeautifulSoup
import json
import hashlib
from app.models import JobListing

async def search_google_jobs(profile: dict) -> list[JobListing]:
    """
    Uses Google Jobs structured data endpoint.
    Returns structured JSON from Google's /search?ibp=htl;jobs endpoint.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    role = profile.get("roles", ["Software Engineer"])[0]
    location = profile.get("location", "")
    query = f"{role} jobs in {location}" if location else f"{role} jobs"
    
    params = {
        "q": query,
        "ibp": "htl;jobs",
        "hl": "en",
        "gl": "in"
    }
    
    jobs = []
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            resp = await client.get(
                "https://www.google.com/search",
                params=params,
                headers=headers
            )
            resp.raise_for_status()
        except Exception as e:
            print(f"Google Jobs scrape error: {e}")
            return jobs

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            # Some tags contain multiple JSON objects or malformed data, we need to handle it
            data_text = tag.string.strip()
            # If it's wrapped in an array, load it
            data_list = json.loads(data_text)
            
            # If it's a single dict, wrap it in a list to iterate
            if isinstance(data_list, dict):
                data_list = [data_list]
                
            for data in data_list:
                if data.get("@type") == "JobPosting":
                    title = data.get("title", "")
                    company = data.get("hiringOrganization", {}).get("name", "")
                    
                    # Prevent empty results
                    if not title:
                        continue
                        
                    jobs.append(JobListing(
                        id=hashlib.md5(f"{title}{company}".encode()).hexdigest(),
                        title=title,
                        company=company,
                        location=data.get("jobLocation", {}).get("address", {}).get("addressLocality", ""),
                        apply_url=data.get("url", ""),
                        description=data.get("description", "")[:500],  # Truncate to save space
                        source="google_jobs",
                        posted_date=data.get("datePosted", "")
                    ))
        except Exception as e:
            continue
            
    return jobs
