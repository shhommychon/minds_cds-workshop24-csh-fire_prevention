from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from font_utils import setup_korean_font


def generate_pdf(data):
    # Path to save the PDF
    pdf_path = "output.pdf"

    # Font name
    font_name = setup_korean_font()

    # Create a document template
    pdf = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    styles["Normal"].fontName = font_name
    styles["Title"].fontName = font_name
    elements = []

    # Title row
    title = Paragraph("4. 소방시설등 불량세부사항", styles['Title'])
    elements.append(title)

    # Predefined categories in fixed order
    categories = [
        "소화설비", "경보설비", "피난구조설비", "소화용수설비", "소화활동설비", "기타", "안전시설등", "비고"
    ]
    table_data = [["설비명", "점검번호", "불량내용"]]

    # Add parsed data to the table
    for category in categories:
        if category == "비고":
            # Handle "비고" row separately
            note = data.get(category, "")
            table_data.append([
                category,
                note if note else "※ 점검번호는 소방시설등 자체점검표의 점검항목별 번호를 기입합니다."
            ])
        else:
            values = data.get(category, [])
            if values:
                merged_codes = "\n".join(item['점검번호'] for item in values)
                merged_notes = "\n".join(item['불량내용'] for item in values)
                table_data.append([category, merged_codes, merged_notes])
            else:
                table_data.append([category, "-", "-"])

    # Create the table
    table = Table(table_data, colWidths=[100, 100, 300])
    table_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, -1), font_name),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("SPAN", (1, -1), (2, -1)),  # Merge cells for "비고"
    ])
    table.setStyle(table_style)

    # Add table to elements
    elements.append(table)

    # Build the PDF
    pdf.build(elements)

    return pdf_path
