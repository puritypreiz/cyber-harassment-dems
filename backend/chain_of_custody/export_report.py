import json
import os
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from backend.chain_of_custody.audit_log import verify_chain
from backend.chain_of_custody.digital_signature import get_public_key_pem


def build_case_report_json(case, evidence_items, audit_entries, storage_dir: str) -> dict:
    verification = verify_chain(audit_entries)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case": case.to_dict(),
        "evidence": [item.to_dict() for item in evidence_items],
        "chain_of_custody": [entry.to_dict() for entry in audit_entries],
        "chain_verification": verification,
        "signing_public_key": get_public_key_pem(storage_dir),
    }


def write_case_report_pdf(case, evidence_items, audit_entries, output_path: str, storage_dir: str) -> str:
    report = build_case_report_json(case, evidence_items, audit_entries, storage_dir)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph("Chain-of-Custody Report", styles["Title"]),
        Paragraph(f"Case #{case.case_number} — generated {report['generated_at']}", styles["Normal"]),
        Spacer(1, 12),
        Paragraph("Case Summary", styles["Heading2"]),
        Paragraph(f"Status: {case.status} | Severity: {case.severity} | Category: {case.category}", styles["Normal"]),
        Spacer(1, 12),
        Paragraph("Evidence Items", styles["Heading2"]),
    ]

    evidence_rows = [["Filename", "SHA-256", "Uploaded", "Verified"]]
    for item in evidence_items:
        evidence_rows.append([
            item.original_filename,
            item.sha256_hash[:16] + "...",
            item.uploaded_at.strftime("%Y-%m-%d %H:%M UTC") if item.uploaded_at else "",
            "Yes" if item.is_verified else "NO - INTEGRITY FAILURE",
        ])
    evidence_table = Table(evidence_rows, repeatRows=1)
    evidence_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4B2E83")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    elements.append(evidence_table)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Chain-of-Custody Trail", styles["Heading2"]))
    audit_rows = [["Timestamp", "Action", "Signature Valid", "Chain Linkage Valid"]]
    for entry, verified in zip(audit_entries, report["chain_verification"]):
        audit_rows.append([
            entry.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
            entry.action,
            "Yes" if verified["signature_valid"] else "NO",
            "Yes" if verified["chain_linkage_valid"] else "NO",
        ])
    audit_table = Table(audit_rows, repeatRows=1)
    audit_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4B2E83")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    elements.append(audit_table)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(
        "This report's underlying audit entries are individually signed with the "
        "system's RSA private key. The corresponding public key is embedded below "
        "for independent verification.",
        styles["Normal"],
    ))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(report["signing_public_key"].replace("\n", "<br/>"), styles["Code"]))

    doc.build(elements)

    json_path = output_path.rsplit(".", 1)[0] + ".json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return output_path
