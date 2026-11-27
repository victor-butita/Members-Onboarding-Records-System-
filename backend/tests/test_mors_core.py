import pytest
from fastapi.testclient import TestClient
from app.core.database import SessionLocal
from app.models.models import Member, User
from main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}

def test_login_success():
    res = client.post("/api/v1/auth/login", json={
        "username": "clerk.lp",
        "password": "Password123!"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["unit"] == "CLERK_LP"
    assert data["user"]["role"] == "SUPER_USER"

def test_portal_search():
    res = client.get("/api/v1/portal/search?q=Kariuki")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "full_name" in data[0]
        assert "category" in data[0]

def test_portal_prefill():
    res = client.get("/api/v1/portal/member/1")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 1
    assert "full_name" in data
    assert "party" in data

def test_dashboard_summary():
    # Login as clerk office to view dashboard
    login_res = client.post("/api/v1/auth/login", json={
        "username": "clerk.office",
        "password": "Password123!"
    })
    token = login_res.json()["access_token"]
    
    res = client.get("/api/v1/dashboards/summary", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert "funnel" in data
    assert data["funnel"]["total_gazetted"] == 349
    assert len(data["unit_progress"]) == 5

def test_demographic_insights():
    login_res = client.post("/api/v1/auth/login", json={
        "username": "clerk.office",
        "password": "Password123!"
    })
    token = login_res.json()["access_token"]
    
    res = client.get("/api/v1/dashboards/insights", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert "avg_age" in data
    assert "female_share_pct" in data
    assert "party_breakdown" in data

def test_clearance_unit_restrictions():
    # Media relations user should not be able to tick ICT biometrics
    login_res = client.post("/api/v1/auth/login", json={
        "username": "media.lead",
        "password": "Password123!"
    })
    token = login_res.json()["access_token"]
    
    res = client.post("/api/v1/clearance/ict/biometrics", json={
        "member_id": 1,
        "collected": True
    }, headers={"Authorization": f"Bearer {token}"})
    
    assert res.status_code == 403  # Forbidden for non-ICT

def _login(username):
    res = client.post("/api/v1/auth/login", json={
        "username": username,
        "password": "Password123!"
    })
    assert res.status_code == 200
    return res.json()["access_token"]

def _pdf_with_lines(lines):
    content = ["BT", "/F1 11 Tf", "48 740 Td"]
    for index, line in enumerate(lines):
        escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        if index:
            content.append("0 -16 Td")
        content.append(f"({escaped}) Tj")
    content.append("ET")
    stream = "\n".join(content).encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Count 1 /Kids [3 0 R] >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        (b"<< /Length %d >>\nstream\n" % len(stream)) + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, body in enumerate(objects, start=1):
        offsets.append(len(output))
        output += f"{number} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(output)
    output += f"xref\n0 {len(objects) + 1}\n".encode()
    output += b"0000000000 65535 f \n"
    for offset in offsets[1:]:
        output += f"{offset:010d} 00000 n \n".encode()
    output += (
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF"
    ).encode()
    return bytes(output)

def test_media_cannot_open_another_department_queue():
    token = _login("media.lead")
    res = client.get(
        "/api/v1/clearance/queue/ICT",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 403

def test_pdf_extracts_members_and_ignores_preamble():
    from app.services.gazette_service import parse_gazette_pdf
    pdf = _pdf_with_lines([
        "THE KENYA GAZETTE",
        "GAZETTE NOTICE NO. 170",
        "IN EXERCISE OF THE POWERS conferred upon the Commission by the Constitution of Kenya and the Elections Act",
        "MEMBERS OF THE NATIONAL ASSEMBLY",
        "OCHIENG  John Otieno  Nairobi  Embakasi East  Orange Democratic Movement",
        "COUNTY WOMAN REPRESENTATIVE",
        "CHEBET  Faith Wanjiku  Nakuru  United Democratic Alliance",
    ])
    items, warnings = parse_gazette_pdf(pdf)
    names = {item.full_name for item in items}
    assert "OCHIENG John Otieno" in names
    assert any(item.category == "WOMAN_REP" and "CHEBET" in item.surname for item in items)
    assert all("GAZETTE" not in item.surname.upper() for item in items)
    assert not any("EXERCISE" in item.full_name.upper() for item in items)
    assert warnings == [] or isinstance(warnings, list)

def test_preview_returns_the_full_member_list():
    token = _login("ict.lead")
    rows = ["Surname,Other Names,Constituency,County,Party,Category"]
    rows.extend([
        f"Testsurname{i},Othername{i},ZZ Seat {i},Nairobi,United Democratic Alliance,MP"
        for i in range(20)
    ])
    res = client.post(
        "/api/v1/gazette/preview",
        files={"file": ("notice.csv", "\n".join(rows), "text/csv")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_parsed"] == 20
    assert len(data["records"]) == 20
    assert len(data["sample_records"]) == 15

def test_overwrite_keeps_biodata_for_the_same_person():
    from app.core.database import SessionLocal
    from app.models.models import Member
    from app.api.routes.gazette import apply_gazette_notice
    from app.schemas.schemas import MemberGazetteItem

    db = SessionLocal()
    try:
        member = Member(
            surname="Zzkeep",
            other_names="Biodata",
            full_name="Zzkeep Biodata",
            category="MP",
            constituency="ZZ Keep Seat",
            county="Nairobi",
            party="Independent",
            national_id="ZZ-KEEP-100",
            email="zzkeep@example.com",
            stage="SUBMITTED_ONLINE",
            status="ACTIVE",
        )
        db.add(member)
        db.flush()
        same = MemberGazetteItem(
            surname="Zzkeep",
            other_names="Biodata",
            full_name="Zzkeep Biodata",
            category="MP",
            constituency="ZZ Keep Seat",
            county="Nairobi",
            party="United Democratic Alliance",
        )
        result = apply_gazette_notice(db, [same], "TEST-KEEP", True, False, False)
        db.flush()
        db.refresh(member)
        assert result["updated"] == 1
        assert member.national_id == "ZZ-KEEP-100"
        assert member.email == "zzkeep@example.com"
        assert member.party == "United Democratic Alliance"
        assert member.stage == "SUBMITTED_ONLINE"

        changed = MemberGazetteItem(
            surname="Zznew",
            other_names="Person",
            full_name="Zznew Person",
            category="MP",
            constituency="ZZ Keep Seat",
            county="Nairobi",
            party="Orange Democratic Movement",
        )
        replaced = apply_gazette_notice(db, [changed], "TEST-REPLACE", True, False, False)
        db.flush()
        db.refresh(member)
        assert replaced["replaced"] == 1
        assert member.status == "SUPERSEDED"
        assert member.national_id == "ZZ-KEEP-100"
        created = db.query(Member).filter(Member.full_name == "Zznew Person").one()
        assert created.stage == "GAZETTED"
        assert created.national_id is None
    finally:
        db.rollback()
        db.close()

def test_partial_overwrite_requires_confirmation():
    from app.core.database import SessionLocal
    from app.api.routes.gazette import apply_gazette_notice
    from app.schemas.schemas import MemberGazetteItem
    from fastapi import HTTPException

    db = SessionLocal()
    item = MemberGazetteItem(
        surname="Zzpartial",
        other_names="Notice",
        full_name="Zzpartial Notice",
        category="MP",
        constituency="ZZ Partial Seat",
        county="Nairobi",
        party="Independent",
    )
    try:
        apply_gazette_notice(db, [item], "TEST-PARTIAL", True, True, False)
        raise AssertionError("Partial overwrite should have been refused")
    except HTTPException as exc:
        assert exc.status_code == 400
    finally:
        db.rollback()
        db.close()

def test_desk_verification_marks_member_onboarded():
    from app.core.database import SessionLocal
    from app.models.models import Member

    db = SessionLocal()
    member = Member(
        surname="Zzonboard",
        other_names="Desk",
        full_name="Zzonboard Desk",
        category="MP",
        constituency="ZZ Onboard Seat",
        county="Nairobi",
        party="Independent",
        status="ACTIVE",
        stage="SUBMITTED_ONLINE",
    )
    db.add(member)
    db.commit()
    member_id = member.id
    db.close()
    try:
        token = _login("clerk.lp")
        res = client.post("/api/v1/desk/verify-documents", json={
            "member_id": member_id,
            "verified": True,
            "biodata_confirmed": True,
            "notes": "Originals matched the submitted particulars."
        }, headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert res.json()["stage"] == "DESK_CHECKED_IN"
    finally:
        cleanup = SessionLocal()
        cleanup.query(Member).filter(Member.id == member_id).delete()
        cleanup.commit()
        cleanup.close()
