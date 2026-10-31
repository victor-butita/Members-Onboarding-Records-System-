from typing import Generator, Optional, List
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.models import User, AuditLog, utcnow

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user

def require_units(allowed_units: List[str]):
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.unit == "SYSTEM_ADMIN" or current_user.unit in allowed_units:
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied for unit: {current_user.unit}. Required: {allowed_units}"
        )
    return checker

def require_super_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.unit == "SYSTEM_ADMIN" or current_user.role == "SUPER_USER":
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Super user authority required for this action."
    )

def log_audit(
    db: Session,
    user: Optional[User],
    action: str,
    resource_type: str,
    resource_id: Optional[str],
    details: str,
    request: Optional[Request] = None
):
    ip_address = request.client.host if request and request.client else None
    audit = AuditLog(
        user_id=user.id if user else None,
        user_name=user.full_name if user else "PUBLIC_PORTAL",
        unit=user.unit if user else "PUBLIC",
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
        timestamp=utcnow()
    )
    db.add(audit)
    db.commit()
