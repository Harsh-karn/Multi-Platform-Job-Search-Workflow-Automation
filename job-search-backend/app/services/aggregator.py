from app.models import JobListing

def aggregate(all_lists: list[list[JobListing]]) -> list[JobListing]:
    seen = {}
    for job_list in all_lists:
        if not job_list:
            continue
            
        for job in job_list:
            # Dedup key: normalized title + company
            key = f"{job.title.lower().strip()}::{job.company.lower().strip()}"
            if key not in seen:
                seen[key] = job
            else:
                # If dupe exists, prefer the one with a direct apply link (not google redirect)
                existing = seen[key]
                if "google.com" not in job.apply_url and "google.com" in existing.apply_url:
                    seen[key] = job
    return list(seen.values())
