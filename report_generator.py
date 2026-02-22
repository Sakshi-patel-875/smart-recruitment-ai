from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def generate_report(results, job_skills, filepath):
    doc = SimpleDocTemplate(filepath)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title = Paragraph("<b>Smart Recruitment AI - Match Report</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 20))

    # Job skills
    job_text = "<b>Job Skills:</b> " + ", ".join(job_skills)
    elements.append(Paragraph(job_text, styles['Normal']))
    elements.append(Spacer(1, 20))

    # Table header
    data = [[
        "Rank",
        "Resume",
        "Match %",
        "Matched Skills",
        "Missing Skills"
    ]]

    # Table rows
    for i, r in enumerate(results, start=1):
        data.append([
            str(i),
            r["name"],
            str(r["score"]) + "%",
            Paragraph(", ".join(r["matched"]), styles['Normal']),
            Paragraph(", ".join(r["missing"]), styles['Normal'])
        ])

    # Column widths (VERY IMPORTANT)
    table = Table(
        data,
        colWidths=[40, 100, 60, 170, 170]
    )

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (2, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('ROWHEIGHT', (0, 0), (-1, -1), 30),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(table)
    doc.build(elements)
