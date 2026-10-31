from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Member, User, ClearanceLog, utcnow
from app.schemas.schemas import DeskCheckinRequest, VerifyOriginalsRequest, MemberResponse, ReopenSubmissionRequest
from app.api.deps import require_units, get_current_user, log_audit

router = APIRouter(prefix="/desk", tags=["Registration Desk (Clerks L&P)"])

@router.get("/queue", response_model=List[MemberResponse])
def get_desk_queue(
    q: Optional[str] = None,
    stage: Optional[str] = None,
    current_user: User = Depends(require_units(["CLERK_LP", "CLERK_OFFICE", "AUDITOR"])),
    db: Session = Depends(get_db)
):
    query = db.query(Member).filter(Member.status == "ACTIVE")
    if q:
        query = query.filter(
            (Member.full_name.ilike(f"%{q}%")) |
            (Member.national_id.ilike(f"%{q}%")) |
            (Member.submission_reference.ilike(f"%{q}%")) |
            (Member.constituency.ilike(f"%{q}%")) |
            (Member.county.ilike(f"%{q}%"))
        )
    if stage and stage != "ALL":
        query = query.filter(Member.stage == stage)
        
    return query.order_by(Member.surname.asc()).all()

@router.post("/checkin")
def check_in_member(
    data: DeskCheckinRequest,
    request: Request,
    current_user: User = Depends(require_units(["CLERK_LP"])),
    db: Session = Depends(get_db)
):
    member = db.query(Member).filter(Member.id == data.member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member record not found.")
        
    member.desk_checked_in_at = utcnow()
    member.desk_checked_in_by = current_user.full_name
    
    if member.stage in ["GAZETTED", "SUBMITTED_ONLINE"]:
        member.stage = "DESK_CHECKED_IN"
        
    if data.notes:
        member.notes = f"{member.notes or ''}\n[Check-in Note]: {data.notes}".strip()
        
    log_entry = ClearanceLog(
        member_id=member.id,
        step="Desk Physical Check-In",
        unit="CLERK_LP",
        completed_by_id=current_user.id,
        completed_by_name=current_user.full_name,
        remarks="Member physically reported to Registration Desk.",
        timestamp=utcnow()
    )
    db.add(log_entry)
    db.commit()
    
    log_audit(db, current_user, "CHECKIN", "MEMBER", str(member.id), f"Member {member.full_name} checked in at desk", request)
    return {"message": f"Hon. {member.full_name} successfully checked in.", "stage": member.stage}

@router.post("/verify-documents")
def verify_original_documents(
    data: VerifyOriginalsRequest,
    request: Request,
    current_user: User = Depends(require_units(["CLERK_LP"])),
    db: Session = Depends(get_db)
):
    member = db.query(Member).filter(Member.id == data.member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member record not found.")
        
    now = utcnow()
    member.original_docs_verified = data.verified
    member.original_docs_verified_by = current_user.full_name
    member.original_docs_verified_at = now
    
    member.biodata_confirmed = data.biodata_confirmed
    member.biodata_confirmed_by = current_user.full_name
    member.biodata_confirmed_at = now
    
    if data.oath_recorded:
        member.oath_recorded = True
        member.oath_recorded_by = current_user.full_name
        member.oath_recorded_at = now
        
    if data.assets_declaration_filed:
        member.assets_declaration_filed = True
        member.assets_declaration_filed_by = current_user.full_name
        member.assets_declaration_filed_at = now
        
    if data.notes:
        member.notes = f"{member.notes or ''}\n[L&P Verification Note]: {data.notes}".strip()
        
    # Check if all 6 units are complete to advance stage to FULLY_CLEARED
    check_and_update_fully_cleared(member)
    
    log_entry = ClearanceLog(
        member_id=member.id,
        step="Original Documents & Biodata Verification",
        unit="CLERK_LP",
        completed_by_id=current_user.id,
        completed_by_name=current_user.full_name,
        remarks=f"Original docs verified: {data.verified}, Oath: {data.oath_recorded}, Assets: {data.assets_declaration_filed}",
        timestamp=now
    )
    db.add(log_entry)
    db.commit()
    
    log_audit(db, current_user, "TICK", "MEMBER", str(member.id), f"Original documents & biodata verified for {member.full_name}", request)
    return {"message": "Verification records saved.", "stage": member.stage}

@router.post("/reopen")
def reopen_submission_for_correction(
    data: ReopenSubmissionRequest,
    request: Request,
    current_user: User = Depends(require_units(["CLERK_LP"])),
    db: Session = Depends(get_db)
):
    member = db.query(Member).filter(Member.id == data.member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member record not found.")
        
    member.is_submission_locked = False
    member.reopened_for_correction = True
    member.notes = f"{member.notes or ''}\n[Reopened by {current_user.full_name}]: {data.reason}".strip()
    
    db.commit()
    log_audit(db, current_user, "EDIT", "MEMBER", str(member.id), f"Online submission reopened for {member.full_name}. Reason: {data.reason}", request)
    return {"message": f"Online submission reopened for Hon. {member.full_name}."}

def check_and_update_fully_cleared(member: Member):
    if (
        member.original_docs_verified and
        member.biodata_confirmed and
        member.photo_approved and
        member.biometrics_collected and
        member.security_cleared and
        member.hr_verified and
        member.finance_verified
    ):
        member.stage = "FULLY_CLEARED"
        member.fully_cleared_at = utcnow()
