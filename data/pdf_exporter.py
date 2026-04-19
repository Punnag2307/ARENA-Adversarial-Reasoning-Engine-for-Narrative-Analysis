from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from datetime import datetime
import os

BG     = colors.white
ORANGE = colors.HexColor('#cc4400')
GREEN  = colors.HexColor('#006b3c')
RED    = colors.HexColor('#cc1a1a')
GRAY   = colors.HexColor('#555555')
TEXT   = colors.HexColor('#111111')
TEXT2  = colors.HexColor('#333333')
BORDER = colors.HexColor('#cccccc')

AGENT_COLORS = {
    'Marcus': colors.HexColor('#006b3c'),
    'Elena':  colors.HexColor('#cc1a1a'),
    'Dev':    colors.HexColor('#1a4fcc'),
    'Zara':   colors.HexColor('#555555'),
    'Rohan':  colors.HexColor('#886600'),
    'Moderator': colors.HexColor('#cc4400'),
}


def build_pdf(results: dict, conflict: dict, validation: dict) -> str:
    ticker = results["ticker"]
    company = results["company_name"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ARENA_{ticker}_{timestamp}.pdf"
    os.makedirs("exports", exist_ok=True)
    filepath = os.path.join("exports", filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        leftMargin=20*mm,
        rightMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm,
    )

    styles = getSampleStyleSheet()

    def style(name, **kwargs):
        return ParagraphStyle(name, **kwargs)

    title_style = style('Title',
        fontName='Courier-Bold',
        fontSize=20,
        textColor=ORANGE,
        alignment=TA_CENTER,
        spaceAfter=4,
    )

    sub_style = style('Sub',
        fontName='Courier',
        fontSize=7,
        textColor=GRAY,
        alignment=TA_CENTER,
        spaceAfter=12,
    )

    section_style = style('Section',
        fontName='Courier-Bold',
        fontSize=7,
        textColor=ORANGE,
        spaceBefore=10,
        spaceAfter=4,
    )

    agent_name_style = style('AgentName',
        fontName='Courier-Bold',
        fontSize=9,
        textColor=ORANGE,
        spaceBefore=8,
        spaceAfter=3,
    )

    body_style = style('Body',
        fontName='Helvetica',
        fontSize=9,
        textColor=TEXT2,
        leading=13,
        spaceAfter=6,
    )

    synth_style = style('Synth',
        fontName='Helvetica',
        fontSize=9,
        textColor=TEXT,
        leading=13,
        spaceAfter=6,
    )

    uq_style = style('UQ',
        fontName='Helvetica-Oblique',
        fontSize=9,
        textColor=ORANGE,
        leading=13,
        spaceBefore=8,
    )

    story = []

    # Header
    story.append(Spacer(1, 4))
    story.append(Paragraph("ARENA", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "ADVERSARIAL REASONING ENGINE FOR NARRATIVE ANALYSIS",
        style('Sub2',
            fontName='Courier',
            fontSize=7,
            textColor=GRAY,
            alignment=TA_CENTER,
            spaceAfter=10,
        )
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=ORANGE, spaceAfter=8))
    story.append(Paragraph(
        f"{ticker} — {company}",
        style('Co',
            fontName='Courier-Bold',
            fontSize=13,
            textColor=TEXT,
            alignment=TA_CENTER,
            spaceAfter=6,
        )
    ))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        style('Meta1',
            fontName='Courier',
            fontSize=8,
            textColor=GRAY,
            alignment=TA_CENTER,
            spaceAfter=3,
        )
    ))
    story.append(Paragraph(
        f"Data Quality: {validation['quality']} ({validation['score']}/100)",
        style('Meta2',
            fontName='Courier',
            fontSize=8,
            textColor=GRAY,
            alignment=TA_CENTER,
            spaceAfter=3,
        )
    ))
    story.append(Paragraph(
        f"Temperature: {conflict['debate_temperature']}  |  Polarization: {conflict['polarization_label']}",
        style('Meta3',
            fontName='Courier',
            fontSize=8,
            textColor=GRAY,
            alignment=TA_CENTER,
            spaceAfter=10,
        )
    ))
    story.append(HRFlowable(width="100%", thickness=0.5, color=ORANGE, spaceAfter=12))
    story.append(Spacer(1, 8))

    # Conflict summary table
    story.append(Paragraph("SENTIMENT SCORES", section_style))
    agent_scores = conflict.get('agent_scores', {})
    score_data = [['ANALYST', 'SCORE', 'STANCE']]
    for agent, score in agent_scores.items():
        name = agent.split(' ')[0]
        stance = 'BULLISH' if score > 0.2 else 'BEARISH' if score < -0.2 else 'NEUTRAL'
        score_data.append([name, f"{score:+.3f}", stance])

    score_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, 0), 'Courier-Bold'),
    ('FONTNAME', (0, 1), (-1, -1), 'Courier'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#cc4400')),
    ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#111111')),
    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f5f5f5'), colors.white]),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('LEFTPADDING', (0, 0), (-1, -1), 8),
]))
    story.append(score_table)
    story.append(Spacer(1, 10))

    # Verdict
    v = results.get('verdict', {})
    story.append(Paragraph(
        f"PROBABILITY VERDICT — Bull: {conflict.get('verdict_bull', 25)}% | "
        f"Base: {conflict.get('verdict_base', 50)}% | "
        f"Bear: {conflict.get('verdict_bear', 25)}%",
        style('Verdict', fontName='Courier-Bold', fontSize=8,
              textColor=TEXT, spaceAfter=12)
    ))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))

    # Round 1
    story.append(Spacer(1, 8))
    story.append(Paragraph("ROUND 1 — OPENING POSITIONS", section_style))
    for entry in results['round1']:
        name = entry['agent'].split(' ')[0]
        col = AGENT_COLORS.get(name, GRAY)
        ns = style(f'N_{name}', fontName='Courier-Bold', fontSize=9,
                   textColor=col, spaceBefore=8, spaceAfter=2)
        story.append(Paragraph(f"{name.upper()} — {entry['agent']}", ns))
        story.append(Paragraph(entry['response'].replace('**', ''), body_style))

    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))

    # Round 2
    story.append(Spacer(1, 8))
    story.append(Paragraph("ROUND 2 — CROSS EXAMINATION", section_style))
    for entry in results['round2']:
        name = entry['agent'].split(' ')[0]
        col = AGENT_COLORS.get(name, GRAY)
        ns = style(f'N2_{name}', fontName='Courier-Bold', fontSize=9,
                   textColor=col, spaceBefore=8, spaceAfter=2)
        story.append(Paragraph(f"{name.upper()} — RESPONDING", ns))
        story.append(Paragraph(entry['response'].replace('**', ''), body_style))

    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))

    # Synthesis
    story.append(Spacer(1, 8))
    story.append(Paragraph("FINAL SYNTHESIS — MODERATOR", section_style))
    synthesis_text = results['synthesis'].replace('**', '')
    story.append(Paragraph(synthesis_text, synth_style))

    uq = ''
    for line in synthesis_text.split('\n'):
        if '?' in line and len(line.strip()) > 20:
            uq = line.strip()
    if uq:
        story.append(Paragraph(f'"{uq}"', uq_style))

    doc.build(story)
    return filepath