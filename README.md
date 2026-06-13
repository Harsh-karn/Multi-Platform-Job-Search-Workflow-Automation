# Multi-Platform Job Search Workflow Automation

This project is an AI-powered, full-stack workflow automation system designed to streamline the job search process. It accepts a candidate's resume, uses Gemini AI to extract key profile information (skills, roles, experience), and then asynchronously scrapes and aggregates job listings from multiple platforms. Finally, the AI ranks the matched jobs based on how well they fit the candidate's profile.

## Features

- **Resume Parsing**: Uses Google Gemini API to extract structured candidate data from uploaded resumes.
- **Multi-Platform Aggregation**: Searches for jobs across:
  - **Google Jobs** (Direct structured data extraction)
  - **Naukri** (Headless browser scraping via Playwright)
  - **Jobicy** (Remote tech jobs via Free API)
  - **Adzuna** (Global job data via API)
- **Asynchronous Processing**: Utilizes Celery and Redis to handle concurrent scraping without blocking the backend API.
- **AI Ranking**: Gemini AI evaluates each job description against the candidate's profile to generate a match score (0-100%).
- **Modern UI**: A responsive, dark-themed Next.js frontend built with Tailwind CSS and Lucide icons.

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js (App Router), React, Tailwind CSS |
| **Backend API** | FastAPI (Python) |
| **AI / LLM** | Google Gemini 2.5 Pro (`google-genai`) |
| **Task Queue** | Celery |
| **Broker / Cache** | Redis |
| **Scraping** | Playwright, BeautifulSoup4, HTTPX |

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **Redis Server** (Running locally on default port `6379`)
- **API Keys**:
  - `GEMINI_API_KEY`: For resume parsing and job ranking.
  - `ADZUNA_APP_ID` & `ADZUNA_APP_KEY`: For Adzuna API job fetching (Optional, but recommended).

## Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/Harsh-karn/Multi-Platform-Job-Search-Workflow-Automation.git
cd Multi-Platform-Job-Search-Workflow-Automation
```

### 2. Backend Setup
```bash
cd job-search-backend

# Create and activate a virtual environment
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
# Alternatively, if requirements.txt is missing:
# pip install fastapi uvicorn celery redis google-genai httpx playwright beautifulsoup4 python-multipart pydantic

# Install Playwright browsers (required for Naukri scraper)
playwright install chromium
```

### 3. Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install
# or
yarn install
```

## Running the Application Locally

You will need three separate terminal windows running concurrently.

**Terminal 1: Redis Server**
Make sure your Redis server is running. If installed locally on Windows via WSL or Docker:
```bash
redis-server
```

**Terminal 2: FastAPI Backend**
```bash
cd job-search-backend
.\venv\Scripts\activate

# Set Environment Variables
# Windows PowerShell
$env:GEMINI_API_KEY="your-gemini-key"
$env:ADZUNA_APP_ID="your-adzuna-id"
$env:ADZUNA_APP_KEY="your-adzuna-key"

# Linux/Mac
export GEMINI_API_KEY="your-gemini-key"
export ADZUNA_APP_ID="your-adzuna-id"
export ADZUNA_APP_KEY="your-adzuna-key"

# Start the server
uvicorn app.main:app --reload
```
*API will run at http://localhost:8000*

**Terminal 3: Celery Worker**
```bash
cd job-search-backend
.\venv\Scripts\activate

# Set the same environment variables as above

# Start Celery worker (Windows usually requires --pool=solo)
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
```

**Terminal 4: Next.js Frontend**
```bash
cd frontend

# Start the development server
npm run dev
```
*Frontend will run at http://localhost:3000*

## How it Works
1. Navigate to the frontend (http://localhost:3000).
2. Upload a `.txt`, `.pdf`, or `.docx` resume file.
3. The frontend sends the file to the FastAPI `/search` endpoint.
4. FastAPI parses the text using Gemini, creates a background Celery task, and returns a `task_id`.
5. The frontend polls the `/results/{task_id}` endpoint every 3 seconds.
6. Meanwhile, the Celery worker concurrently spins up the Playwright scrapers and API requests to fetch jobs.
7. Jobs are deduplicated, passed to Gemini for match scoring, and saved in Celery's Redis result backend.
8. The frontend receives the `done` status and renders the job cards sorted by the highest match score.
