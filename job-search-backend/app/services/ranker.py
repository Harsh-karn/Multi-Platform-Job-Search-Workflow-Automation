import json
from google import genai
from app.models import JobListing, ResumeProfile

def rank_jobs(jobs: list[JobListing], profile: ResumeProfile) -> list[JobListing]:
    if not jobs:
        return []
        
    client = genai.Client()
    
    # Batch score in groups of 10 to save API calls and context length issues
    batches = [jobs[i:i+10] for i in range(0, len(jobs), 10)]
    scored = []
    
    for batch in batches:
        job_list_text = "\n".join([
            f"{i+1}. {j.title} at {j.company} | {j.description[:200] if j.description else 'no description'}"
            for i, j in enumerate(batch)
        ])
        
        prompt = f"""
Score each job 0-100 for match with this candidate profile:
Skills: {', '.join(profile.skills)}
Target roles: {', '.join(profile.roles)}
Experience: {profile.experience_years} years
Location preference: {profile.location}, remote_ok={profile.remote_ok}

Jobs to score:
{job_list_text}

Return ONLY a valid JSON array of numbers representing scores in order: [85, 42, 71]
No markdown formatting, no text, no explanation. Just the JSON array.
"""
        try:
            response = client.models.generate_content(
                model='gemini-2.5-pro',
                contents=prompt,
            )
            
            response_text = response.text
            # Cleanup markdown
            if response_text.startswith("```json"):
                response_text = response_text.strip()[7:-3]
            elif response_text.startswith("```"):
                response_text = response_text.strip()[3:-3]
                
            scores = json.loads(response_text)
            
            # Ensure scores matches batch length
            if len(scores) != len(batch):
                # Fallback if AI hallucinates array length
                print(f"Warning: Scores length ({len(scores)}) does not match batch length ({len(batch)})")
                scores = [50] * len(batch)
                
            for job, score in zip(batch, scores):
                job.match_score = float(score)
                scored.append(job)
                
        except Exception as e:
            print(f"Ranking error: {e}")
            # Give neutral score if ranking fails
            for job in batch:
                job.match_score = 50.0
                scored.append(job)
    
    # Sort by score descending, filter below threshold
    return sorted([j for j in scored if getattr(j, "match_score", 0) >= 50], 
                  key=lambda x: getattr(x, "match_score", 0), reverse=True)
