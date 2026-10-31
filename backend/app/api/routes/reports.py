from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.models import Member, User
from app.services.report_service import get_report_data, export_members_csv
from app.api.deps import get_current_user

router = APIRouter(prefix="/reports", tags=["Printable Reports & Data Export"])

@router.get("/{report_type}")
def get_report(
    report_type: str,
    category: Optional[str] = Query(None),
    unit: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_report_data(db, report_type, category_filter=category, unit_filter=unit)

@router.get("/export/csv")
def export_csv(
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Member)
    if category and category != "ALL":
        query = query.filter(Member.category == category)
    members = query.order_by(Member.surname.asc()).all()
    
    csv_str = export_members_csv(members)
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=mors_members_export.csv"}
    )
