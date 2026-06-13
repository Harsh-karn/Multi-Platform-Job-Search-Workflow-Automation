from pydantic import BaseModel
from typing import Optional, List

class JobListing(BaseModel):
    id: str
    title: str
    company: str
    location: str
    salary: Optional[str] = None
    description: Optional[str] = None
    apply_url: str
    source: str           # "linkedin", "naukri", "indeed", "google_jobs", "jobicy", etc.
    posted_date: Optional[str] = None
    match_score: Optional[float] = None  # filled by ranker

class ResumeProfile(BaseModel):
    roles: List[str]
    skills: List[str]
    experience_years: int
    location: str
    remote_ok: bool
    salary_min: Optional[int] = None
