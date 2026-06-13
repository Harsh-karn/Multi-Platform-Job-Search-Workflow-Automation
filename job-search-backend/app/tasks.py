from celery import Celery
import asyncio
from app.models import ResumeProfile
from app.scrapers.jobicy_scraper import search_jobicy
from app.scrapers.adzuna_scraper import search_adzuna
from app.scrapers.google_jobs_scraper import search_google_jobs
from app.scrapers.naukri_scraper import search_naukri
from app.services.aggregator import aggregate
from app.services.ranker import rank_jobs

# Configure Celery
# Use Redis as broker and backend
# Ensure Redis is running locally on default port 6379
celery_app = Celery(
    "job_search_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

# In-memory store for demo purposes. 
# In a real app, you'd store this in Redis or a DB because celery workers are separate processes.
# For simplicity, we will just return the result to the backend.
results_store = {}

@celery_app.task(name="process_job_search")
def process_job_search(session_id: str, profile_dict: dict):
    # Run the async code in a synchronous celery task
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    result = loop.run_until_complete(_run_scrapers_async(session_id, profile_dict))
    return result

async def _run_scrapers_async(session_id: str, profile_dict: dict):
    try:
        profile = ResumeProfile(**profile_dict)
        
        # Fan out to all scrapers concurrently
        jobicy_jobs, adzuna_jobs, google_jobs, naukri_jobs = await asyncio.gather(
            search_jobicy(profile_dict),
            search_adzuna(profile_dict),
            search_google_jobs(profile_dict),
            search_naukri(profile_dict),
            return_exceptions=True   # don't fail if one scraper errors
        )
        
        # Filter out exceptions from results
        all_lists = []
        for jobs in [jobicy_jobs, adzuna_jobs, google_jobs, naukri_jobs]:
            if isinstance(jobs, list):
                all_lists.append(jobs)
            else:
                print(f"Scraper error: {jobs}")
                
        # Aggregate + deduplicate
        merged = aggregate(all_lists)
        
        # AI rank
        ranked = rank_jobs(merged, profile)
        
        return {
            "status": "done",
            "total": len(ranked),
            "jobs": [j.model_dump() for j in ranked]
        }
    except Exception as e:
        print(f"Pipeline error: {e}")
        return {"status": "error", "detail": str(e)}
