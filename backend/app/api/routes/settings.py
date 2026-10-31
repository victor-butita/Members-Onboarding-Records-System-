from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import SystemSetting, EmailOutbox, User, utcnow
from app.schemas.schemas import EmailOutboxResponse
from app.api.deps import require_units, get_current_user, log_audit

router = APIRouter(prefix="/settings", tags=["System Settings & Outbox"])

@router.get("/")
def get_all_settings(
    current_user: User = Depends(require_units(["ICT", "CLERK_LP"])),
    db: Session = Depends(get_db)
):
    settings_records = db.query(SystemSetting).all()
    return {s.key: s.value for s in settings_records}

@router.post("/")
def update_setting(
    key: str,
    value: str,
    description: Optional[str] = None,
    request: Request = None,
    current_user: User = Depends(require_units(["ICT"])),
    db: Session = Depends(get_db)
):
    setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if setting:
        setting.value = value
        if description: setting.description = description
    else:
        setting = SystemSetting(key=key, value=value, description=description)
        db.add(setting)
        
    db.commit()
    log_audit(db, current_user, "SETTING", "SYSTEM_SETTING", key, f"Updated {key} to {value}", request)
    return {"message": f"Setting {key} updated successfully."}

@router.get("/outbox", response_model=List[EmailOutboxResponse])
def get_email_outbox(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_units(["ICT", "CLERK_LP"])),
    db: Session = Depends(get_db)
):
    return db.query(EmailOutbox).order_by(EmailOutbox.created_at.desc()).offset(skip).limit(limit).all()

@router.post("/outbox/{email_id}/resend")
def resend_outbox_email(
    email_id: int,
    request: Request,
    current_user: User = Depends(require_units(["ICT"])),
    db: Session = Depends(get_db)
):
    email = db.query(EmailOutbox).filter(EmailOutbox.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email record not found.")
        
    email.status = "SENT"
    email.sent_at = utcnow()
    email.error_message = None
    db.commit()
    
    log_audit(db, current_user, "EMAIL_RESEND", "EMAIL", str(email.id), f"Resent confirmation email to {email.recipient_email}", request)
    return {"message": f"Email to {email.recipient_email} queued and sent."}
