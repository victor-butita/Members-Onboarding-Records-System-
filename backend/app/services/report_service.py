import csv
import io
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import Member, AuditLog

def get_report_data(db: Session, report_type: str, category_filter: str = None, unit_filter: str = None) -> Dict[str, Any]:
    query = db.query(Member)
    if category_filter and category_filter != "ALL":
        query = query.filter(Member.category == category_filter)
        
    members = query.order_by(Member.surname.asc()).all()
    total = len(members)
    
    if report_type == "executive_summary":
        # Aggregate summary
        stages = {
            "GAZETTED": sum(1 for m in members if m.stage == "GAZETTED"),
            "SUBMITTED_ONLINE": sum(1 for m in members if m.stage == "SUBMITTED_ONLINE"),
            "DESK_CHECKED_IN": sum(1 for m in members if m.stage == "DESK_CHECKED_IN"),
            "FULLY_CLEARED": sum(1 for m in members if m.stage == "FULLY_CLEARED"),
        }
        unit_progress = {
            "clerks_verified": sum(1 for m in members if m.original_docs_verified),
            "media_approved": sum(1 for m in members if m.photo_approved),
            "ict_biometrics": sum(1 for m in members if m.biometrics_collected),
            "security_cleared": sum(1 for m in members if m.security_cleared),
            "hr_verified": sum(1 for m in members if m.hr_verified),
            "finance_verified": sum(1 for m in members if m.finance_verified),
        }
        return {
            "title": "Executive Summary Report",
            "parliament_term": "14th Parliament of Kenya",
            "total_members": total,
            "stages": stages,
            "unit_progress": unit_progress,
            "generated_at": str(func.now())
        }
        
    elif report_type == "register_of_members":
        rows = []
        for m in members:
            rows.append({
                "id": m.id,
                "full_name": m.full_name,
                "category": m.category,
                "county": m.county or "N/A",
                "constituency": m.constituency or "N/A",
                "party": m.party,
                "stage": m.stage,
                "status": m.status,
                "submission_reference": m.submission_reference or "—"
            })
        return {"title": "Register of Members (14th Parliament)", "total": total, "records": rows}
        
    elif report_type == "online_submissions":
        online_members = [m for m in members if m.submitted_at is not None]
        rows = []
        for m in online_members:
            rows.append({
                "full_name": m.full_name,
                "category": m.category,
                "constituency": m.constituency,
                "national_id": m.national_id,
                "submission_reference": m.submission_reference,
                "submitted_at": m.submitted_at.strftime("%Y-%m-%d %H:%M") if m.submitted_at else "",
                "has_id_upload": bool(m.id_document_path),
                "has_iebc_cert": bool(m.iebc_cert_path),
                "has_photo": bool(m.passport_photo_path),
                "stage": m.stage
            })
        return {"title": "Online Submissions Report", "total": len(rows), "records": rows}

    elif report_type == "physical_onboarding":
        desk_members = [m for m in members if m.desk_checked_in_at is not None]
        rows = []
        for m in desk_members:
            rows.append({
                "full_name": m.full_name,
                "category": m.category,
                "checked_in_at": m.desk_checked_in_at.strftime("%Y-%m-%d %H:%M") if m.desk_checked_in_at else "",
                "checked_in_by": m.desk_checked_in_by or "Clerks L&P",
                "original_docs_verified": m.original_docs_verified,
                "oath_recorded": m.oath_recorded,
                "assets_declaration_filed": m.assets_declaration_filed,
                "stage": m.stage
            })
        return {"title": "Physical Onboarding & Verification Report", "total": len(rows), "records": rows}

    elif report_type == "outstanding_clearance":
        rows = []
        for m in members:
            pending_units = []
            if not m.original_docs_verified: pending_units.append("Clerks (L&P)")
            if not m.photo_approved: pending_units.append("Media Relations")
            if not m.biometrics_collected: pending_units.append("ICT")
            if not m.security_cleared: pending_units.append("Security")
            if not (m.hr_verified and m.finance_verified): pending_units.append("HR & Finance")
            
            if pending_units:
                rows.append({
                    "full_name": m.full_name,
                    "category": m.category,
                    "county": m.county,
                    "party": m.party,
                    "pending_units": pending_units,
                    "stage": m.stage
                })
        return {"title": "Outstanding Clearance by Unit Report", "total": len(rows), "records": rows}

    elif report_type == "document_status":
        rows = []
        for m in members:
            rows.append({
                "full_name": m.full_name,
                "national_id": m.national_id or "—",
                "id_uploaded": bool(m.id_document_path),
                "iebc_uploaded": bool(m.iebc_cert_path),
                "photo_uploaded": bool(m.passport_photo_path),
                "originals_verified": m.original_docs_verified,
                "photo_approved": m.photo_approved
            })
        return {"title": "Document Verification Status Report", "total": len(rows), "records": rows}

    elif report_type == "audit_log":
        audits = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(200).all()
        rows = []
        for a in audits:
            rows.append({
                "timestamp": a.timestamp.strftime("%Y-%m-%d %H:%M:%S") if a.timestamp else "",
                "user_name": a.user_name,
                "unit": a.unit,
                "action": a.action,
                "resource_type": a.resource_type,
                "resource_id": a.resource_id or "",
                "details": a.details,
                "ip_address": a.ip_address or ""
            })
        return {"title": "MORS Complete Audit Log", "total": len(rows), "records": rows}

    return {"title": "Report", "records": []}

def export_members_csv(members: List[Member]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Surname", "Other Names", "Full Name", "Category", "County", "Constituency",
        "Party", "Status", "Stage", "Submission Ref", "National ID", "Phone", "Email",
        "Originals Verified", "Photo Approved", "Biometrics Collected", "Security Cleared",
        "HR Verified", "Finance Verified"
    ])
    for m in members:
        writer.writerow([
            m.id, m.surname, m.other_names, m.full_name, m.category, m.county or "", m.constituency or "",
            m.party, m.status, m.stage, m.submission_reference or "", m.national_id or "", m.phone or "", m.email or "",
            m.original_docs_verified, m.photo_approved, m.biometrics_collected, m.security_cleared,
            m.hr_verified, m.finance_verified
        ])
    return output.getvalue()
