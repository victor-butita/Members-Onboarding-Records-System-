import os
import uuid
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models.models import Member, User, ClearanceLog, utcnow
from app.schemas.schemas import (
    MediaPhotoApprovalRequest, IctBiometricsRequest, SecurityClearanceRequest,
    HrFinanceClearanceRequest, MemberResponse
)
from app.api.deps import require_units, log_audit
from app.api.routes.desk import check_and_update_fully_cleared

router = APIRouter(prefix="/clearance", tags=["Unit Clearance Stations"])

@router.get("/queue/{unit_name}", response_model=List[MemberResponse])
def get_unit_queue(
    unit_name: str,
    status_filter: Optional[str] = "PENDING",  # PENDING or ALL
    current_user: User = Depends(require_units(["MEDIA_RELATIONS", "ICT", "SECURITY", "HR_FINANCE", "CLERK_LP", "CLERK_OFFICE", "AUDITOR"])),
    db: Session = Depends(get_db)
):
    query = db.query(Member).filter(Member.status == "ACTIVE")
    
    # Usually members must be at least checked in or submitted online to clear
    unit = unit_name.upper()
    if unit == "MEDIA_RELATIONS":
        if status_filter == "PENDING":
            query = query.filter(Member.photo_approved == False)
    elif unit == "ICT":
        if status_filter == "PENDING":
            query = query.filter(Member.biometrics_collected == False)
    elif unit == "SECURITY":
        if status_filter == "PENDING":
            query = query.filter(Member.security_cleared == False)
    elif unit in ["HR_FINANCE", "HR", "FINANCE"]:
        if status_filter == "PENDING":
            query = query.filter((Member.hr_verified == False) | (Member.finance_verified == False))
            
    return query.order_by(Member.surname.asc()).all()

@router.post("/media/photo")
async def process_media_photo(
    request: Request,
    member_id: int = Form(...),
    approved: bool = Form(...),
    photo_source: str = Form("UPLOAD"),  # UPLOAD or CAMERA
    notes: Optional[str] = Form(None),
    replacement_photo: Optional[UploadFile] = File(None),
    current_user: User = Depends(require_units(["MEDIA_RELATIONS"])),
    db: Session = Depends(get_db)
):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member record not found.")
        
    now = utcnow()
    if replacement_photo and replacement_photo.filename:
        ext = os.path.splitext(replacement_photo.filename)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png"]:
            raise HTTPException(status_code=400, detail="Only JPG and PNG images are accepted.")
        unique_name = f"{member.id}_official_photo_{uuid.uuid4().hex[:8]}{ext}"
        dest_path = os.path.join(settings.UPLOAD_DIR, unique_name)
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(replacement_photo.file, buffer)
        member.passport_photo_path = f"/uploads/{unique_name}"
        
    member.photo_approved = approved
    member.photo_approved_by = current_user.full_name
    member.photo_approved_at = now
    member.photo_source = photo_source
    
    if notes:
        member.notes = f"{member.notes or ''}\n[Media Note]: {notes}".strip()
        
    check_and_update_fully_cleared(member)
    
    db.add(ClearanceLog(
        member_id=member.id,
        step="Official Passport Photo Approval",
        unit="MEDIA_RELATIONS",
        completed_by_id=current_user.id,
        completed_by_name=current_user.full_name,
        remarks=f"Photo approved: {approved} (Source: {photo_source})",
        timestamp=now
    ))
    db.commit()
    
    log_audit(db, current_user, "TICK", "MEMBER", str(member.id), f"Media photo approval status set to {approved} for {member.full_name}", request)
    return {"message": "Photo status updated.", "photo_approved": member.photo_approved, "photo_url": member.passport_photo_path}

