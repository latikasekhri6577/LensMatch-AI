import src.face_mesh
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

def generate_report(measurements,face_shape,recommendation):
    pdf_path = "LensMatch_Report.pdf"

    doc = SimpleDocTemplate(pdf_path)

    styles = getSampleStyleSheet()

    story = []

    story.append(
    Paragraph(
        "<b>LensMatch AI</b>",
        styles["Title"]
    )
    )
    date = datetime.now().strftime("%d-%m-%Y %H:%M")

    story.append(
    Paragraph(
        f"Generated on: {date}",
        styles["Normal"]
    )
    )
    story.append(Spacer(1,20))

    story.append(
    Paragraph(
        f"<b>Face Shape:</b> {face_shape}",
        styles["Heading2"]
    )
    )

    story.append(
    Paragraph("<b>Measurements</b>",styles["Heading2"])
)

    story.append(
    Paragraph(f"Face Width : {measurements['face_width']:.1f}px",
    styles["Normal"])
)

    story.append(
    Paragraph(f"Face Height : {measurements['face_height']:.1f}px",
    styles["Normal"])
)

    story.append(
    Paragraph(f"Forehead Width : {measurements['forehead_width']:.1f}px",
    styles["Normal"])
)

    story.append(
    Paragraph(f"Cheekbone Width : {measurements['cheekbone_width']:.1f}px",
    styles["Normal"])
)

    story.append(
    Paragraph(f"Jaw Width : {measurements['jaw_width']:.1f}px",
    styles["Normal"])
)

    story.append(
    Paragraph(f"Aspect Ratio : {measurements['aspect_ratio']:.2f}",
    styles["Normal"])
)

    story.append(Spacer(1,20))

    story.append(
    Paragraph(
        "<b>Recommended Frames</b>",
        styles["Heading2"]
    )
)

    for frame in recommendation["recommended"]:

        story.append(
        Paragraph(
            f"• {frame}",
            styles["Normal"]
        )
    )
        
    doc.build(story)

    return pdf_path