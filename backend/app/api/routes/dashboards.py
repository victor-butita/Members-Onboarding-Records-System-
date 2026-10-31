from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
import statistics
from dateutil import parser
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.models import Member, AuditLog, User
from app.schemas.schemas import DashboardResponse, DemographicInsights, FunnelStats, UnitProgressItem
from app.api.deps import get_current_user

router = APIRouter(prefix="/dashboards", tags=["Dashboards & Analytics"])

@router.get("/summary", response_model=DashboardResponse)
def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    active_members = db.query(Member).filter(Member.status == "ACTIVE").all()
    total = len(active_members) or 1
    
    submitted_online = sum(1 for m in active_members if m.submitted_at is not None or m.stage in ["SUBMITTED_ONLINE", "DESK_CHECKED_IN", "FULLY_CLEARED"])
    desk_checked_in = sum(1 for m in active_members if m.desk_checked_in_at is not None or m.stage in ["DESK_CHECKED_IN", "FULLY_CLEARED"])
    fully_cleared = sum(1 for m in active_members if m.stage == "FULLY_CLEARED")
    
    funnel = FunnelStats(
        total_gazetted=total,
        submitted_online=submitted_online,
        submitted_online_pct=round((submitted_online / total) * 100, 1),
        desk_checked_in=desk_checked_in,
        desk_checked_in_pct=round((desk_checked_in / total) * 100, 1),
        fully_cleared=fully_cleared,
        fully_cleared_pct=round((fully_cleared / total) * 100, 1)
    )
    
    # Unit Progress
    clerks_done = sum(1 for m in active_members if m.original_docs_verified)
    media_done = sum(1 for m in active_members if m.photo_approved)
    ict_done = sum(1 for m in active_members if m.biometrics_collected)
    security_done = sum(1 for m in active_members if m.security_cleared)
    hr_fin_done = sum(1 for m in active_members if m.hr_verified and m.finance_verified)
    
    unit_progress = [
        UnitProgressItem(unit="CLERK_LP", unit_name="Clerks (L&P) Original Docs", completed=clerks_done, pending=total-clerks_done, pct=round((clerks_done/total)*100, 1)),
        UnitProgressItem(unit="MEDIA_RELATIONS", unit_name="Media Relations Photo Approval", completed=media_done, pending=total-media_done, pct=round((media_done/total)*100, 1)),
        UnitProgressItem(unit="ICT", unit_name="ICT Chamber Biometrics", completed=ict_done, pending=total-ict_done, pct=round((ict_done/total)*100, 1)),
        UnitProgressItem(unit="SECURITY", unit_name="Security Clearance & Badge", completed=security_done, pending=total-security_done, pct=round((security_done/total)*100, 1)),
        UnitProgressItem(unit="HR_FINANCE", unit_name="HR & Finance Clearance", completed=hr_fin_done, pending=total-hr_fin_done, pct=round((hr_fin_done/total)*100, 1)),
    ]
    
    # Category Breakdown
    cat_breakdown = {}
    for cat in ["MP", "WOMAN_REP", "NOMINATED"]:
        cat_members = [m for m in active_members if m.category == cat]
        cat_total = len(cat_members)
        cat_breakdown[cat] = {
            "total": cat_total,
            "submitted_online": sum(1 for m in cat_members if m.submitted_at is not None),
            "checked_in": sum(1 for m in cat_members if m.desk_checked_in_at is not None),
            "fully_cleared": sum(1 for m in cat_members if m.stage == "FULLY_CLEARED")
        }
        
    # Recent Activity
    recent_audits = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(8).all()
    recent_activity = [
        {
            "id": a.id,
            "action": a.action,
            "user_name": a.user_name,
            "unit": a.unit,
            "details": a.details,
            "timestamp": a.timestamp.isoformat() if a.timestamp else None
        }
        for a in recent_audits
    ]
    
    # 14-day trend (past 14 days)
    today = datetime.now(timezone.utc).date()
    trend_map = {}
    for i in range(13, -1, -1):
        day_str = (today - timedelta(days=i)).strftime("%b %d")
        trend_map[day_str] = {"date": day_str, "online": 0, "desk": 0}
        
    for m in active_members:
        if m.submitted_at:
            m_date = m.submitted_at.date()
            d_str = m_date.strftime("%b %d")
            if d_str in trend_map:
                trend_map[d_str]["online"] += 1
        if m.desk_checked_in_at:
            d_date = m.desk_checked_in_at.date()
            d_str = d_date.strftime("%b %d")
            if d_str in trend_map:
                trend_map[d_str]["desk"] += 1
                
    trend_list = list(trend_map.values())
    
    # System alerts
    alerts = []
    if funnel.submitted_online_pct < 70:
        alerts.append({
            "type": "warning",
            "message": f"Online pre-registration is at {funnel.submitted_online_pct}% (Target is 70%+ before arrival)."
        })
    if funnel.fully_cleared_pct >= 90:
        alerts.append({
            "type": "success",
            "message": f"Induction target on track: {funnel.fully_cleared_pct}% of Members are fully cleared."
        })
    else:
        alerts.append({
            "type": "info",
            "message": f"{funnel.fully_cleared} of {funnel.total_gazetted} Members fully cleared across all units."
        })

    return DashboardResponse(
        funnel=funnel,
        unit_progress=unit_progress,
        category_breakdown=cat_breakdown,
        recent_activity=recent_activity,
        fourteen_day_trend=trend_list,
        alerts=alerts
    )

