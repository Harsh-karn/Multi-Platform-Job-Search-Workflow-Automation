from playwright.async_api import async_playwright
import hashlib
from app.models import JobListing

async def search_naukri(profile: dict) -> list[JobListing]:
    jobs = []
    
    role = profile.get("roles", ["Software Engineer"])[0]
    location = profile.get("location", "")
    
    # Format role and location for Naukri URL
    role_formatted = role.replace(' ', '-').lower()
    location_formatted = location.replace(' ', '-').lower() if location else "india"
    
    url = f"https://www.naukri.com/{role_formatted}-jobs-in-{location_formatted}"
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Use anti-bot measures if possible, here we just set a common user agent
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            await page.goto(url, wait_until="domcontentloaded")
            
            # Wait for job cards to load (with a timeout so we don't hang)
            try:
                # Naukri's job card container class
                await page.wait_for_selector(".srp-jobtuple-wrapper", timeout=10000)
            except Exception:
                # If we timeout, we might have hit a captcha or no results
                print("Naukri: Timeout waiting for job cards.")
                await browser.close()
                return jobs
                
            job_elements = await page.query_selector_all(".srp-jobtuple-wrapper")
            
            for el in job_elements[:20]: # Limit to 20 to avoid spending too much time
                try:
                    title_el = await el.query_selector("a.title")
                    title = await title_el.inner_text() if title_el else ""
                    apply_url = await title_el.get_attribute("href") if title_el else ""
                    
                    company_el = await el.query_selector(".comp-dtls-wrap a.comp-name")
                    company = await company_el.inner_text() if company_el else ""
                    
                    loc_el = await el.query_selector(".locWdth")
                    job_loc = await loc_el.inner_text() if loc_el else location
                    
                    desc_el = await el.query_selector(".job-desc")
                    desc = await desc_el.inner_text() if desc_el else ""
                    
                    if title and apply_url:
                        jobs.append(JobListing(
                            id=hashlib.md5(f"{title}{company}".encode()).hexdigest(),
                            title=title,
                            company=company,
                            location=job_loc,
                            apply_url=apply_url,
                            description=desc,
                            source="naukri"
                        ))
                except Exception as e:
                    continue
                    
            await browser.close()
    except Exception as e:
        print(f"Naukri Scraper Error: {e}")
        
    return jobs
