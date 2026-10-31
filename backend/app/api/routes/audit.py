from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import AuditLog, User
from app.schemas.schemas import AuditLogResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/audit", tags=["Audit Log"])

@router.get("/", response_model=List[AuditLogResponse])
def get_audit_trail(
    unit: Optional[str] = None,
    action: Optional[str] = None,
    user_name: Optional[str] = None,
    skip: int = 0,
    limit: int = 150,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(AuditLog)
    if unit and unit != "ALL":
        query = query.filter(AuditLog.unit == unit)
    if action and action != "ALL":
        query = query.filter(AuditLog.action == action)
    if user_name:
        query = query.filter(AuditLog.user_name.ilike(f"%{user_name}%"))
        
    return query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