@router.get("/insights", response_model=DemographicInsights)
def get_demographics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    members = db.query(Member).filter(Member.status == "ACTIVE").all()
    total = len(members) or 1
    
    now_year = 2027
    ages = []
    brackets = {"under_35": 0, "35_44": 0, "45_54": 0, "55_64": 0, "65_plus": 0}
    
    for m in members:
        if m.date_of_birth:
            try:
                # Try parsing DOB
                dt = parser.parse(m.date_of_birth)
                age = now_year - dt.year
                if 20 <= age <= 100:
                    ages.append(age)
                    if age < 35: brackets["under_35"] += 1
                    elif age <= 44: brackets["35_44"] += 1
                    elif age <= 54: brackets["45_54"] += 1
                    elif age <= 64: brackets["55_64"] += 1
                    else: brackets["65_plus"] += 1
            except Exception:
                pass
                
    if not ages:
        ages = [47]  # default fallback
        
    avg_age = round(statistics.mean(ages), 1)
    median_age = round(statistics.median(ages), 1)
    min_age = min(ages)
    max_age = max(ages)
    
    # Gender
    female_count = sum(1 for m in members if (m.gender and m.gender.upper() == "FEMALE") or m.category == "WOMAN_REP")
    male_count = total - female_count
    female_pct = round((female_count / total) * 100, 1)
    
    # Youth (< 35)
    under_35_count = brackets["under_35"]
    under_35_pct = round((under_35_count / total) * 100, 1)
    
    # Term history
    first_term_count = sum(1 for m in members if not m.is_returning_member)
    returning_count = total - first_term_count
    first_term_pct = round((first_term_count / total) * 100, 1)
    returning_pct = round((returning_count / total) * 100, 1)
    
    # Party breakdown
    party_counts = {}
    for m in members:
        p = m.party or "Independent"
        party_counts[p] = party_counts.get(p, 0) + 1
        
    # Category breakdown
    category_counts = {}
    for m in members:
        c = m.category
        category_counts[c] = category_counts.get(c, 0) + 1
        
    return DemographicInsights(
        total_members=total,
        avg_age=avg_age,
        median_age=median_age,
        min_age=min_age,
        max_age=max_age,
        age_brackets=brackets,
        gender_counts={"FEMALE": female_count, "MALE": male_count},
        female_share_pct=female_pct,
        under_35_count=under_35_count,
        under_35_pct=under_35_pct,
        first_term_count=first_term_count,
        first_term_pct=first_term_pct,
        returning_count=returning_count,
        returning_pct=returning_pct,
        party_breakdown=party_counts,
        category_breakdown=category_counts
    )
