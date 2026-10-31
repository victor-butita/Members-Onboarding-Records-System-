import os
import uuid
import shutil
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models.models import Member, SystemSetting
from app.schemas.schemas import MemberPortalLookupItem, MemberResponse
from app.services.email_service import queue_onboarding_confirmation_email
from app.api.deps import log_audit

router = APIRouter(prefix="/portal", tags=["Member Self-Service Portal"])

@router.get("/status")
def get_portal_status(db: Session = Depends(get_db)):
    is_open_setting = db.query(SystemSetting).filter(SystemSetting.key == "PORTAL_OPEN").first()
    deadline_setting = db.query(SystemSetting).filter(SystemSetting.key == "PORTAL_CLOSING_DATE").first()
    
    is_open = is_open_setting.value.lower() == "true" if is_open_setting else settings.PORTAL_OPEN
    deadline = deadline_setting.value if deadline_setting else "2027-08-15 23:59:59"
    
    return {
        "is_open": is_open,
        "closing_date": deadline,
        "parliament_term": settings.PARLIAMENT_TERM,
        "help_desk_email": "mors.support@parliament.go.ke",
        "help_desk_phone": "+254 (0)20 284 8000"
    }

@router.get("/search", response_model=List[MemberPortalLookupItem])
def search_gazetted_members(q: str, db: Session = Depends(get_db)):
    if not q or len(q.strip()) < 2:
        return []
        
    query_str = f"%{q.strip()}%"
    from sqlalchemy import or_
    members = db.query(Member).filter(
        Member.status == "ACTIVE",
        or_(
            Member.full_name.ilike(query_str),
            Member.surname.ilike(query_str),
            Member.other_names.ilike(query_str),
            Member.constituency.ilike(query_str),
            Member.county.ilike(query_str)
        )
    ).limit(15).all()
    
    return [
        MemberPortalLookupItem(
            id=m.id,
            full_name=m.full_name,
            category=m.category,
            constituency=m.constituency,
            county=m.county,
            party=m.party,
            stage=m.stage,
            is_submission_locked=m.is_submission_locked,
            reopened_for_correction=m.reopened_for_correction
        )
        for m in members
    ]

@router.get("/member/{member_id}")
def get_member_portal_profile(member_id: int, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member record not found in gazette notice.")
    
    # Return prefilled gazette information
    return {
        "id": member.id,
        "full_name": member.full_name,
        "surname": member.surname,
        "other_names": member.other_names,
        "category": member.category,
        "constituency": member.constituency,
        "county": member.county,
        "party": member.party,
        "stage": member.stage,
        "is_submission_locked": member.is_submission_locked,
        "reopened_for_correction": member.reopened_for_correction,
        "submission_reference": member.submission_reference,
        # If previously submitted, pre-fill to allow review or correction
        "gender": member.gender,
        "date_of_birth": member.date_of_birth,
        "national_id": member.national_id,
        "phone": member.phone,
        "email": member.email,
        "kra_pin": member.kra_pin,
        "postal_address": member.postal_address,
        "qualifications": member.qualifications,
        "next_of_kin_name": member.next_of_kin_name,
        "next_of_kin_relation": member.next_of_kin_relation,
        "next_of_kin_phone": member.next_of_kin_phone,
        "next_of_kin_email": member.next_of_kin_email,
        "has_id_upload": bool(member.id_document_path),
        "has_iebc_cert": bool(member.iebc_cert_path),
        "has_photo": bool(member.passport_photo_path)
    }

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}

def validate_and_save_upload(file: UploadFile, member_id: int, doc_type: str) -> str:
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Invalid file type for {doc_type}. Only PDF, JPG, and PNG are allowed.")
        
    unique_name = f"{member_id}_{doc_type}_{uuid.uuid4().hex[:8]}{ext}"
    dest_path = os.path.join(settings.UPLOAD_DIR, unique_name)
    
    file.file.seek(0)
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    size_mb = os.path.getsize(dest_path) / (1024 * 1024)
    if size_mb > settings.MAX_FILE_SIZE_MB:
        os.remove(dest_path)
        raise HTTPException(status_code=400, detail=f"{doc_type} file exceeds 5MB limit.")
        
    return f"/uploads/{unique_name}"

