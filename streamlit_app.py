import hashlib
import streamlit as st
from resume_analyzer.pdf_parser import extract_text_from_pdf, is_english_text
from resume_analyzer.analyzer import analyze_resume_description
from resume_analyzer.report import create_pdf_report


def _hash_inputs(resume_bytes: bytes, description_text: str) -> str:
    hasher = hashlib.sha256()
    if resume_bytes:
        hasher.update(resume_bytes)
    hasher.update(description_text.encode("utf-8"))
    return hasher.hexdigest()


def main():
    st.set_page_config(page_title="SmartResumeAI Resume Analyzer", layout="wide")
    st.title("SmartResumeAI — Resume Analyzer & Job Matcher")
    st.markdown(
        "Upload your resume PDF and paste or upload a job description to receive a local AI-powered match analysis, missing skills, strengths, and a downloadable PDF report."
    )

    with st.sidebar:
        st.header("Input")
        resume_file = st.file_uploader("Upload resume PDF", type=["pdf"])
        jd_file = st.file_uploader("Upload job description file", type=["txt", "pdf"])
        jd_text = st.text_area("Paste job description text", height=220)
        if st.button("Analyze"):
            st.session_state["run_analysis"] = True

        if st.button("Load sample data"):
            st.session_state["load_sample"] = True

    if st.session_state.get("load_sample"):
        try:
            with open("samples/resume_sample.txt", "r", encoding="utf-8") as f:
                sample_resume = f.read()
            with open("samples/job_description_sample.txt", "r", encoding="utf-8") as f:
                sample_jd = f.read()
            st.session_state["sample_resume_text"] = sample_resume
            st.session_state["sample_jd_text"] = sample_jd
            st.success("Sample data loaded. Copy to the editor and analyze.")
        except FileNotFoundError:
            st.warning("Sample files not found in the workspace.")

    resume_text = ""
    if resume_file is not None:
        try:
            resume_bytes = resume_file.read()
            resume_text = extract_text_from_pdf(resume_bytes)
        except Exception as exc:
            st.error(f"Resume parsing failed: {exc}")
            resume_text = ""
    elif st.session_state.get("sample_resume_text"):
        resume_text = st.session_state["sample_resume_text"]

    if jd_file is not None and not jd_text.strip():
        if jd_file.type == "application/pdf":
            try:
                jd_text = extract_text_from_pdf(jd_file.read())
            except Exception as exc:
                st.error(f"Job description PDF parsing failed: {exc}")
        else:
            try:
                jd_text = jd_file.read().decode("utf-8", errors="ignore")
            except Exception:
                st.error("Failed to read job description file.")

    if st.session_state.get("run_analysis"):
        if not resume_text:
            st.error("Please upload or provide a valid resume PDF.")
            st.session_state["run_analysis"] = False
            return
        if not jd_text.strip():
            st.error("Please provide a job description text or upload a JD file.")
            st.session_state["run_analysis"] = False
            return

        if not is_english_text(resume_text):
            st.warning("Resume text may not be in English or is too short for reliable language detection.")
        if not is_english_text(jd_text):
            st.warning("Job description may not be in English or is too short for reliable language detection.")

        input_hash = _hash_inputs(resume_text.encode("utf-8"), jd_text)
        if st.session_state.get("last_hash") == input_hash and st.session_state.get("analysis_result") is not None:
            analysis = st.session_state["analysis_result"]
            st.info("Using cached analysis for the same inputs.")
        else:
            with st.spinner("Analyzing resume and job description locally..."):
                analysis = analyze_resume_description(resume_text, jd_text)
            st.session_state["analysis_result"] = analysis
            st.session_state["last_hash"] = input_hash

        st.markdown("## Analysis Overview")
        cols = st.columns(4)
        cols[0].metric("Match Score", f"{analysis['match_score']}%")
        cols[1].metric("Similarity", f"{analysis['similarity']}")
        cols[2].metric("Skill Coverage", f"{analysis['coverage_ratio'] * 100:.1f}%")
        cols[3].metric("Resume Words", analysis["resume_length_words"])

        st.markdown("### Strengths")
        for item in analysis["strengths"]:
            st.markdown(f"- {item}")

        st.markdown("### Improvement Suggestions")
        for item in analysis["improvements"]:
            st.markdown(f"- {item}")

        st.markdown("### Skills Summary")
        st.write(f"**Matched:** {', '.join(analysis['matched_skills']) or 'None detected.'}")
        st.write(f"**Missing:** {', '.join(analysis['missing_skills']) or 'No clearly missing skills detected from the default skill set.'}")

        if analysis.get("notes"):
            with st.expander("Notes and warnings"):
                for note in analysis["notes"]:
                    st.warning(note)

        pdf_bytes = create_pdf_report(analysis, resume_name=resume_file.name if resume_file else "Sample Resume", job_description_name=jd_file.name if jd_file else "Text JD")
        st.download_button(
            label="Download PDF Report",
            data=pdf_bytes,
            file_name="SmartResumeAI_Resume_Report.pdf",
            mime="application/pdf",
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "**How to use:** upload a PDF resume, provide a job description, and click Analyze. The app runs fully locally using open-source Python tools."
    )


if __name__ == "__main__":
    main()
