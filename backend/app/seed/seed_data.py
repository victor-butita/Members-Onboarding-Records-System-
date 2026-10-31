import random
from datetime import datetime, timedelta, timezone
from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.models import User, Member, ClearanceLog, AuditLog, SystemSetting, utcnow

COUNTIES_AND_CONSTITUENCIES = [
    ("Nairobi", ["Westlands", "Parklands", "Dagoretti North", "Dagoretti South", "Langata", "Kibra", "Roysambu", "Kasarani", "Ruaraka", "Embakasi South", "Embakasi North", "Embakasi Central", "Embakasi East", "Embakasi West", "Makadara", "Kamukunji", "Starehe"]),
    ("Mombasa", ["Changamwe", "Jomvu", "Kisauni", "Nyali", "Likoni", "Mvita"]),
    ("Kwale", ["Msambweni", "Lungalunga", "Matuga", "Kinango"]),
    ("Kilifi", ["Kilifi North", "Kilifi South", "Kaloleni", "Rabai", "Ganze", "Malindi", "Magarini"]),
    ("Tana River", ["Garsen", "Galole", "Bura"]),
    ("Lamu", ["Lamu East", "Lamu West"]),
    ("Taita Taveta", ["Taveta", "Wundanyi", "Mwatate", "Voi"]),
    ("Garissa", ["Garissa Township", "Balambala", "Lagdera", "Dadaab", "Fafi", "Ijara"]),
    ("Wajir", ["Wajir North", "Wajir East", "Tarbaj", "Wajir West", "Eldas", "Wajir South"]),
    ("Mandera", ["Mandera West", "Banissa", "Mandera North", "Mandera South", "Mandera East", "Lafey"]),
    ("Marsabit", ["Moyale", "North Horr", "Saku", "Laisamis"]),
    ("Isiolo", ["Isiolo North", "Isiolo South"]),
    ("Meru", ["Igembe South", "Igembe Central", "Igembe North", "Tigania West", "Tigania East", "North Imenti", "Buuri", "Central Imenti", "South Imenti"]),
    ("Tharaka-Nithi", ["Maara", "Chuka/Igambang'ombe", "Tharaka"]),
    ("Embu", ["Manyatta", "Runyenjes", "Mbeere South", "Mbeere North"]),
    ("Kitui", ["Mwingi North", "Mwingi West", "Mwingi Central", "Kitui West", "Kitui Rural", "Kitui Central", "Kitui East", "Kitui South"]),
    ("Machakos", ["Masinga", "Yatta", "Kangundo", "Matungulu", "Kathiani", "Mavoko", "Machakos Town", "Mwala"]),
    ("Makueni", ["Mbooni", "Kilome", "Kaiti", "Makueni", "Kibwezi West", "Kibwezi East"]),
    ("Nyandarua", ["Kinangop", "Kipipiri", "Ol Kalou", "Ol Jorok", "Ndaragwa"]),
    ("Nyeri", ["Tetu", "Kieni", "Mathira", "Othaya", "Mukurweini", "Nyeri Town"]),
    ("Kirinyaga", ["Mwea", "Gichugu", "Ndia", "Kirinyaga Central"]),
    ("Murang'a", ["Kangema", "Mathioya", "Kiharu", "Kigumo", "Maragwa", "Kandara", "Gatanga"]),
    ("Kiambu", ["Gatundu South", "Gatundu North", "Juja", "Thika Town", "Ruiru", "Githunguri", "Kiambu", "Kiambaa", "Kabete", "Kikuyu", "Limuru", "Lari"]),
    ("Turkana", ["Turkana North", "Turkana West", "Turkana Central", "Loima", "Turkana South", "Turkana East"]),
    ("West Pokot", ["Kapenguria", "Sigor", "Kacheliba", "Pokot South"]),
    ("Samburu", ["Samburu West", "Samburu North", "Samburu East"]),
    ("Trans Nzoia", ["Kwanza", "Endebess", "Saboti", "Kiminini", "Cherangany"]),
    ("Uasin Gishu", ["Soy", "Turbo", "Moiben", "Ainabkoi", "Kapseret", "Kesses"]),
    ("Elgeyo/Marakwet", ["Marakwet East", "Marakwet West", "Keiyo North", "Keiyo South"]),
    ("Nandi", ["Tinderet", "Aldai", "Nandi Hills", "Chesumei", "Emgwen", "Mosop"]),
    ("Baringo", ["Tiaty", "Baringo North", "Baringo Central", "Baringo South", "Mogotio", "Eldama Ravine"]),
    ("Laikipia", ["Laikipia West", "Laikipia East", "Laikipia North"]),
    ("Nakuru", ["Molo", "Njoro", "Naivasha", "Gilgil", "Kuresoi South", "Kuresoi North", "Subukia", "Rongai", "Bahati", "Nakuru Town West", "Nakuru Town East"]),
    ("Narok", ["Kilgoris", "Emurua Dikirr", "Narok North", "Narok East", "Narok South", "Narok West"]),
    ("Kajiado", ["Kajiado North", "Kajiado Central", "Kajiado East", "Kajiado West", "Kajiado South"]),
    ("Kericho", ["Kipkelion East", "Kipkelion West", "Ainamoi", "Bureti", "Belgut", "Sigowet/Soin"]),
    ("Bomet", ["Sotik", "Chepalungu", "Bomet East", "Bomet Central", "Konoin"]),
    ("Kakamega", ["Lugari", "Likuyani", "Malava", "Lurambi", "Navakholo", "Mumias West", "Mumias East", "Matungu", "Butere", "Khwisero", "Shinyalu", "Ikolomani"]),
    ("Vihiga", ["Vihiga", "Sabatia", "Hamisi", "Luanda", "Emuhaya"]),
    ("Bungoma", ["Mount Elgon", "Sirisia", "Kabuchai", "Bumula", "Kanduyi", "Webuye West", "Webuye East", "Kimilili", "Tongaren"]),
    ("Busia", ["Teso North", "Teso South", "Nambale", "Matayos", "Butula", "Funyula", "Budalangi"]),
    ("Siaya", ["Ugenya", "Ugunja", "Alego Usonga", "Gem", "Bondo", "Rarieda"]),
    ("Kisumu", ["Kisumu East", "Kisumu West", "Kisumu Central", "Seme", "Nyando", "Muhoroni", "Nyakach"]),
    ("Homa Bay", ["Kasipul", "Kabondo Kasipul", "Karachuonyo", "Rangwe", "Homa Bay Town", "Ndhiwa", "Suba North", "Suba South"]),
    ("Migori", ["Rongo", "Awendo", "Suna East", "Suna West", "Uriri", "Nyatike", "Kuria West", "Kuria East"]),
    ("Kisii", ["Bonchari", "South Mugirango", "Bomachoge Borabu", "Bobasi", "Bomachoge Chache", "Nyaribari Masaba", "Nyaribari Chache", "Kitutu Chache North", "Kitutu Chache South"]),
    ("Nyamira", ["Kitutu Masaba", "West Mugirango", "North Mugirango", "Borabu"])
]

