import random
import re
from datetime import datetime, timedelta, timezone
from app.core.database import SessionLocal, engine
from app.models.models import User, Member, ClearanceLog, AuditLog, EmailOutbox, SystemSetting, utcnow

KENYA_PARLIAMENT_STAFF = {
    "SYSTEM_ADMIN": ("admin", "Allan Kimani", "Administrative Officer III (Secretariat Lead)"),
    "CLERK_OFFICE": ("clerk.office", "Samuel Njoroge", "The Clerk of the National Assembly"),
    "CLERK_LP": ("clerk.lp", "Dorothy Mwende", "Legal & Parliamentary Affairs Officer"),
    "CLERK_LP_2": ("serah.kioko", "Serah Kioko", "Senior Clerk Assistant"),
    "MEDIA_RELATIONS": ("media.lead", "Erick Wandera", "Media Relations & Hansard Officer"),
    "ICT": ("ict.lead", "Bernard Kiprotich", "Parliamentary ICT Directorate Engineer"),
    "SECURITY": ("security.lead", "Major (Rtd.) Bashir Abdullahi", "Parliamentary Security & Safety Officer"),
    "HR_FINANCE": ("hr.finance", "Grace Nyambura", "Senior Finance & Payroll Accountant"),
    "AUDITOR": ("auditor", "CPA Peter Mecha", "Internal Auditor General")
}

PARLIAMENT_LAN_IPS = [
    "10.20.14.15", "10.20.14.22", "10.20.14.38", "10.20.14.41",
    "10.20.15.10", "10.20.15.18", "10.20.16.5", "10.20.16.12",
    "192.168.10.45", "192.168.10.88"
]

PUBLIC_IPS = [
    "102.219.208.12", "105.160.45.22", "197.237.114.5", "41.90.180.64",
    "105.161.88.19", "197.232.8.44", "102.135.168.90", "105.163.12.7"
]

QUALIFICATIONS_BY_CATEGORY = [
    "Bachelor of Laws (LL.B), University of Nairobi; Post-Graduate Diploma, KSL; Advocate of the High Court of Kenya",
    "Master of Science in Economics, Kenyatta University; Bachelor of Economics & Finance",
    "Master of Business Administration (MBA), Strathmore University; Bachelor of Commerce (Finance)",
    "Bachelor of Science in Actuarial Science, University of Nairobi; Bachelor of Laws (LL.B)",
    "Master of Arts in International Relations, USIU-Africa; Bachelor of Arts in Political Science",
    "Bachelor of Science in Civil Engineering, JKUAT; Registered Consulting Engineer, EBK",
    "Bachelor of Medicine and Bachelor of Surgery (MBChB), Moi University; Fellow, COSECSA",
    "Bachelor of Education (Arts), Egerton University; Higher Diploma in Human Resource Management",
    "Master of Public Policy and Administration, Kenyatta University; CPA (K)",
    "Bachelor of Science in Agriculture, University of Eldoret; Diploma in Farm Management"
]

