# SmartResumeAI — Resume Analyzer & Job Matcher

A local AI-powered resume analyzer built with open-source tools.

## What this project does
- Uploads a resume PDF and accepts a job description text or file
- Extracts resume content locally with `PyMuPDF`
- Uses `sentence-transformers` embeddings for similarity and match scoring
- Detects skills, matched skills, and missing skills
- Generates a downloadable PDF report with strengths and improvements
- Supports a Streamlit UI and optional FastAPI endpoints

## Project structure
- `streamlit_app.py` — Streamlit frontend for interactive analysis
- `fastapi_app.py` — API endpoints for remote analysis and report generation
- `resume_analyzer/pdf_parser.py` — PDF text extraction and English detection
- `resume_analyzer/analyzer.py` — match scoring, skill gap detection, and heuristics
- `resume_analyzer/report.py` — PDF report generation
- `samples/` — sample resume / job description text files

## Install dependencies
```bash
pip install -r requirements.txt
```

## Run the app locally
```bash
streamlit run streamlit_app.py
```

## Run the API server locally
```bash
uvicorn fastapi_app:app --reload
```

## Notes on local behavior
- The analyzer runs fully locally using open-source models only.
- `sentence-transformers` downloads a model on first run, then uses cached local files.
- The app handles missing inputs, invalid PDF content, short resumes / job descriptions, and duplicate analysis of the same data.

## Sample inputs
- `samples/resume_sample.txt`
- `samples/job_description_sample.txt`

## How to test edge cases
- Upload a corrupted or non-PDF file to simulate parsing failure
- Provide an extremely short resume (name + contact) to see a warning
- Paste a very short job description to see score handling for vague JD
- Refresh the page during processing to preserve warnings and cached analysis via session state

## Recommended evaluation metrics
- Match score (0–100)
- Similarity score (embedding cosine similarity)
- Skill coverage ratio
- Resume and job description lengths

## Deployment
This project is designed to run on a local machine with Python and can be deployed on any system that supports Streamlit or FastAPI.