@router.post("/ict/biometrics")
def process_ict_biometrics(
    data: IctBiometricsRequest,
    request: Request,
    current_user: User = Depends(require_units(["ICT"])),
    db: Session = Depends(get_db)
):
    member = db.query(Member).filter(Member.id == data.member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member record not found.")
        
    now = utcnow()
    member.biometrics_collected = data.collected
    member.biometrics_collected_by = current_user.full_name
    member.biometrics_collected_at = now
    
    if data.notes:
        member.notes = f"{member.notes or ''}\n[ICT Note]: {data.notes}".strip()
        
    check_and_update_fully_cleared(member)
    
    db.add(ClearanceLog(
        member_id=member.id,
        step="Chamber Attendance & Voting Biometrics",
        unit="ICT",
        completed_by_id=current_user.id,
        completed_by_name=current_user.full_name,
        remarks=f"Biometrics collection recorded: {data.collected}",
        timestamp=now
    ))
    db.commit()
    
    log_audit(db, current_user, "TICK", "MEMBER", str(member.id), f"Chamber biometrics recorded for {member.full_name}", request)
    return {"message": "Biometrics recorded successfully."}

@router.post("/security/clearance")
async def process_security_clearance(
    request: Request,
    member_id: int = Form(...),
    cleared: bool = Form(...),
    badge_number: str = Form(...),
    notes: Optional[str] = Form(None),
    vetting_form: Optional[UploadFile] = File(None),
    current_user: User = Depends(require_units(["SECURITY"])),
    db: Session = Depends(get_db)
):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member record not found.")
        
    now = utcnow()
    if vetting_form and vetting_form.filename:
        ext = os.path.splitext(vetting_form.filename)[1].lower()
        unique_name = f"{member.id}_vetting_{uuid.uuid4().hex[:8]}{ext}"
        dest_path = os.path.join(settings.UPLOAD_DIR, unique_name)
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(vetting_form.file, buffer)
        member.security_vetting_path = f"/uploads/{unique_name}"
        
    member.security_cleared = cleared
    member.security_cleared_by = current_user.full_name
    member.security_cleared_at = now
    member.badge_number = badge_number.strip()
    
    if notes:
        member.notes = f"{member.notes or ''}\n[Security Note]: {notes}".strip()
        
    check_and_update_fully_cleared(member)
    
    db.add(ClearanceLog(
        member_id=member.id,
        step="Security Badge & Vetting Clearance",
        unit="SECURITY",
        completed_by_id=current_user.id,
        completed_by_name=current_user.full_name,
        remarks=f"Badge #{badge_number} issued. Security cleared: {cleared}",
        timestamp=now
    ))
    db.commit()
    
    log_audit(db, current_user, "TICK", "MEMBER", str(member.id), f"Security badge {badge_number} issued and cleared for {member.full_name}", request)
    return {"message": "Security clearance saved.", "badge_number": member.badge_number}

@router.post("/hr-finance/clearance")
def process_hr_finance_clearance(
    data: HrFinanceClearanceRequest,
    request: Request,
    current_user: User = Depends(require_units(["HR_FINANCE"])),
    db: Session = Depends(get_db)
):
    member = db.query(Member).filter(Member.id == data.member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member record not found.")
        
    now = utcnow()
    member.hr_verified = data.hr_verified
    member.hr_verified_by = current_user.full_name
    member.hr_verified_at = now
    
    member.finance_verified = data.finance_verified
    member.finance_verified_by = current_user.full_name
    member.finance_verified_at = now
    
    if data.bank_name: member.bank_name = data.bank_name.strip()
    if data.bank_account: member.bank_account = data.bank_account.strip()
    if data.bank_branch: member.bank_branch = data.bank_branch.strip()
    if data.nssf_number: member.nssf_number = data.nssf_number.strip()
    if data.sha_number: member.sha_number = data.sha_number.strip()
    
    if data.notes:
        member.notes = f"{member.notes or ''}\n[HR & Finance Note]: {data.notes}".strip()
        
    check_and_update_fully_cleared(member)
    
    db.add(ClearanceLog(
        member_id=member.id,
        step="HR & Finance Clearance",
        unit="HR_FINANCE",
        completed_by_id=current_user.id,
        completed_by_name=current_user.full_name,
        remarks=f"HR verified: {data.hr_verified}, Finance verified: {data.finance_verified}",
        timestamp=now
    ))
    db.commit()
    
    log_audit(db, current_user, "TICK", "MEMBER", str(member.id), f"HR & Finance clearance updated for {member.full_name}", request)
    return {"message": "HR & Finance clearance recorded."}
