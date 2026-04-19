import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors


def create_pdf_report(analysis: dict, resume_name: str = "Resume", job_description_name: str = "Job Description") -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=inch / 2, leftMargin=inch / 2, topMargin=inch / 2, bottomMargin=inch / 2)
    style = ParagraphStyle(name="Normal", fontSize=11, leading=14, alignment=TA_LEFT)
    title_style = ParagraphStyle(name="Title", fontSize=18, leading=22, spaceAfter=18)
    heading_style = ParagraphStyle(name="Heading", fontSize=13, leading=16, spaceAfter=10, textColor=colors.HexColor("#2E4053"))

    items = []
    items.append(Paragraph("SmartResumeAI - Resume Match Report", title_style))
    items.append(Paragraph(f"Resume: {resume_name}", style))
    items.append(Paragraph(f"Job Description: {job_description_name}", style))
    items.append(Spacer(1, 12))

    table_data = [
        ["Match Score", f"{analysis['match_score']}%"],
        ["Similarity", f"{analysis['similarity']}"],
        ["Skill coverage", f"{analysis['coverage_ratio'] * 100:.1f}%"],
        ["Resume length", f"{analysis['resume_length_words']} words"],
        ["JD length", f"{analysis['job_description_length_words']} words"],
    ]
    table = Table(table_data, colWidths=[2.3 * inch, 3.2 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D6EAF8")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5D8DC")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
    ]))
    items.append(table)
    items.append(Spacer(1, 14))

    items.append(Paragraph("Key strengths", heading_style))
    for strength in analysis["strengths"]:
        items.append(Paragraph(f"• {strength}", style))
    items.append(Spacer(1, 10))

    items.append(Paragraph("Improvement suggestions", heading_style))
    for improvement in analysis["improvements"]:
        items.append(Paragraph(f"• {improvement}", style))
    items.append(Spacer(1, 10))

    if analysis["matched_skills"]:
        items.append(Paragraph("Matched skills", heading_style))
        items.append(Paragraph(", ".join(analysis["matched_skills"]), style))
        items.append(Spacer(1, 10))

    if analysis["missing_skills"]:
        items.append(Paragraph("Skills to add", heading_style))
        items.append(Paragraph(", ".join(analysis["missing_skills"]), style))
        items.append(Spacer(1, 10))

    if analysis.get("notes"):
        items.append(Paragraph("Notes", heading_style))
        for note in analysis["notes"]:
            items.append(Paragraph(f"• {note}", style))

    doc.build(items)
    return buffer.getvalue()
