import re
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Member, User
from app.schemas.schemas import GazettePreviewResponse, GazetteCommitRequest, MemberGazetteItem
from app.services.gazette_service import parse_gazette_spreadsheet, parse_gazette_pdf, preview_gazette
from app.api.deps import require_units, require_writer, log_audit

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

def _norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()

def _seat_key(category: str, constituency: str, county: str, full_name: str) -> str:
    cat = (category or "MP").upper()
    if cat == "WOMAN_REP":
        return "WOMAN_REP|" + (_norm(county) or _norm(full_name))
    if cat == "NOMINATED":
        return "NOMINATED|" + _norm(full_name)
    if cat == "SPEAKER":
        return "SPEAKER|" + _norm(full_name)
    return "MP|" + (_norm(constituency) or _norm(full_name))

def _same_person(left: str, right: str) -> bool:
    a, b = _norm(left), _norm(right)
    return bool(a) and a == b

def apply_gazette_notice(
    db: Session,
    items: list,
    gazette_notice_no: str,
    replace_existing_seats: bool,
    supersede_missing: bool,
    confirm_partial_overwrite: bool,
) -> dict:
    """Write a gazette notice onto the member register.

    Matching seats are overwritten. The same person keeps biodata and clearance.
    A different person on that seat supersedes the previous holder.
    When supersede_missing is set, active members left off the notice leave the register.
    """
    if not items:
        raise HTTPException(
            status_code=400,
            detail="No elected members were found in this notice. Nothing was written to the register."
        )

    active_members = db.query(Member).filter(Member.status == "ACTIVE").all()
    if (
        supersede_missing
        and len(active_members) >= 30
        and len(items) < len(active_members) * 0.5
        and not confirm_partial_overwrite
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                f"This notice lists {len(items)} members and the active register has {len(active_members)}. "
                "Confirm partial overwrite if everyone not listed should be marked superseded."
            ),
        )

    by_seat = {}
    for member in active_members:
        key = _seat_key(member.category, member.constituency, member.county, member.full_name)
        by_seat.setdefault(key, member)

    imported = updated = replaced = skipped = 0
    touched_ids = set()

    for item in items:
        full_name = (item.full_name or f"{item.surname} {item.other_names}").strip()
        key = _seat_key(item.category, item.constituency, item.county, full_name)
        existing = by_seat.get(key)

        if existing and existing.id in touched_ids:
            continue

        if existing and not replace_existing_seats:
            touched_ids.add(existing.id)
            skipped += 1
            continue

        if existing and _same_person(existing.full_name, full_name):
            existing.surname = item.surname
            existing.other_names = item.other_names
            existing.full_name = full_name
            existing.category = item.category
            existing.constituency = item.constituency
            existing.county = item.county
            existing.party = item.party
            existing.gazette_notice_no = gazette_notice_no
            existing.status = "ACTIVE"
            touched_ids.add(existing.id)
            updated += 1
            continue

        if existing:
            existing.status = "SUPERSEDED"
            existing.status_reason = (
                f"Seat overwritten by gazette notice {gazette_notice_no} ({full_name})."
            )
            touched_ids.add(existing.id)
            replaced += 1

        member = Member(
            surname=item.surname,
            other_names=item.other_names,
            full_name=full_name,
            category=item.category,
            constituency=item.constituency,
            county=item.county,
            party=item.party,
            gazette_notice_no=gazette_notice_no,
            stage="GAZETTED",
            status="ACTIVE",
        )
        db.add(member)
        db.flush()
        by_seat[key] = member
        touched_ids.add(member.id)
        imported += 1

    superseded = 0
    if supersede_missing:
        for member in active_members:
            if member.id not in touched_ids and member.status == "ACTIVE":
                member.status = "SUPERSEDED"
                member.status_reason = f"Not listed in gazette notice {gazette_notice_no}."
                superseded += 1

    return {
        "imported": imported,
        "updated": updated,
        "replaced": replaced,
        "skipped": skipped,
        "superseded": superseded,
    }

@router.post("/commit")
def commit_gazette(
    data: GazetteCommitRequest,
    request: Request,
    current_user: User = Depends(require_units(["ICT", "CLERK_LP"])),
    writer: User = Depends(require_writer),
    db: Session = Depends(get_db)
):
    result = apply_gazette_notice(
        db,
        data.items,
        data.gazette_notice_no,
        data.replace_existing_seats,
        data.supersede_missing,
        data.confirm_partial_overwrite,
    )
    db.commit()

    details = (
        f"Gazette Notice {data.gazette_notice_no}: {result['imported']} imported, "
        f"{result['updated']} overwritten in place, {result['replaced']} seats replaced, "
        f"{result['superseded']} superseded."
    )
    log_audit(db, current_user, "UPLOAD", "GAZETTE", data.gazette_notice_no, details, request)

    total_active = db.query(Member).filter(Member.status == "ACTIVE").count()
    return {
        "message": "Gazette notice uploaded and the member register was overwritten for the seats in this notice.",
        **result,
        "total_active": total_active,
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