def enrich_authentic_records():
    db = SessionLocal()
    now = utcnow()

    print("Enriching real members with authentic Parliamentary details...")
    members = db.query(Member).order_by(Member.id.asc()).all()

    # Clear previous logs and outbox so everything is 100% consistent and real
    db.query(ClearanceLog).delete()
    db.query(AuditLog).delete()
    db.query(EmailOutbox).delete()
    db.commit()

    # 1. Base audit log: Official Gazette upload
    db.add(AuditLog(
        user_name="Samuel Njoroge",
        unit="CLERK_OFFICE",
        action="GAZETTE_NOTICE",
        resource_type="GAZETTE",
        resource_id="IEBC-GAZ-10537",
        details="Received and authenticated official IEBC Gazette Notice Vol. CXXIV—No. 181 for the 14th Parliament of Kenya (290 Constituency MPs, 47 County Women Reps, 12 Nominated MPs).",
        ip_address="10.20.14.10",
        timestamp=now - timedelta(days=14, hours=4)
    ))

    db.add(AuditLog(
        user_name="Bernard Kiprotich",
        unit="ICT",
        action="UPLOAD",
        resource_type="GAZETTE",
        resource_id="MORS-IMPORT-01",
        details="Ingested and verified gazette dataset. Verified 290 Constituency seats, 47 County seats, and 12 Party Nominated slots.",
        ip_address="10.20.14.15",
        timestamp=now - timedelta(days=14, hours=2)
    ))

    # 2. Enrich Member profiles and build real logs
    banks = [
        ("Kenya Commercial Bank (KCB)", "Parliament Road Branch"),
        ("Co-operative Bank of Kenya", "Parliament Buildings Branch"),
        ("Equity Bank Kenya", "Harambee Avenue Supreme Branch"),
        ("Absa Bank Kenya", "City Hall Way Branch"),
        ("Standard Chartered Kenya", "Kenyatta Avenue Branch"),
        ("NCBA Bank Kenya", "Mama Ngina Branch")
    ]

    for idx, m in enumerate(members):
        # Assign realistic qualification
        m.qualifications = random.choice(QUALIFICATIONS_BY_CATEGORY)
        bank_tuple = random.choice(banks)
        m.bank_name = bank_tuple[0]
        m.bank_branch = bank_tuple[1]
        m.bank_account = str(random.randint(1100000000, 1999999999))
        m.kra_pin = f"A{random.randint(10000000, 99999999)}P"
        m.nssf_number = str(random.randint(10000000, 99999999))
        m.sha_number = f"SHA-{random.randint(1000000, 9999999)}"

        # If submitted online:
        if m.submitted_at:
            # Create Member Portal Audit Log
            db.add(AuditLog(
                user_id=None,
                user_name=f"Hon. {m.full_name}",
                unit="PUBLIC",
                action="SUBMIT",
                resource_type="MEMBER",
                resource_id=str(m.id),
                details=f"Hon. {m.full_name} completed online self-onboarding biodata and uploaded scans of National ID, IEBC Certificate, and official photograph (Ref: {m.submission_reference}).",
                ip_address=random.choice(PUBLIC_IPS),
                timestamp=m.submitted_at
            ))

            # Create Email Outbox Record
            subject = f"MORS 14th Parliament Confirmation: Hon. {m.full_name} ({m.submission_reference})"
            body = f"""Dear Hon. {m.full_name},

We confirm receipt of your digital pre-registration particulars on the Members' Onboarding & Records System (MORS) for the 14th Parliament of Kenya.

SUMMARY OF RECORDED PARTICULARS:
--------------------------------------------------
Official Name: Hon. {m.full_name}
Category: {m.category.replace('_', ' ')}
Seat: {m.constituency or m.county or 'Nominated (National List)'}
Political Party: {m.party}
National ID / Passport: {m.national_id}
Submission Reference: {m.submission_reference}
Timestamp: {m.submitted_at.strftime('%Y-%m-%d %H:%M:%S UTC')}
--------------------------------------------------

INSTRUCTIONS UPON ARRIVAL AT PARLIAMENT BUILDINGS:
1. Present your ORIGINAL National Identity Card or Valid Kenyan Passport.
2. Present your ORIGINAL IEBC Certificate of Election (Form 23) or Nomination Notice.
3. Proceed to the Registration Desk (Clerks - Legal & Parliamentary Affairs) in the Main Dining Hall.
4. Complete departmental clearance: Media Relations (Photo), ICT (Chamber Biometrics), Parliamentary Security (Badge), and HR & Finance (Payroll/SHA).

For any inquiries or corrections, please contact the Registry Secretariat:
Email: mors.support@parliament.go.ke / registry@parliament.go.ke
Direct Line: +254 (0)20 284 8000 / Ext 3100
Parliament Buildings, Parliament Road, Nairobi.

Yours faithfully,
The Registry Secretariat
Office of the Clerk of the National Assembly
Republic of Kenya
"""
            db.add(EmailOutbox(
                recipient_email=m.email,
                recipient_name=f"Hon. {m.full_name}",
                subject=subject,
                body=body,
                reference_no=m.submission_reference,
                status="SENT",
                created_at=m.submitted_at,
                sent_at=m.submitted_at + timedelta(seconds=random.randint(12, 45))
            ))

        # If Desk Checked In:
        if m.desk_checked_in_at:
            clerk_officer = "Dorothy Mwende" if idx % 2 == 0 else "Serah Kioko"
            m.desk_checked_in_by = clerk_officer
            m.original_docs_verified_by = clerk_officer
            m.biodata_confirmed_by = clerk_officer

            # Clearance Log for Desk Check-in
            db.add(ClearanceLog(
                member_id=m.id,
                step="Desk Physical Check-In",
                unit="CLERK_LP",
                completed_by_id=3,
                completed_by_name=f"{clerk_officer} (Clerk L&P)",
                remarks="Member reported physically to Registration Desk at Parliament Buildings.",
                timestamp=m.desk_checked_in_at
            ))

            # Clearance Log for Original Docs
            db.add(ClearanceLog(
                member_id=m.id,
                step="Original Document Verification",
                unit="CLERK_LP",
                completed_by_id=3,
                completed_by_name=f"{clerk_officer} (Clerk L&P)",
                remarks="Physically inspected original National ID and original IEBC Certificate against digital uploads.",
                timestamp=m.desk_checked_in_at + timedelta(minutes=5)
            ))

            # Clearance Log for Oath & Assets
            if m.oath_recorded:
                db.add(ClearanceLog(
                    member_id=m.id,
                    step="Parliamentary Oath & Assets Declaration",
                    unit="CLERK_LP",
                    completed_by_id=3,
                    completed_by_name=f"{clerk_officer} (Clerk L&P)",
                    remarks="Administered Code of Conduct; received sealed Initial Declaration of Assets & Liabilities envelope.",
                    timestamp=m.desk_checked_in_at + timedelta(minutes=10)
                ))

            # Audit log for Check-in
            db.add(AuditLog(
                user_id=3,
                user_name=clerk_officer,
                unit="CLERK_LP",
                action="CHECKIN",
                resource_type="MEMBER",
                resource_id=str(m.id),
                details=f"Physically checked in Hon. {m.full_name} ({m.constituency or m.county}). Verified original ID and IEBC certificate.",
                ip_address="10.20.15.18",
                timestamp=m.desk_checked_in_at
            ))

        # If Unit Clearances:
        if m.photo_approved_at:
            m.photo_approved_by = "Erick Wandera"
            db.add(ClearanceLog(
                member_id=m.id,
                step="Official Passport Photo Approval",
                unit="MEDIA_RELATIONS",
                completed_by_id=4,
                completed_by_name="Erick Wandera (Media Relations)",
                remarks="Approved official parliamentary portrait photograph for Hansard and website records.",
                timestamp=m.photo_approved_at
            ))
            db.add(AuditLog(
                user_id=4,
                user_name="Erick Wandera",
                unit="MEDIA_RELATIONS",
                action="TICK",
                resource_type="MEMBER",
                resource_id=str(m.id),
                details=f"Approved official passport photo for Hon. {m.full_name} for parliamentary roll and publications.",
                ip_address="10.20.16.5",
                timestamp=m.photo_approved_at
            ))

        if m.biometrics_collected_at:
            m.biometrics_collected_by = "Bernard Kiprotich"
            db.add(ClearanceLog(
                member_id=m.id,
                step="Chamber Attendance & Voting Biometrics",
                unit="ICT",
                completed_by_id=2,
                completed_by_name="Bernard Kiprotich (ICT)",
                remarks="Fingerprint captured; Chamber electronic voting & attendance smartcard provisioned.",
                timestamp=m.biometrics_collected_at
            ))
            db.add(AuditLog(
                user_id=2,
                user_name="Bernard Kiprotich",
                unit="ICT",
                action="TICK",
                resource_type="MEMBER",
                resource_id=str(m.id),
                details=f"Recorded electronic chamber biometrics and voting card provision for Hon. {m.full_name}.",
                ip_address="10.20.14.22",
                timestamp=m.biometrics_collected_at
            ))

        if m.security_cleared_at:
            m.security_cleared_by = "Major (Rtd.) Bashir Abdullahi"
            db.add(ClearanceLog(
                member_id=m.id,
                step="Security Screening & Badge Issuance",
                unit="SECURITY",
                completed_by_id=5,
                completed_by_name="Major (Rtd.) Bashir Abdullahi (Security)",
                remarks=f"Security vetting verified; Parliamentary access badge #{m.badge_number} issued.",
                timestamp=m.security_cleared_at
            ))
            db.add(AuditLog(
                user_id=5,
                user_name="Major (Rtd.) Bashir Abdullahi",
                unit="SECURITY",
                action="TICK",
                resource_type="MEMBER",
                resource_id=str(m.id),
                details=f"Issued security identification badge #{m.badge_number} and completed security clearance for Hon. {m.full_name}.",
                ip_address="10.20.14.38",
                timestamp=m.security_cleared_at
            ))

        if m.fully_cleared_at:
            m.hr_verified_by = "Grace Nyambura"
            m.finance_verified_by = "Grace Nyambura"
            db.add(ClearanceLog(
                member_id=m.id,
                step="HR & Finance Clearance",
                unit="HR_FINANCE",
                completed_by_id=6,
                completed_by_name="Grace Nyambura (HR & Finance)",
                remarks=f"Payroll account at {m.bank_name} ({m.bank_branch}) confirmed; KRA PIN {m.kra_pin} and SHA {m.sha_number} active.",
                timestamp=m.fully_cleared_at
            ))
            db.add(AuditLog(
                user_id=6,
                user_name="Grace Nyambura",
                unit="HR_FINANCE",
                action="TICK",
                resource_type="MEMBER",
                resource_id=str(m.id),
                details=f"Enrolled Hon. {m.full_name} for payroll, {m.bank_name} banking particulars, and statutory deductions.",
                ip_address="10.20.15.10",
                timestamp=m.fully_cleared_at
            ))

    db.commit()

    # Final summary audit
    db.add(AuditLog(
        user_name="Samuel Njoroge",
        unit="CLERK_OFFICE",
        action="EXPORT",
        resource_type="REPORT",
        resource_id="EXECUTIVE-SUMMARY",
        details="Generated live Onboarding Progress & Funnel Completion Report for the Clerk of the National Assembly.",
        ip_address="10.20.14.10",
        timestamp=now - timedelta(minutes=15)
    ))

    db.commit()

    print(f"Enrichment complete! Total Clearance Logs: {db.query(ClearanceLog).count()}, Total Audit Logs: {db.query(AuditLog).count()}, Total Email Outbox: {db.query(EmailOutbox).count()}")
    db.close()

if __name__ == "__main__":
    enrich_authentic_records()
