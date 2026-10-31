from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.models import EmailOutbox, Member

def queue_onboarding_confirmation_email(db: Session, member: Member) -> EmailOutbox:
    subject = f"MORS 14th Parliament: Onboarding Confirmation - {member.full_name} ({member.submission_reference})"
    
    body = f"""Dear Hon. {member.full_name},

Thank you for completing your pre-registration on the Members' Onboarding & Records System (MORS) for the 14th Parliament of Kenya.

Your details have been successfully captured before arrival:
--------------------------------------------------
Official Name: {member.full_name}
Category: {member.category.replace('_', ' ')}
County: {member.county or 'N/A'}
Constituency: {member.constituency or 'N/A'}
Party: {member.party}
National ID / Passport: {member.national_id}
Submission Reference: {member.submission_reference}
Date & Time: {member.submitted_at.strftime('%Y-%m-%d %H:%M:%S UTC') if member.submitted_at else 'N/A'}
--------------------------------------------------

NEXT STEPS AT PARLIAMENT BUILDINGS (REGISTRATION DESK):
1. Please carry your ORIGINAL National Identity Card / Valid Passport.
2. Please carry your ORIGINAL IEBC Certificate of Election / Nomination.
3. Report to the Registration Desk (Clerks - Legal & Parliamentary Affairs) for physical document verification.
4. Proceed through Media Relations (Photo approval), ICT (Chamber biometrics), Security (Badge issuance), and HR & Finance (Payroll/Bank/SHA).

FOR ANY CORRECTIONS OR INQUIRIES:
Contact the Office of the Director, Legal & Parliamentary Affairs:
Email: mors.support@parliament.go.ke / registry@parliament.go.ke
Helpline: +254 (0)20 284 8000 / Ext 3100
National Assembly, Parliament Buildings, Parliament Road, Nairobi.

Yours faithfully,
The Registry & Onboarding Secretariat
Office of the Clerk of the National Assembly
Republic of Kenya
"""

    outbox = EmailOutbox(
        recipient_email=member.email or "member@parliament.go.ke",
        recipient_name=member.full_name,
        subject=subject,
        body=body,
        reference_no=member.submission_reference,
        status="SENT",  # Logged in outbox
        sent_at=datetime.now(timezone.utc)
    )
    db.add(outbox)
    db.commit()
    db.refresh(outbox)
    return outbox
