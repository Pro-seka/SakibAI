"""
services/export_service.py — Export conversations to TXT / Markdown / PDF
"""

import io
from datetime import datetime
from typing import Optional


def to_markdown(title: str, messages: list[dict]) -> str:
    lines = [f"# {title}", f"*Exported from SakibAI on {datetime.now().strftime('%Y-%m-%d %H:%M')}*", "---", ""]
    for m in messages:
        if m["role"] == "system":
            continue
        role = "**You**" if m["role"] == "user" else "**SakibAI**"
        lines.append(f"{role}\n\n{m['content']}\n\n---\n")
    return "\n".join(lines)


def to_txt(title: str, messages: list[dict]) -> str:
    lines = [f"{title}", f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}", "=" * 60, ""]
    for m in messages:
        role = "You" if m["role"] == "user" else "SakibAI"
        lines.append(f"[{role}]")
        lines.append(m["content"])
        lines.append("")
    return "\n".join(lines)


def to_pdf_bytes(title: str, messages: list[dict]) -> Optional[bytes]:
    """Generate PDF bytes. Returns None if reportlab not available."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
        from reportlab.lib.enums import TA_LEFT

        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )
        styles = getSampleStyleSheet()

        user_style = ParagraphStyle(
            "UserMsg",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#1a1a2e"),
            spaceAfter=4,
        )
        ai_style = ParagraphStyle(
            "AIMsg",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#0f3460"),
            spaceAfter=4,
        )
        label_style = ParagraphStyle(
            "Label",
            parent=styles["Normal"],
            fontSize=8,
            textColor=colors.grey,
            spaceAfter=2,
        )

        story = [
            Paragraph(f"<b>{title}</b>", styles["Title"]),
            Paragraph(
                f"Exported from SakibAI · {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                styles["Normal"],
            ),
            Spacer(1, 0.4 * cm),
            HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e0e0e0")),
            Spacer(1, 0.3 * cm),
        ]

        for m in messages:
            if m["role"] == "system":
                continue
            label = "You" if m["role"] == "user" else "SakibAI"
            story.append(Paragraph(label, label_style))
            safe_content = m["content"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            style = user_style if m["role"] == "user" else ai_style
            story.append(Paragraph(safe_content, style))
            story.append(Spacer(1, 0.2 * cm))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#f0f0f0")))
            story.append(Spacer(1, 0.2 * cm))

        doc.build(story)
        return buf.getvalue()
    except ImportError:
        return None
