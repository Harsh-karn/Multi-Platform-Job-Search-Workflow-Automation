from playwright.async_api import async_playwright
import hashlib
from app.models import JobListing
import urllib.parse

async def search_linkedin(profile: dict) -> list[JobListing]:
    jobs = []
    
    role = profile.get("roles", ["Software Engineer"])[0]
    location = profile.get("location", "India")
    
    encoded_role = urllib.parse.quote(role)
    encoded_location = urllib.parse.quote(location)
    
    url = f"https://www.linkedin.com/jobs/search?keywords={encoded_role}&location={encoded_location}&f_TPR=r604800"
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            await page.goto(url, wait_until="domcontentloaded")
            
            # Wait for job cards to load
            try:
                await page.wait_for_selector(".base-card", timeout=8000)
            except Exception:
                print("LinkedIn: Timeout waiting for job cards. Captcha or no results.")
                await browser.close()
                return jobs
                
            job_elements = await page.query_selector_all(".base-card")
            
            for el in job_elements[:20]:
                try:
                    title_el = await el.query_selector(".base-search-card__title")
                    title = await title_el.inner_text() if title_el else ""
                    
                    company_el = await el.query_selector(".base-search-card__subtitle")
                    company = await company_el.inner_text() if company_el else ""
                    
                    loc_el = await el.query_selector(".job-search-card__location")
                    job_loc = await loc_el.inner_text() if loc_el else location
                    
                    link_el = await el.query_selector("a.base-card__full-link")
                    apply_url = await link_el.get_attribute("href") if link_el else ""
                    
                    # Ensure url has scheme
                    if apply_url and not apply_url.startswith("http"):
                        apply_url = "https://" + apply_url.lstrip("/")
                    
                    if title and apply_url:
                        jobs.append(JobListing(
                            id=hashlib.md5(f"{title}{company}".encode()).hexdigest(),
                            title=title.strip(),
                            company=company.strip(),
                            location=job_loc.strip(),
                            apply_url=apply_url,
                            source="linkedin"
                        ))
                except Exception as e:
                    continue
                    
            await browser.close()
    except Exception as e:
        print(f"LinkedIn Scraper Error: {e}")
        
    return jobs
