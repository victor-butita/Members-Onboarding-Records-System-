from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class LoginRequest(BaseModel):
    username: str
    password: str

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    unit: str
    role: str = "STAFF"

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    unit: str
    role: str
    is_active: bool
    must_change_password: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Member schemas
class MemberGazetteItem(BaseModel):
    surname: str
    other_names: str
    full_name: Optional[str] = None
    category: str  # MP, WOMAN_REP, NOMINATED
    constituency: Optional[str] = None
    county: Optional[str] = None
    party: str
    gazette_notice_no: Optional[str] = None

class GazettePreviewResponse(BaseModel):
    total_parsed: int
    count_mp: int
    count_woman_rep: int
    count_nominated: int
    target_mp: int = 290
    target_woman_rep: int = 47
    target_nominated: int = 12
    is_counts_valid: bool
    sample_records: List[MemberGazetteItem]
    warnings: List[str] = []

class GazetteCommitRequest(BaseModel):
    items: List[MemberGazetteItem]
    gazette_notice_no: str
    replace_existing_seats: bool = True

class MemberPortalLookupItem(BaseModel):
    id: int
    full_name: str
    category: str
    constituency: Optional[str] = None
    county: Optional[str] = None
    party: str
    stage: str
    is_submission_locked: bool
    reopened_for_correction: bool

class MemberPortalSubmitRequest(BaseModel):
    member_id: int
    gender: str
    date_of_birth: str
    national_id: str
    phone: str
    email: str
    kra_pin: str
    postal_address: str
    qualifications: Optional[str] = None
    next_of_kin_name: str
    next_of_kin_relation: str
    next_of_kin_phone: str
    next_of_kin_email: Optional[str] = None
    spam_honeypot: Optional[str] = None  # Spam prevention field

class MemberUpdateRequest(BaseModel):
    surname: Optional[str] = None
    other_names: Optional[str] = None
    category: Optional[str] = None
    constituency: Optional[str] = None
    county: Optional[str] = None
    party: Optional[str] = None
    status: Optional[str] = None
    status_reason: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    national_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    kra_pin: Optional[str] = None
    postal_address: Optional[str] = None
    qualifications: Optional[str] = None
    next_of_kin_name: Optional[str] = None
    next_of_kin_relation: Optional[str] = None
    next_of_kin_phone: Optional[str] = None
    next_of_kin_email: Optional[str] = None
    is_returning_member: Optional[bool] = None
    term_count: Optional[int] = None
    notes: Optional[str] = None

class MemberResponse(BaseModel):
    id: int
    surname: str
    other_names: str
    full_name: str
    category: str
    constituency: Optional[str] = None
    county: Optional[str] = None
    party: str
    gazette_notice_no: Optional[str] = None
    gazette_date: Optional[str] = None
    status: str
    status_reason: Optional[str] = None
    is_returning_member: bool
    term_count: int
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    national_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    kra_pin: Optional[str] = None
    postal_address: Optional[str] = None
    qualifications: Optional[str] = None
    next_of_kin_name: Optional[str] = None
    next_of_kin_relation: Optional[str] = None
    next_of_kin_phone: Optional[str] = None
    next_of_kin_email: Optional[str] = None
    stage: str
    submission_reference: Optional[str] = None
    submitted_at: Optional[datetime] = None
    is_submission_locked: bool
    reopened_for_correction: bool
    desk_checked_in_at: Optional[datetime] = None
    desk_checked_in_by: Optional[str] = None
    fully_cleared_at: Optional[datetime] = None
    
    # Document indicators
    id_document_path: Optional[str] = None
    iebc_cert_path: Optional[str] = None
    passport_photo_path: Optional[str] = None
    security_vetting_path: Optional[str] = None
    finance_docs_path: Optional[str] = None
    
    # Clearance flags
    original_docs_verified: bool
    original_docs_verified_by: Optional[str] = None
    original_docs_verified_at: Optional[datetime] = None
    biodata_confirmed: bool
    biodata_confirmed_by: Optional[str] = None
    biodata_confirmed_at: Optional[datetime] = None
    oath_recorded: bool
    oath_recorded_by: Optional[str] = None
    oath_recorded_at: Optional[datetime] = None
    assets_declaration_filed: bool
    assets_declaration_filed_by: Optional[str] = None
    assets_declaration_filed_at: Optional[datetime] = None
    photo_approved: bool
    photo_approved_by: Optional[str] = None
    photo_approved_at: Optional[datetime] = None
    photo_source: Optional[str] = None
    biometrics_collected: bool
    biometrics_collected_by: Optional[str] = None
    biometrics_collected_at: Optional[datetime] = None
    security_cleared: bool
    security_cleared_by: Optional[str] = None
    security_cleared_at: Optional[datetime] = None
    badge_number: Optional[str] = None
    hr_verified: bool
    hr_verified_by: Optional[str] = None
    hr_verified_at: Optional[datetime] = None
    finance_verified: bool
    finance_verified_by: Optional[str] = None
    finance_verified_at: Optional[datetime] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    bank_branch: Optional[str] = None
    nssf_number: Optional[str] = None
    sha_number: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Desk and Clearance action schemas
class DeskCheckinRequest(BaseModel):
    member_id: int
    notes: Optional[str] = None

class VerifyOriginalsRequest(BaseModel):
    member_id: int
    verified: bool
    biodata_confirmed: bool
    oath_recorded: bool = False
    assets_declaration_filed: bool = False
    notes: Optional[str] = None

class MediaPhotoApprovalRequest(BaseModel):
    member_id: int
    approved: bool
    photo_source: str = "UPLOAD"  # UPLOAD or CAMERA
    notes: Optional[str] = None

class IctBiometricsRequest(BaseModel):
    member_id: int
    collected: bool
    notes: Optional[str] = None

class SecurityClearanceRequest(BaseModel):
    member_id: int
    cleared: bool
    badge_number: str
    notes: Optional[str] = None

class HrFinanceClearanceRequest(BaseModel):
    member_id: int
    hr_verified: bool
    finance_verified: bool
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    bank_branch: Optional[str] = None
    nssf_number: Optional[str] = None
    sha_number: Optional[str] = None
    notes: Optional[str] = None

class ReopenSubmissionRequest(BaseModel):
    member_id: int
    reason: str

# Dashboard and stats
class FunnelStats(BaseModel):
    total_gazetted: int
    submitted_online: int
    submitted_online_pct: float
    desk_checked_in: int
    desk_checked_in_pct: float
    fully_cleared: int
    fully_cleared_pct: float

class UnitProgressItem(BaseModel):
    unit: str
    unit_name: str
    completed: int
    pending: int
    pct: float

class DashboardResponse(BaseModel):
    funnel: FunnelStats
    unit_progress: List[UnitProgressItem]
    category_breakdown: Dict[str, Dict[str, int]]
    recent_activity: List[Dict[str, Any]]
    fourteen_day_trend: List[Dict[str, Any]]
    alerts: List[Dict[str, str]]

class DemographicInsights(BaseModel):
    total_members: int
    avg_age: float
    median_age: float
    min_age: int
    max_age: int
    age_brackets: Dict[str, int]
    gender_counts: Dict[str, int]
    female_share_pct: float
    under_35_count: int
    under_35_pct: float
    first_term_count: int
    first_term_pct: float
    returning_count: int
    returning_pct: float
    party_breakdown: Dict[str, int]
    category_breakdown: Dict[str, int]

class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_name: str
    unit: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: str
    ip_address: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class EmailOutboxResponse(BaseModel):
    id: int
    recipient_email: str
    recipient_name: str
    subject: str
    body: str
    reference_no: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    sent_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
