from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request, Response
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.models import Member, User, utcnow
from app.schemas.schemas import GazettePreviewResponse, GazetteCommitRequest, MemberGazetteItem
from app.services.gazette_service import parse_gazette_spreadsheet, parse_gazette_pdf, preview_gazette
from app.api.deps import require_units, log_audit

router = APIRouter(prefix="/gazette", tags=["Gazette Processing"])

@router.post("/preview", response_model=GazettePreviewResponse)
async def preview_gazette_file(
    file: UploadFile = File(...),
    current_user: User = Depends(require_units(["ICT", "CLERK_LP"]))
):
    filename = file.filename
    content = await file.read()
    
    if filename.lower().endswith(".pdf"):
        items, warnings = parse_gazette_pdf(content)
    elif filename.lower().endswith((".xlsx", ".xls", ".csv")):
        items, warnings = parse_gazette_spreadsheet(content, filename)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload Excel (.xlsx), CSV, or PDF.")
        
    return preview_gazette(items, warnings)

@router.post("/commit")
def commit_gazette(
    data: GazetteCommitRequest,
    request: Request,
    current_user: User = Depends(require_units(["ICT", "CLERK_LP"])),
    db: Session = Depends(get_db)
):
    imported_count = 0
    updated_count = 0
    
    for item in data.items:
        # Check if record for same seat exists
        existing = None
        if item.category == "MP" and item.constituency:
            existing = db.query(Member).filter(
                Member.category == "MP",
                Member.constituency.ilike(item.constituency)
            ).first()
        elif item.category == "WOMAN_REP" and item.county:
            existing = db.query(Member).filter(
                Member.category == "WOMAN_REP",
                Member.county.ilike(item.county)
            ).first()
        elif item.category == "NOMINATED":
            existing = db.query(Member).filter(
                Member.category == "NOMINATED",
                Member.full_name.ilike(item.full_name)
            ).first()
            
        full_name = item.full_name or f"{item.surname} {item.other_names}".strip()
        
        if existing and data.replace_existing_seats:
            # Corrigenda / seat update
            existing.surname = item.surname
            existing.other_names = item.other_names
            existing.full_name = full_name
            existing.party = item.party
            existing.gazette_notice_no = data.gazette_notice_no
            existing.status = "ACTIVE"
            updated_count += 1
        else:
            member = Member(
                surname=item.surname,
                other_names=item.other_names,
                full_name=full_name,
                category=item.category,
                constituency=item.constituency,
                county=item.county,
                party=item.party,
                gazette_notice_no=data.gazette_notice_no,
                stage="GAZETTED",
                status="ACTIVE"
            )
            db.add(member)
            imported_count += 1
            
    db.commit()
    
    details = f"Gazette Notice {data.gazette_notice_no}: {imported_count} imported, {updated_count} updated."
    log_audit(db, current_user, "UPLOAD", "GAZETTE", data.gazette_notice_no, details, request)
    
    return {
        "message": "Gazette notice processed successfully.",
        "imported": imported_count,
        "updated": updated_count,
        "total_active": db.query(Member).filter(Member.status == "ACTIVE").count()
    }

@router.get("/template")
def download_template():
    csv_content = (
        "Surname,Other Names,Constituency,County,Party,Category\n"
        "Ochola,John Otieno,Embakasi East,Nairobi,Orange Democratic Movement,MP\n"
        "Kamau,Faith Wanjiku,,Nakuru,United Democratic Alliance,WOMAN_REP\n"
        "Mutiso,David Kioko,,,Jubilee Party,NOMINATED\n"
    )
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=mors_gazette_template.csv"}
    )
