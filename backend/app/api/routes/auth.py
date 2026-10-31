from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, hash_password, create_access_token
from app.models.models import User
from app.schemas.schemas import LoginRequest, Token, PasswordChangeRequest, UserResponse
from app.api.deps import get_current_user, log_audit

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login(request_data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    clean_username = request_data.username.strip().lower()
    user = db.query(User).filter(User.username.ilike(clean_username)).first()
    
    # Check password directly, or trimmed in case of copy-paste whitespace/tabs
    pwd_valid = False
    if user:
        if verify_password(request_data.password, user.hashed_password):
            pwd_valid = True
        elif verify_password(request_data.password.strip(), user.hashed_password):
            pwd_valid = True

    if not user or not pwd_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled. Please contact your Unit Administrator."
        )
        
    access_token = create_access_token(
        subject=user.username,
        role=user.role,
        unit=user.unit
    )
    
    log_audit(db, user, "LOGIN", "USER", str(user.id), f"User {user.username} logged in successfully", request)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "unit": user.unit,
            "role": user.role,
            "must_change_password": user.must_change_password
        }
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/change-password")
def change_password(
    data: PasswordChangeRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is not correct.")
        
    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters.")
        
    current_user.hashed_password = hash_password(data.new_password)
    current_user.must_change_password = False
    db.commit()
    
    log_audit(db, current_user, "USER_CHANGE", "USER", str(current_user.id), "Password changed successfully", request)
    return {"message": "Password updated successfully."}
