"""
Prescription PDF Generator — HTML-to-PDF using reportlab (fallback: HTML file)
"""
from __future__ import annotations

import io
import os
from datetime import datetime
from typing import Optional

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    )
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


BRAND_PURPLE = colors.HexColor("#6366f1") if REPORTLAB_AVAILABLE else None
BRAND_TEAL   = colors.HexColor("#0891b2") if REPORTLAB_AVAILABLE else None


def generate_prescription_pdf(
    prescription_id: str,
    doctor_name: str,
    doctor_specialization: str,
    clinic_name: str,
    patient_name: str,
    patient_dob: Optional[str],
    diagnosis: str,
    medicines: list[dict],
    instructions: Optional[str],
    follow_up_date: Optional[str],
    created_at: str,
) -> bytes:
    """Generate a styled prescription PDF and return as bytes."""

    if not REPORTLAB_AVAILABLE:
        # Fallback: return HTML as bytes
        return _build_html_prescription(
            prescription_id, doctor_name, doctor_specialization, clinic_name,
            patient_name, patient_dob, diagnosis, medicines, instructions,
            follow_up_date, created_at,
        ).encode("utf-8")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=1.5*cm, bottomMargin=2*cm,
        leftMargin=2*cm, rightMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    story  = []

    # ── Header ────────────────────────────────────────────────────────────────
    header_data = [[
        Paragraph(f"<font color='#6366f1' size=18><b>🏥 PraDoc Health</b></font>", styles["Normal"]),
        Paragraph(f"<font size=9 color='#64748b'>Rx No: {prescription_id[:8].upper()}<br/>{created_at}</font>", styles["Normal"]),
    ]]
    header_table = Table(header_data, colWidths=[12*cm, 5*cm])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN",  (1, 0), (1, 0),  "RIGHT"),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=2, color=BRAND_PURPLE, spaceAfter=10))

    # ── Doctor info ───────────────────────────────────────────────────────────
    story.append(Paragraph(f"<b>Dr. {doctor_name}</b>", ParagraphStyle("doc", fontSize=13, textColor=BRAND_PURPLE)))
    story.append(Paragraph(f"<font size=10 color='#64748b'>{doctor_specialization} | {clinic_name}</font>", styles["Normal"]))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0"), spaceAfter=10))

    # ── Patient info ──────────────────────────────────────────────────────────
    pt_data = [
        [Paragraph("<b>Patient</b>", styles["Normal"]), Paragraph(patient_name, styles["Normal"])],
        [Paragraph("<b>DOB</b>",     styles["Normal"]), Paragraph(patient_dob or "—",     styles["Normal"])],
        [Paragraph("<b>Date</b>",    styles["Normal"]), Paragraph(created_at,              styles["Normal"])],
    ]
    pt_table = Table(pt_data, colWidths=[3*cm, 14*cm])
    pt_table.setStyle(TableStyle([
        ("FONTSIZE",   (0, 0), (-1, -1), 9),
        ("TEXTCOLOR",  (0, 0), (0, -1), colors.HexColor("#64748b")),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(pt_table)
    story.append(Spacer(1, 10))

    # ── Diagnosis ─────────────────────────────────────────────────────────────
    story.append(Paragraph("<b>Diagnosis</b>", ParagraphStyle("label", fontSize=10, textColor=BRAND_TEAL)))
    story.append(Paragraph(diagnosis, ParagraphStyle("diag", fontSize=11, leftIndent=10, spaceBefore=4)))
    story.append(Spacer(1, 10))

    # ── Medicines table ───────────────────────────────────────────────────────
    story.append(Paragraph("<b>Medicines</b>", ParagraphStyle("label", fontSize=10, textColor=BRAND_TEAL)))
    story.append(Spacer(1, 4))

    med_header = [["Medicine", "Dosage", "Frequency", "Duration", "Notes"]]
    med_rows   = [
        [
            m.get("name", ""),
            m.get("dosage", ""),
            m.get("frequency", ""),
            m.get("duration", ""),
            m.get("notes", "—"),
        ]
        for m in (medicines or [])
    ]
    med_table = Table(med_header + med_rows, colWidths=[4.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 5*cm])
    med_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), BRAND_PURPLE),
        ("TEXTCOLOR",    (0, 0), (-1, 0), colors.white),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("ALIGN",        (0, 0), (-1, -1), "LEFT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
    ]))
    story.append(med_table)
    story.append(Spacer(1, 12))

    # ── Instructions & Follow-up ──────────────────────────────────────────────
    if instructions:
        story.append(Paragraph("<b>Instructions</b>", ParagraphStyle("label", fontSize=10, textColor=BRAND_TEAL)))
        story.append(Paragraph(instructions, ParagraphStyle("inst", fontSize=10, leftIndent=10, spaceBefore=4)))
        story.append(Spacer(1, 8))

    if follow_up_date:
        story.append(Paragraph(f"<b>Follow-up Date:</b> <font color='#6366f1'>{follow_up_date}</font>",
                                ParagraphStyle("fu", fontSize=10, spaceBefore=4)))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0"), spaceAfter=8))
    story.append(Paragraph(
        f"<font size=8 color='#94a3b8'>This prescription is digitally generated by PraDoc Health. "
        f"Prescription ID: {prescription_id} | © 2026 PraDoc Health</font>",
        styles["Normal"],
    ))

    doc.build(story)
    return buffer.getvalue()