@router.post("/submit")
async def submit_member_portal(
    request: Request,
    member_id: int = Form(...),
    gender: str = Form(...),
    date_of_birth: str = Form(...),
    national_id: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    kra_pin: str = Form(...),
    postal_address: str = Form(...),
    qualifications: Optional[str] = Form(None),
    next_of_kin_name: str = Form(...),
    next_of_kin_relation: str = Form(...),
    next_of_kin_phone: str = Form(...),
    next_of_kin_email: Optional[str] = Form(None),
    spam_honeypot: Optional[str] = Form(None),
    id_document: Optional[UploadFile] = File(None),
    iebc_cert: Optional[UploadFile] = File(None),
    passport_photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # Spam honeypot check
    if spam_honeypot:
        raise HTTPException(status_code=400, detail="Invalid submission.")
        
    # Check portal open
    is_open_setting = db.query(SystemSetting).filter(SystemSetting.key == "PORTAL_OPEN").first()
    if is_open_setting and is_open_setting.value.lower() != "true":
        raise HTTPException(status_code=403, detail="The Member Onboarding Portal is currently closed.")

    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member record not found.")
        
    # Safeguard: one submission per member unless reopened for correction
    if member.is_submission_locked and not member.reopened_for_correction:
        raise HTTPException(
            status_code=400,
            detail=f"This record has already been submitted under reference {member.submission_reference}. Please contact the Registration Desk to request a correction."
        )
        
    # Safeguard: unique National ID check across members
    existing_id = db.query(Member).filter(
        Member.national_id == national_id.strip(),
        Member.id != member_id
    ).first()
    if existing_id:
        raise HTTPException(status_code=400, detail="This National ID/Passport number is already registered to another Member.")

    # Save document files if provided
    if id_document and id_document.filename:
        member.id_document_path = validate_and_save_upload(id_document, member.id, "national_id")
    if iebc_cert and iebc_cert.filename:
        member.iebc_cert_path = validate_and_save_upload(iebc_cert, member.id, "iebc_cert")
    if passport_photo and passport_photo.filename:
        member.passport_photo_path = validate_and_save_upload(passport_photo, member.id, "photo")

    # Update member biodata
    member.gender = gender.strip()
    member.date_of_birth = date_of_birth.strip()
    member.national_id = national_id.strip()
    member.phone = phone.strip()
    member.email = email.strip()
    member.kra_pin = kra_pin.strip().upper()
    member.postal_address = postal_address.strip()
    member.qualifications = qualifications.strip() if qualifications else None
    member.next_of_kin_name = next_of_kin_name.strip()
    member.next_of_kin_relation = next_of_kin_relation.strip()
    member.next_of_kin_phone = next_of_kin_phone.strip()
    member.next_of_kin_email = next_of_kin_email.strip() if next_of_kin_email else None
    
    # Generate reference number if not already assigned
    if not member.submission_reference:
        ref_seq = str(member.id).zfill(4)
        member.submission_reference = f"MORS-14P-{ref_seq}"
        
    member.submitted_at = datetime.now(timezone.utc)
    member.is_submission_locked = True
    member.reopened_for_correction = False
    
    if member.stage == "GAZETTED":
        member.stage = "SUBMITTED_ONLINE"
        
    db.commit()
    db.refresh(member)
    
    # Queue confirmation email
    queue_onboarding_confirmation_email(db, member)
    
    log_audit(
        db, None, "SUBMIT", "MEMBER", str(member.id),
        f"Member {member.full_name} completed online onboarding with reference {member.submission_reference}",
        request
    )
    
    return {
        "success": True,
        "message": "Onboarding information successfully submitted.",
        "reference_number": member.submission_reference,
        "member_name": member.full_name,
        "category": member.category,
        "submitted_at": member.submitted_at.isoformat()
    }
