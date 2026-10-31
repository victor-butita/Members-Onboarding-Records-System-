from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password
from app.models.models import User, utcnow
from app.schemas.schemas import UserCreate, UserUpdate, UserResponse
from app.api.deps import get_current_user, require_super_user, log_audit

router = APIRouter(prefix="/users", tags=["User Hierarchy & Administration"])

@router.get("/", response_model=List[UserResponse])
def list_users(
    unit: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(User)
    
    # If not System Admin or ICT, can only view users in their own unit
    if current_user.unit not in ["SYSTEM_ADMIN", "ICT"]:
        query = query.filter(User.unit == current_user.unit)
    elif unit and unit != "ALL":
        query = query.filter(User.unit == unit)
        
    return query.order_by(User.unit.asc(), User.full_name.asc()).all()

@router.post("/", response_model=UserResponse)
def create_user(
    data: UserCreate,
    request: Request,
    current_user: User = Depends(require_super_user),
    db: Session = Depends(get_db)
):
    # Validation: A unit super user can only add users to their own unit
    if current_user.unit not in ["SYSTEM_ADMIN", "ICT"] and data.unit != current_user.unit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Unit super users can only create accounts for their own unit ({current_user.unit})."
        )
        
    # Check if username or email already exists
    existing = db.query(User).filter((User.username == data.username) | (User.email == data.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already in use.")
        
    new_user = User(
        username=data.username.strip().lower(),
        email=data.email.strip().lower(),
        full_name=data.full_name.strip(),
        hashed_password=hash_password(data.password),
        unit=data.unit,
        role=data.role,
        is_active=True,
        must_change_password=True,  # Mandatory password change on first sign-in
        created_by_id=current_user.id,
        created_at=utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    log_audit(
        db, current_user, "USER_CHANGE", "USER", str(new_user.id),
        f"Created user {new_user.username} ({new_user.full_name}) for unit {new_user.unit}",
        request
    )
    return new_user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    request: Request,
    current_user: User = Depends(require_super_user),
    db: Session = Depends(get_db)
):
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found.")
        
    if current_user.unit not in ["SYSTEM_ADMIN", "ICT"] and target_user.unit != current_user.unit:
        raise HTTPException(status_code=403, detail="Cannot edit users outside your unit.")
        
    update_data = data.dict(exclude_unset=True)
    for field, val in update_data.items():
        setattr(target_user, field, val)
        
    db.commit()
    db.refresh(target_user)
    
    log_audit(db, current_user, "USER_CHANGE", "USER", str(target_user.id), f"Updated user {target_user.username}", request)
    return target_user

@router.post("/{user_id}/reset-password")
def reset_user_password(
    user_id: int,
    temp_password: str,
    request: Request,
    current_user: User = Depends(require_super_user),
    db: Session = Depends(get_db)
):
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found.")
        
    if current_user.unit not in ["SYSTEM_ADMIN", "ICT"] and target_user.unit != current_user.unit:
        raise HTTPException(status_code=403, detail="Cannot reset passwords for users outside your unit.")
        
    target_user.hashed_password = hash_password(temp_password)
    target_user.must_change_password = True
    db.commit()
    
    log_audit(db, current_user, "USER_CHANGE", "USER", str(target_user.id), f"Reset password for user {target_user.username}", request)
    return {"message": f"Password reset for {target_user.username}. Temporary password set."}