def _build_html_prescription(
    prescription_id, doctor_name, doctor_specialization, clinic_name,
    patient_name, patient_dob, diagnosis, medicines, instructions,
    follow_up_date, created_at,
) -> str:
    """Fallback HTML prescription when reportlab is not available."""
    med_rows = "".join([
        f"<tr>"
        f"<td style='padding:8px;border-bottom:1px solid #f1f5f9;font-weight:700;'>{m.get('name','')}</td>"
        f"<td style='padding:8px;border-bottom:1px solid #f1f5f9;'>{m.get('dosage','')}</td>"
        f"<td style='padding:8px;border-bottom:1px solid #f1f5f9;color:#6366f1;'>{m.get('frequency','')}</td>"
        f"<td style='padding:8px;border-bottom:1px solid #f1f5f9;color:#0f766e;'>{m.get('duration','')}</td>"
        f"<td style='padding:8px;border-bottom:1px solid #f1f5f9;color:#64748b;'>{m.get('notes','—')}</td>"
        f"</tr>"
        for m in (medicines or [])
    ])
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Prescription — PraDoc</title>
  <style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 32px; color: #1e293b; }}
    .header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }}
    .brand {{ font-size: 22px; font-weight: 800; color: #6366f1; }}
    .rx-no {{ font-size: 12px; color: #94a3b8; text-align: right; }}
    hr {{ border: none; border-top: 2px solid #6366f1; margin: 16px 0; }}
    .doctor {{ font-size: 16px; font-weight: 800; color: #1e293b; }}
    .doctor-sub {{ font-size: 12px; color: #64748b; margin-top: 2px; }}
    .info-grid {{ display: grid; grid-template-columns: 80px 1fr; gap: 4px 16px; margin: 14px 0; font-size: 13px; }}
    .info-label {{ color: #94a3b8; font-weight: 600; }}
    .section-label {{ font-size: 11px; font-weight: 800; color: #0891b2; text-transform: uppercase; letter-spacing: 1px; margin: 16px 0 6px; }}
    .diagnosis {{ background: #eef2ff; border-radius: 8px; padding: 10px 14px; font-size: 14px; font-weight: 700; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th {{ background: #6366f1; color: #fff; padding: 8px 10px; text-align: left; font-size: 11px; text-transform: uppercase; }}
    .footer {{ margin-top: 32px; padding-top: 12px; border-top: 1px solid #e2e8f0; font-size: 11px; color: #94a3b8; }}
  </style>
</head>
<body>
  <div class="header">
    <div class="brand">🏥 PraDoc Health</div>
    <div class="rx-no">Rx No: {prescription_id[:8].upper()}<br>{created_at}</div>
  </div>
  <hr>
  <div class="doctor">Dr. {doctor_name}</div>
  <div class="doctor-sub">{doctor_specialization} | {clinic_name}</div>
  <div class="info-grid">
    <span class="info-label">Patient</span><span>{patient_name}</span>
    <span class="info-label">DOB</span><span>{patient_dob or '—'}</span>
    <span class="info-label">Date</span><span>{created_at}</span>
  </div>
  <hr style="border-color:#e2e8f0;border-width:1px;">
  <div class="section-label">Diagnosis</div>
  <div class="diagnosis">{diagnosis}</div>
  <div class="section-label">Medicines</div>
  <table>
    <thead><tr><th>Medicine</th><th>Dosage</th><th>Frequency</th><th>Duration</th><th>Notes</th></tr></thead>
    <tbody>{med_rows}</tbody>
  </table>
  {'<div class="section-label">Instructions</div><p style="font-size:13px;margin:4px 0 0 10px;">' + instructions + '</p>' if instructions else ''}
  {'<p style="margin-top:14px;font-size:13px;color:#6366f1;font-weight:700;">🗓️ Follow-up: ' + follow_up_date + '</p>' if follow_up_date else ''}
  <div class="footer">
    This prescription is digitally generated by PraDoc Health.
    Prescription ID: {prescription_id} | © 2026 PraDoc Health
  </div>
</body>
</html>"""
