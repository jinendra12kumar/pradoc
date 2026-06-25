# Doctor Onboarding & Verification System — Walkthrough

## Summary

Built a complete Doctor Onboarding and Verification System for PraDoc with 8 new database tables, 15 API endpoints, a 6-step React wizard, automated verification scoring, and fraud detection.

---

## Backend Changes

### New Files Created

| File | Purpose |
|---|---|
| [doctor.py](file:///d:/python%20FullStack/pradoc/backend/models/doctor.py) | 8 SQLAlchemy models + 10 enums |
| [doctor.py](file:///d:/python%20FullStack/pradoc/backend/schemas/doctor.py) | 20+ Pydantic V2 schemas |
| [doctor_repo.py](file:///d:/python%20FullStack/pradoc/backend/repositories/doctor_repo.py) | Data access layer |
| [doctor_service.py](file:///d:/python%20FullStack/pradoc/backend/services/doctor_service.py) | Business logic + scoring + fraud |
| [file_service.py](file:///d:/python%20FullStack/pradoc/backend/services/file_service.py) | File upload with SHA-256 hashing |
| [doctor.py](file:///d:/python%20FullStack/pradoc/backend/app/api/v1/doctor.py) | 15 API endpoints |

### Modified Files

| File | Change |
|---|---|
| [models/__init__.py](file:///d:/python%20FullStack/pradoc/backend/models/__init__.py) | Export all new models |
| [router.py](file:///d:/python%20FullStack/pradoc/backend/app/api/v1/router.py) | Include doctor router |
| [config.py](file:///d:/python%20FullStack/pradoc/backend/core/config.py) | Added `UPLOAD_DIR` |
| [.env](file:///d:/python%20FullStack/pradoc/backend/.env) | Added `UPLOAD_DIR=./uploads` |
| [app/__init__.py](file:///d:/python%20FullStack/pradoc/backend/app/__init__.py) | Static file serving for uploads |

### Database Tables (all auto-created on startup)

1. `doctor_profiles` — personal + professional info + council/clinic verification fields
2. `doctor_qualifications` — MBBS/MD/MS/etc with college and year
3. `doctor_specializations` — primary + secondary specializations
4. `doctor_clinics` — clinic details + online consultation + verification fields
5. `doctor_availability` — day/time schedule per clinic
6. `doctor_documents` — file uploads with SHA-256 hash
7. `doctor_verification` — status + score + breakdown + admin review
8. `verification_flags` — fraud detection flags with severity

### API Endpoints (15 total)

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/doctor/reference-data` | Dropdown data for forms |
| GET | `/doctor/profile` | Full profile |
| PUT | `/doctor/profile/personal` | Step 1 |
| PUT | `/doctor/profile/professional` | Step 2 |
| POST/GET/DELETE | `/doctor/profile/qualifications` | Step 3 |
| PUT | `/doctor/profile/specializations` | Step 4 |
| POST/PUT/DELETE | `/doctor/profile/clinics` | Step 5 |
| POST/DELETE | `/doctor/profile/documents` | Step 6 |
| POST | `/doctor/profile/photo` | Profile photo |
| POST | `/doctor/profile/submit` | Submit for verification |
| GET | `/doctor/dashboard` | Dashboard data |
| GET | `/doctor/public/{id}` | Patient-facing profile |

### Verification Scoring Engine

| Criterion | Points |
|---|---|
| Registration Number | +20 |
| Qualification Added | +20 |
| Registration Certificate | +30 |
| Degree Certificate | +20 |
| Clinic Information | +10 |
| **Total** | **100** |

- Score ≥ 80 → **AUTO APPROVE**
- Score 50–79 → **UNDER_REVIEW**
- Score < 50 → **REJECTED**

### Fraud Detection

Runs on every `/profile/submit`:
- Duplicate registration number
- Duplicate document hash (SHA-256)
- Invalid graduation year
- Experience exceeds age

---

## Frontend Changes

### New Files

| File | Purpose |
|---|---|
| [doctorApi.js](file:///d:/python%20FullStack/pradoc/frontend/src/api/doctorApi.js) | API client |
| [doctor-onboarding.css](file:///d:/python%20FullStack/pradoc/frontend/src/pages/doctor/doctor-onboarding.css) | 500+ lines of premium CSS |
| [DoctorOnboarding.jsx](file:///d:/python%20FullStack/pradoc/frontend/src/pages/doctor/DoctorOnboarding.jsx) | Wizard container |
| [PersonalInfoStep.jsx](file:///d:/python%20FullStack/pradoc/frontend/src/pages/doctor/steps/PersonalInfoStep.jsx) | Photo, name, DOB, languages |
| [ProfessionalInfoStep.jsx](file:///d:/python%20FullStack/pradoc/frontend/src/pages/doctor/steps/ProfessionalInfoStep.jsx) | Reg number, council, experience |
| [QualificationsStep.jsx](file:///d:/python%20FullStack/pradoc/frontend/src/pages/doctor/steps/QualificationsStep.jsx) | Dynamic add/remove cards |
| [SpecializationsStep.jsx](file:///d:/python%20FullStack/pradoc/frontend/src/pages/doctor/steps/SpecializationsStep.jsx) | Chip selector (primary + secondary) |
| [PracticeInfoStep.jsx](file:///d:/python%20FullStack/pradoc/frontend/src/pages/doctor/steps/PracticeInfoStep.jsx) | Clinic + availability scheduler |
| [DocumentsStep.jsx](file:///d:/python%20FullStack/pradoc/frontend/src/pages/doctor/steps/DocumentsStep.jsx) | Upload cards with status |

### Modified Files

| File | Change |
|---|---|
| [DoctorDashboard.jsx](file:///d:/python%20FullStack/pradoc/frontend/src/pages/doctor/DoctorDashboard.jsx) | Full dashboard with completion ring, score breakdown, missing items |
| [App.jsx](file:///d:/python%20FullStack/pradoc/frontend/src/App.jsx) | Added `/doctor/onboarding` route |

---

## How to Test

1. Register as a doctor at `http://localhost:5173/auth/register`
2. Complete OTP verification
3. You'll be redirected to `/doctor/dashboard` → which redirects to `/doctor/onboarding`
4. Complete all 6 steps
5. Submit for verification → auto-approved if score ≥ 80
6. Dashboard shows completion ring, score breakdown, status

API docs available at `http://localhost:8000/docs`
