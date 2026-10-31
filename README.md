# Members' Onboarding & Records System (MORS)
**The National Assembly of Kenya · Digital Onboarding for the 14th Parliament**

Based on **System Paper Version 3.0 (October 2026)** presented to The Clerk of the National Assembly.

---

## 🏛️ System Architecture & Workflow

MORS digitizes and consolidates the four key stages of member onboarding into a single unified process for up to 350 Members (290 Constituency MPs, 47 County Woman Representatives, 12 Nominated Members, and Speaker *ex-officio*):

1. **Stage 1: Gazette Processing & Management**
   - Ingests the official IEBC Gazette Notice (Excel, CSV, or PDF).
   - Automatically parses headings (Surname, Other Names, Constituency, County, Party).
   - Validates constitutional seat allocations against targets: 290 MPs, 47 Woman Reps, 12 Nominated Members.
   - Handles corrigenda and by-election updates seamlessly without losing audit records.

2. **Stage 2: Public Member Self-Service Portal (`/portal`)**
   - One common link for all members.
   - Gazetted members search their name and claim their record.
   - Official Gazette details are pre-filled and locked (read-only).
   - Captures comprehensive biodata: DOB, National ID, Phone, Email, KRA PIN, Address, Qualifications, Next of Kin.
   - Uploads scans: National ID, IEBC Certificate, Official Passport Photo (max 5 MB, PDF/JPG/PNG).
   - Safeguards: One submission per member, unique National ID enforcement, honeypot spam protection, portal open/close toggles.
   - Generates official submission reference (`MORS-14P-XXXX`), printable confirmation slip, and queues confirmation email.

3. **Stage 3: Registration Desk Check-In (`/desk`)**
   - Managed by Clerks (Legal & Parliamentary Affairs - L&P).
   - Physical check-in and original document inspection against digital scans.
   - Ticks: Original documents verified, biodata confirmed, oath & code of conduct recorded, assets declaration filed.
   - Ability to reopen online submissions for members needing corrections.

4. **Stage 4: Multi-Unit Clearance Stations (`/clearance`)**
   - **Media Relations:** Passport photo quality inspection, approval tick, camera capture or replacement upload.
   - **ICT Directorate:** Chamber attendance and electronic voting biometrics collection tick.
   - **Parliamentary Security:** Badge number assignment, security vetting form upload, security clearance tick.
   - **HR & Finance:** Payroll, bank account verification (Bank, Branch, Account No), NSSF, SHA / SHIF verification tick.

5. **Stage 5: Executive Oversight & Statutory Reports (`/dashboard`, `/insights`, `/reports`)**
   - Real-time onboarding funnel, 14-day influx trend line, demographic insights (age brackets, youth %, female share %, party representation).
   - 8 statutory printable and exportable reports with clean print stylesheets.
   - Immutable audit trail tracking every upload, check-in, tick, edit, and status change with officer identity and timestamp.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.9+
- Node.js 18+ and npm

### 2. Start Backend (FastAPI)
```bash
cd "/Users/vbutita/Pacis Repos/mors/backend"
source .venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation (Swagger UI): **http://127.0.0.1:8000/docs**

### 3. Start Frontend (Vue 3 + Vite)
```bash
cd "/Users/vbutita/Pacis Repos/mors/frontend"
npm run dev
```
Frontend Web Portal: **http://localhost:5173**

---

## 👥 Mock Rehearsal User Accounts (Seed Data)

All accounts are pre-seeded for testing and demonstration:

| Unit / Department | Username | Password | Role / Permissions |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin` | `Password123!` | Global Super User |
| **Clerks (Legal & Parliamentary)** | `clerk.lp` | `Password123!` | Desk Check-in, Doc Verification, Oath, Assets |
| **Media Relations** | `media.lead` | `Password123!` | Official Passport Photo Approval & Camera |
| **ICT Directorate** | `ict.lead` | `Password123!` | Gazette Processing, Chamber Biometrics, Outbox |
| **Parliamentary Security** | `security.lead` | `Password123!` | Security Screening, Badge Issuance & Vetting |
| **HR & Finance** | `hr.finance` | `Password123!` | Payroll, Bank Details, NSSF, SHA/SHIF |
| **Office of the Clerk** | `clerk.office` | `Password123!` | Executive Live Oversight & All Reports (Read-Only) |
| **Independent Auditor** | `auditor` | `Password123!` | Audit Logs, Reports & Compliance (Read-Only) |

---

## 🧪 Running Automated Tests

Run backend unit and integration tests:
```bash
cd "/Users/vbutita/Pacis Repos/mors/backend"
PYTHONPATH=. .venv/bin/pytest tests/
```
All 7 core test suites verify role gating, gazette ingestion, member portal validation, and dashboard calculations.