FIRST_NAMES_MALE = ["Allan", "Brian", "Charles", "David", "Emmanuel", "Francis", "George", "Hassan", "Isaac", "James", "Kevin", "Leonard", "Michael", "Nicholas", "Peter", "Robert", "Samuel", "Thomas", "Victor", "William"]
FIRST_NAMES_FEMALE = ["Alice", "Beatrice", "Catherine", "Dorcas", "Esther", "Faith", "Grace", "Hellen", "Irene", "Jane", "Joyce", "Lilian", "Mary", "Mercy", "Naomi", "Priscilla", "Rose", "Sarah", "Tabitha", "Winnie"]
SURNAMES = ["Kariuki", "Ochieng", "Mwangi", "Kimani", "Otieno", "Wambua", "Kiptoo", "Koech", "Chebet", "Njoroge", "Kamau", "Mutua", "Omondi", "Cheruiyot", "Kiprono", "Wafula", "Wekesa", "Mogaka", "Ondieki", "Ali", "Mohamed", "Abdi", "Nyaga", "Muriithi"]
PARTIES = [
    "United Democratic Alliance (UDA)",
    "Orange Democratic Movement (ODM)",
    "Jubilee Party (JP)",
    "Wiper Democratic Movement (WDM)",
    "Amani National Congress (ANC)",
    "Ford Kenya (FK)",
    "Independent"
]

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # 1. Seed System Settings
    settings_data = [
        ("PORTAL_OPEN", "true", "Controls if the public member self-service portal is accepting submissions"),
        ("PORTAL_CLOSING_DATE", "2027-08-15 23:59:59", "Official registration deadline for the 14th Parliament"),
        ("PARLIAMENT_TERM", "14th Parliament of Kenya", "Current Parliamentary term title"),
        ("REGISTRATION_YEAR", "2027", "Year of induction"),
        ("HELP_DESK_CONTACT", "mors.support@parliament.go.ke", "Registry contact email for corrections")
    ]
    for key, val, desc in settings_data:
        if not db.query(SystemSetting).filter(SystemSetting.key == key).first():
            db.add(SystemSetting(key=key, value=val, description=desc))
    
    # 2. Seed Default Unit Super Users & Staff
    default_users = [
        ("admin", "admin@parliament.go.ke", "Allan Kimani (Admin Lead)", "SYSTEM_ADMIN", "SUPER_USER"),
        ("ict.lead", "ict.admin@parliament.go.ke", "Bernard Kiprotich (ICT Officer)", "ICT", "SUPER_USER"),
        ("clerk.lp", "clerk.lp@parliament.go.ke", "Dorothy Mwende (Legal & Parliamentary Affairs)", "CLERK_LP", "SUPER_USER"),
        ("media.lead", "media.relations@parliament.go.ke", "Erick Wandera (Media Relations Officer)", "MEDIA_RELATIONS", "SUPER_USER"),
        ("security.lead", "security@parliament.go.ke", "Major R. Mutisya (Parliamentary Security)", "SECURITY", "SUPER_USER"),
        ("hr.finance", "hr.finance@parliament.go.ke", "Grace Nyambura (HR & Finance Officer)", "HR_FINANCE", "SUPER_USER"),
        ("clerk.office", "clerk.office@parliament.go.ke", "Samuel Njoroge (The Clerk of National Assembly)", "CLERK_OFFICE", "READ_ONLY"),
        ("auditor", "auditor@parliament.go.ke", "Internal Auditor General (Read-Only)", "AUDITOR", "READ_ONLY")
    ]
    
    default_password_hash = hash_password("Password123!")
    for username, email, full_name, unit, role in default_users:
        if not db.query(User).filter(User.username == username).first():
            db.add(User(
                username=username,
                email=email,
                full_name=full_name,
                hashed_password=default_password_hash,
                unit=unit,
                role=role,
                is_active=True,
                must_change_password=False,
                created_at=utcnow()
            ))
    db.commit()
    
    # 3. Seed 349 Members across 290 Constituency MPs, 47 Woman Reps, 12 Nominated
    if db.query(Member).count() == 0:
        print("Seeding 349 Members for 14th Parliament of Kenya...")
        all_members = []
        gazette_notice = "Vol. CXXIX - No. 165 (IEBC Gazette Notice 2027)"
        
        # 290 Constituency MPs
        constituency_tuples = []
        for county_name, consts in COUNTIES_AND_CONSTITUENCIES:
            for c in consts:
                constituency_tuples.append((county_name, c))
                
        # Trim or pad to exactly 290
        constituency_tuples = constituency_tuples[:290]
        
        for idx, (county, constituency) in enumerate(constituency_tuples):
            gender = "MALE" if random.random() > 0.18 else "FEMALE"
            first_name = random.choice(FIRST_NAMES_MALE if gender == "MALE" else FIRST_NAMES_FEMALE)
            surname = random.choice(SURNAMES)
            other_names = f"{first_name} {random.choice(SURNAMES)}"
            full_name = f"{surname} {other_names}"
            party = random.choice(PARTIES)
            is_returning = random.choice([True, False, False])
            
            all_members.append(Member(
                surname=surname,
                other_names=other_names,
                full_name=full_name,
                category="MP",
                constituency=constituency,
                county=county,
                party=party,
                gender=gender,
                gazette_notice_no=gazette_notice,
                status="ACTIVE",
                is_returning_member=is_returning,
                term_count=random.randint(2, 4) if is_returning else 1
            ))
            
        # 47 County Woman Representatives
        for county_name, _ in COUNTIES_AND_CONSTITUENCIES[:47]:
            first_name = random.choice(FIRST_NAMES_FEMALE)
            surname = random.choice(SURNAMES)
            other_names = f"{first_name} {random.choice(SURNAMES)}"
            full_name = f"{surname} {other_names}"
            party = random.choice(PARTIES)
            is_returning = random.choice([True, False])
            
            all_members.append(Member(
                surname=surname,
                other_names=other_names,
                full_name=full_name,
                category="WOMAN_REP",
                constituency=None,
                county=county_name,
                party=party,
                gender="FEMALE",
                gazette_notice_no=gazette_notice,
                status="ACTIVE",
                is_returning_member=is_returning,
                term_count=random.randint(2, 3) if is_returning else 1
            ))
            
        # 12 Nominated Members
        for i in range(12):
            gender = "FEMALE" if i % 2 == 0 else "MALE"
            first_name = random.choice(FIRST_NAMES_FEMALE if gender == "FEMALE" else FIRST_NAMES_MALE)
            surname = random.choice(SURNAMES)
            other_names = f"{first_name} {random.choice(SURNAMES)}"
            full_name = f"{surname} {other_names}"
            party = random.choice(PARTIES[:4])  # usually major parliamentary parties
            
            all_members.append(Member(
                surname=surname,
                other_names=other_names,
                full_name=full_name,
                category="NOMINATED",
                constituency=None,
                county=None,
                party=party,
                gender=gender,
                gazette_notice_no=gazette_notice,
                status="ACTIVE",
                is_returning_member=random.choice([True, False]),
                term_count=1
            ))
            
        # Add members to DB
        db.add_all(all_members)
        db.commit()
        
        # Populate realistic progression stages for testing dashboards
        all_db_members = db.query(Member).all()
        now = utcnow()
        banks = ["Kenya Commercial Bank (KCB)", "Equity Bank", "Co-operative Bank", "Absa Bank Kenya", "Standard Chartered"]
        
        for idx, m in enumerate(all_db_members):
            # Realistic age between 27 and 68
            birth_year = random.randint(1958, 1999)
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)
            m.date_of_birth = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
            m.national_id = f"{random.randint(11000000, 39999999)}"
            m.phone = f"+254 7{random.randint(10000000, 99999999)}"
            m.email = f"{m.surname.lower()}.{m.other_names.split()[0].lower()}@parliament.go.ke"
            m.kra_pin = f"A{random.randint(10000000, 99999999)}K"
            m.postal_address = f"P.O. Box {random.randint(100, 9000)}-00100, Nairobi"
            m.next_of_kin_name = f"Spouse / Kin of {m.full_name}"
            m.next_of_kin_relation = random.choice(["Spouse", "Brother", "Sister", "Son", "Daughter"])
            m.next_of_kin_phone = f"+254 7{random.randint(10000000, 99999999)}"
            
            # Stages distribution:
            # 75% submitted online
            # 50% desk checked in
            # 35% fully cleared
            if idx < 260: # Submitted online
                m.stage = "SUBMITTED_ONLINE"
                days_ago = random.randint(1, 12)
                m.submitted_at = now - timedelta(days=days_ago, hours=random.randint(1, 8))
                m.submission_reference = f"MORS-14P-{str(m.id).zfill(4)}"
                m.is_submission_locked = True
                m.id_document_path = f"/uploads/{m.id}_national_id_sample.pdf"
                m.iebc_cert_path = f"/uploads/{m.id}_iebc_cert_sample.pdf"
                m.passport_photo_path = f"/uploads/{m.id}_photo_sample.jpg"
                
            if idx < 175: # Desk checked in
                m.stage = "DESK_CHECKED_IN"
                days_ago = random.randint(0, 7)
                m.desk_checked_in_at = now - timedelta(days=days_ago, hours=random.randint(1, 5))
                m.desk_checked_in_by = "Dorothy Mwende (Clerk L&P)"
                m.original_docs_verified = True
                m.original_docs_verified_by = "Dorothy Mwende"
                m.original_docs_verified_at = m.desk_checked_in_at
                m.biodata_confirmed = True
                m.biodata_confirmed_by = "Dorothy Mwende"
                m.biodata_confirmed_at = m.desk_checked_in_at
                m.oath_recorded = True
                m.assets_declaration_filed = True
                
            if idx < 120: # Unit Clearances
                m.photo_approved = True
                m.photo_approved_by = "Erick Wandera (Media)"
                m.photo_approved_at = now - timedelta(days=random.randint(0, 5))
                m.biometrics_collected = True
                m.biometrics_collected_by = "Bernard Kiprotich (ICT)"
                m.biometrics_collected_at = now - timedelta(days=random.randint(0, 5))
                m.security_cleared = True
                m.security_cleared_by = "Major R. Mutisya"
                m.badge_number = f"NA-14P-{str(m.id).zfill(3)}"
                m.security_cleared_at = now - timedelta(days=random.randint(0, 4))
                m.hr_verified = True
                m.finance_verified = True
                m.bank_name = random.choice(banks)
                m.bank_account = str(random.randint(1000000000, 9999999999))
                m.bank_branch = "Parliament Road Branch"
                m.nssf_number = str(random.randint(10000000, 99999999))
                m.sha_number = f"SHA-{random.randint(1000000, 9999999)}"
                m.stage = "FULLY_CLEARED"
                m.fully_cleared_at = now - timedelta(days=random.randint(0, 3))
                
        db.commit()
        
        # Log initial audit
        db.add(AuditLog(
            user_name="SYSTEM_ADMIN",
            unit="SYSTEM_ADMIN",
            action="UPLOAD",
            resource_type="GAZETTE",
            resource_id="IEBC-2027",
            details="Loaded official 14th Parliament gazette notice (349 Members).",
            timestamp=now
        ))
        db.commit()
        print(f"Successfully seeded {len(all_db_members)} members and initialized clearance demo state.")
        
    db.close()

if __name__ == "__main__":
    seed_database()
