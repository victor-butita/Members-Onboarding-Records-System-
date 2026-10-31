from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from app.core.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    unit = Column(String(50), nullable=False)  # SYSTEM_ADMIN, ICT, CLERK_LP, MEDIA_RELATIONS, SECURITY, HR_FINANCE, CLERK_OFFICE, AUDITOR
    role = Column(String(30), nullable=False, default="STAFF")  # SUPER_USER, STAFF, READ_ONLY
    is_active = Column(Boolean, default=True)
    must_change_password = Column(Boolean, default=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    
    # Relationships
    created_users = relationship("User", backref="created_by", remote_side=[id])

class Member(Base):
    __tablename__ = "members"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Gazette attributes
    surname = Column(String(60), nullable=False, index=True)
    other_names = Column(String(100), nullable=False, index=True)
    full_name = Column(String(160), nullable=False, index=True)
    category = Column(String(30), nullable=False, index=True)  # MP, WOMAN_REP, NOMINATED, SPEAKER
    constituency = Column(String(100), nullable=True, index=True)
    county = Column(String(100), nullable=True, index=True)
    party = Column(String(100), nullable=False, index=True)
    gazette_notice_no = Column(String(50), nullable=True)
    gazette_date = Column(String(30), nullable=True)
    status = Column(String(30), default="ACTIVE", index=True)  # ACTIVE, PETITIONED, NULLIFIED, WITHDRAWN
    status_reason = Column(Text, nullable=True)
    is_returning_member = Column(Boolean, default=False)
    term_count = Column(Integer, default=1)
    
    # Member Biodata
    gender = Column(String(20), nullable=True)  # MALE, FEMALE
    date_of_birth = Column(String(30), nullable=True)
    national_id = Column(String(30), nullable=True, index=True, unique=True)
    phone = Column(String(30), nullable=True)
    email = Column(String(120), nullable=True)
    kra_pin = Column(String(30), nullable=True)
    postal_address = Column(String(200), nullable=True)
    qualifications = Column(Text, nullable=True)
    
    # Next of kin
    next_of_kin_name = Column(String(100), nullable=True)
    next_of_kin_relation = Column(String(50), nullable=True)
    next_of_kin_phone = Column(String(30), nullable=True)
    next_of_kin_email = Column(String(120), nullable=True)
    
    # Onboarding status & lifecycle
    stage = Column(String(30), default="GAZETTED", index=True)  # GAZETTED, SUBMITTED_ONLINE, DESK_CHECKED_IN, FULLY_CLEARED
    submission_reference = Column(String(50), nullable=True, unique=True, index=True)
    submitted_at = Column(DateTime, nullable=True)
    is_submission_locked = Column(Boolean, default=False)
    reopened_for_correction = Column(Boolean, default=False)
    desk_checked_in_at = Column(DateTime, nullable=True)
    desk_checked_in_by = Column(String(100), nullable=True)
    fully_cleared_at = Column(DateTime, nullable=True)
    
    # Document storage paths
    id_document_path = Column(String(255), nullable=True)
    iebc_cert_path = Column(String(255), nullable=True)
    passport_photo_path = Column(String(255), nullable=True)
    security_vetting_path = Column(String(255), nullable=True)
    finance_docs_path = Column(String(255), nullable=True)
    
    # Clearance steps
    # 1. Clerks L&P
    original_docs_verified = Column(Boolean, default=False)
    original_docs_verified_by = Column(String(100), nullable=True)
    original_docs_verified_at = Column(DateTime, nullable=True)
    biodata_confirmed = Column(Boolean, default=False)
    biodata_confirmed_by = Column(String(100), nullable=True)
    biodata_confirmed_at = Column(DateTime, nullable=True)
    oath_recorded = Column(Boolean, default=False)
    oath_recorded_by = Column(String(100), nullable=True)
    oath_recorded_at = Column(DateTime, nullable=True)
    assets_declaration_filed = Column(Boolean, default=False)
    assets_declaration_filed_by = Column(String(100), nullable=True)
    assets_declaration_filed_at = Column(DateTime, nullable=True)
    
    # 2. Media Relations
    photo_approved = Column(Boolean, default=False)
    photo_approved_by = Column(String(100), nullable=True)
    photo_approved_at = Column(DateTime, nullable=True)
    photo_source = Column(String(30), default="UPLOAD")  # UPLOAD, CAMERA
    
    # 3. ICT
    biometrics_collected = Column(Boolean, default=False)
    biometrics_collected_by = Column(String(100), nullable=True)
    biometrics_collected_at = Column(DateTime, nullable=True)
    
    # 4. Security
    security_cleared = Column(Boolean, default=False)
    security_cleared_by = Column(String(100), nullable=True)
    security_cleared_at = Column(DateTime, nullable=True)
    badge_number = Column(String(50), nullable=True)
    
    # 5. HR & Finance
    hr_verified = Column(Boolean, default=False)
    hr_verified_by = Column(String(100), nullable=True)
    hr_verified_at = Column(DateTime, nullable=True)
    finance_verified = Column(Boolean, default=False)
    finance_verified_by = Column(String(100), nullable=True)
    finance_verified_at = Column(DateTime, nullable=True)
    bank_name = Column(String(100), nullable=True)
    bank_account = Column(String(50), nullable=True)
    bank_branch = Column(String(100), nullable=True)
    nssf_number = Column(String(50), nullable=True)
    sha_number = Column(String(50), nullable=True)
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    logs = relationship("ClearanceLog", back_populates="member", cascade="all, delete-orphan")

class ClearanceLog(Base):
    __tablename__ = "clearance_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False, index=True)
    step = Column(String(100), nullable=False)
    unit = Column(String(50), nullable=False)
    completed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    completed_by_name = Column(String(100), nullable=False)
    remarks = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=utcnow)
    
    member = relationship("Member", back_populates="logs")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    user_name = Column(String(100), nullable=False)
    unit = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False, index=True)  # LOGIN, UPLOAD, CHECKIN, TICK, EDIT, STATUS_CHANGE, USER_CHANGE, EXPORT
    resource_type = Column(String(50), nullable=False)       # MEMBER, USER, GAZETTE, REPORT, SETTING
    resource_id = Column(String(50), nullable=True)
    details = Column(Text, nullable=False)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=utcnow, index=True)

class EmailOutbox(Base):
    __tablename__ = "email_outbox"
    
    id = Column(Integer, primary_key=True, index=True)
    recipient_email = Column(String(120), nullable=False, index=True)
    recipient_name = Column(String(100), nullable=False)
    subject = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    reference_no = Column(String(50), nullable=True, index=True)
    status = Column(String(20), default="SENT")  # PENDING, SENT, FAILED
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    sent_at = Column(DateTime, default=utcnow)

class SystemSetting(Base):
    __tablename__ = "system_settings"
    
    key = Column(String(50), primary_key=True, index=True)
    value = Column(Text, nullable=False)
    description = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
