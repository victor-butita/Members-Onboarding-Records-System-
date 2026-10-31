from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.database import get_db
from app.models.models import Member, User, ClearanceLog, utcnow
from app.schemas.schemas import MemberResponse, MemberUpdateRequest
from app.api.deps import get_current_user, require_units, log_audit

router = APIRouter(prefix="/members", tags=["Members Directory"])

@router.get("/", response_model=List[MemberResponse])
def list_members(
    q: Optional[str] = None,
    category: Optional[str] = None,
    stage: Optional[str] = None,
    status: Optional[str] = None,
    county: Optional[str] = None,
    party: Optional[str] = None,
    skip: int = 0,
    limit: int = 400,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Member)
    if q:
        search_fmt = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Member.full_name.ilike(search_fmt),
                Member.national_id.ilike(search_fmt),
                Member.submission_reference.ilike(search_fmt),
                Member.constituency.ilike(search_fmt),
                Member.county.ilike(search_fmt),
                Member.party.ilike(search_fmt)
            )
        )
    if category and category != "ALL":
        query = query.filter(Member.category == category)
    if stage and stage != "ALL":
        query = query.filter(Member.stage == stage)
    if status and status != "ALL":
        query = query.filter(Member.status == status)
    if county and county != "ALL":
        query = query.filter(Member.county == county)
    if party and party != "ALL":
        query = query.filter(Member.party == party)
        
    return query.order_by(Member.surname.asc()).offset(skip).limit(limit).all()

@router.get("/{member_id}")
def get_member_dossier(
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found.")
        
    logs = db.query(ClearanceLog).filter(ClearanceLog.member_id == member_id).order_by(ClearanceLog.timestamp.desc()).all()
    
    return {
        "member": MemberResponse.from_orm(member),
        "logs": [
            {
                "id": l.id,
                "step": l.step,
                "unit": l.unit,
                "completed_by": l.completed_by_name,
                "remarks": l.remarks,
                "timestamp": l.timestamp.isoformat() if l.timestamp else None
            }
            for l in logs
        ]
    }

@router.put("/{member_id}", response_model=MemberResponse)
def update_member_details(
    member_id: int,
    data: MemberUpdateRequest,
    request: Request,
    current_user: User = Depends(require_units(["CLERK_LP", "ICT"])),
    db: Session = Depends(get_db)
):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found.")
        
    update_dict = data.dict(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(member, field, val)
        
    # Re-calculate full_name if surname or other_names changed
    if "surname" in update_dict or "other_names" in update_dict:
        member.full_name = f"{member.surname} {member.other_names}".strip()
        
    db.commit()
    db.refresh(member)
    
    log_audit(db, current_user, "EDIT", "MEMBER", str(member.id), f"Member details updated for {member.full_name}", request)
    return member

@router.post("/{member_id}/status")
def update_member_status(
    member_id: int,
    status: str,
    reason: str,
    request: Request,
    current_user: User = Depends(require_units(["CLERK_LP", "ICT"])),
    db: Session = Depends(get_db)
):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found.")
        
    old_status = member.status
    member.status = status.upper()
    member.status_reason = f"[{utcnow().strftime('%Y-%m-%d %H:%M')}] By {current_user.full_name}: {reason}"
    db.commit()
    
    log_audit(
        db, current_user, "STATUS_CHANGE", "MEMBER", str(member.id),
        f"Status changed from {old_status} to {member.status}. Reason: {reason}",
        request
    )
    return {"message": f"Status updated to {member.status}."}
