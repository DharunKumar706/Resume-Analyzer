from fastapi import Body, FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from resume_analyzer.pdf_parser import extract_text_from_pdf, is_english_text
from resume_analyzer.analyzer import analyze_resume_description
from resume_analyzer.report import create_pdf_report
import io

app = FastAPI(title="SmartResumeAI Resume Analyzer API")


@app.post("/analyze")
async def analyze_resume(
    resume_file: UploadFile | None = File(None),
    job_description_text: str = Form(""),
    jd_file: UploadFile | None = File(None),
):
    if resume_file is None and not job_description_text:
        raise HTTPException(status_code=400, detail="Resume and job description are required.")

    if resume_file is None:
        raise HTTPException(status_code=400, detail="Resume file is required.")

    if job_description_text.strip() == "" and jd_file is None:
        raise HTTPException(status_code=400, detail="Job description text or file is required.")

    try:
        resume_bytes = await resume_file.read()
        resume_text = extract_text_from_pdf(resume_bytes)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Resume parse error: {exc}")

    if jd_file is not None and not job_description_text.strip():
        if jd_file.content_type == "application/pdf":
            job_description_text = extract_text_from_pdf(await jd_file.read())
        else:
            job_description_text = (await jd_file.read()).decode("utf-8", errors="ignore")

    if not is_english_text(resume_text) or not is_english_text(job_description_text):
        # Non-English content is accepted but warned in response.
        pass

    analysis = analyze_resume_description(resume_text, job_description_text)
    return JSONResponse(content=analysis)


@app.post("/report")
async def report_resume(
    analysis: dict = Body(...),
    resume_name: str = Form("Resume"),
    job_description_name: str = Form("Job Description"),
):
    try:
        pdf_bytes = create_pdf_report(analysis, resume_name=resume_name, job_description_name=job_description_name)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unable to generate PDF report: {exc}")
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=SmartResumeAI_Report.pdf"})
