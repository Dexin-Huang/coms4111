# Flask Application Plan - Medical Records System
**Group:** Michael Lau (wl2822), Dexin Huang (dh3172)
**Database:** wl2822 schema on proj1part2

---

## Database Schema Overview

### Core Tables & Relationships:

```
PATIENT (400 rows)
├── subject_id (PK)
├── sex, date_of_birth, race
└── Has many ADMISSIONS

ADMISSION (2,147 rows) - Hospital stays
├── hadm_id (PK)
├── subject_id (FK → patient)
├── admission_intime, admission_outtime
├── admission_type, admission_location
├── admit_provider_id (FK → provider)
└── Has many: diagnoses, prescriptions, orders, procedures, images

PROVIDER (42,244 rows)
└── provider_id (PK)

CONDITION (112,107 rows) - Disease/diagnosis catalog
├── icd_code, icd_version (PK)
└── condition_name

ADMISSION_DIAGNOSIS (29,246 rows) - Links admissions to conditions
├── hadm_id, subject_id
├── icd_code, icd_version (FK → condition)
├── rank, diagnosed_on

PRESCRIPTION (88,901 rows)
├── prescription_id (PK)
├── hadm_id (FK → admission)
├── medication_id (FK → medication)
├── provider_id (FK → provider)
├── dose, route, frequency
└── start_time, end_time

MEDICATION (4,206 rows) - Medication catalog
├── medication_id (PK)
├── name, strength, form

ORDERS (225,025 rows)
├── poe_id (PK)
├── hadm_id, subject_id, order_provider_id
├── order_type, order_time

PROCEDURES (86,423 rows) - Procedure catalog
├── icd_code, icd_version (PK)
└── procedure_name

PROCEDURES_PERFORMED (3,168 rows)
├── procedure_performed_id (PK)
├── hadm_id, subject_id
├── icd_code, icd_version (FK → procedures)
└── procedure_date

MEDICAL_IMAGES (1,360 rows)
├── image_id (PK)
├── study_id, hadm_id, subject_id
├── acquisition_date, viewpoint

PATIENT_CONDITION (0 rows) - Empty table
```

---

## Mapping Original Proposal to Actual Schema

| Original Concept | Actual Implementation | Status |
|------------------|----------------------|--------|
| **Encounter** | `admission` | ✓ Implemented |
| **Surgery** | `procedures_performed` | ✓ Implemented |
| **EncounterDiagnosis** | `admission_diagnosis` | ✓ Implemented |
| **Prescription** | `prescription` | ✓ Similar structure |
| **ImageProduction** | `medical_images` | ✓ Simplified (no order link) |
| **EncounterParticipation** | Provider via `admit_provider_id` + `order_provider_id` | ⚠ Different structure |
| **PatientCondition** | `patient_condition` table | ✗ Empty (not used) |
| **ImagingOrder** | Part of `orders` table | ⚠ Combined with other orders |

---

## Planned Flask Application Features

### 1. **Home/Dashboard Page** (`/`)
- Quick stats: Total patients, admissions, prescriptions, images
- Search shortcuts
- Recent activity

### 2. **Patient Management** (`/patients`)

#### `/patients` - Patient List & Search
- Search by: subject_id, sex, race, age range, birth year
- Display: subject_id, sex, DOB, race, # of admissions
- Click patient → go to patient detail page

#### `/patient/<subject_id>` - Patient Detail & Timeline
**Most Important Page - Will feature in README**
- Patient demographics
- **Chronological timeline of all admissions:**
  - For each admission:
    - Admission details (dates, type, location)
    - Diagnoses (ICD codes, condition names, ranks)
    - Prescriptions (medications, doses, frequencies)
    - Procedures performed
    - Medical images
    - Orders placed
- Statistics: Total admissions, unique conditions, medications count

### 3. **Admission Search** (`/admissions`)
- Filter by:
  - Date range
  - Admission type
  - Location
  - Has diagnosis (specific ICD code)
  - Provider ID
- Display results with patient info
- Link to patient detail page

### 4. **Condition/Diagnosis Browser** (`/conditions`)
**Second Most Important Page - Will feature in README**
- Search conditions by:
  - ICD code
  - Condition name (text search)
  - ICD version (9 or 10)
- Show for each condition:
  - ICD code, name
  - **How many patients diagnosed** (JOIN count)
  - **How many admissions** (JOIN count)
  - **Most recent diagnoses**
- Click condition → see all patients with that diagnosis
- **Analytics query:** Top 10 most common diagnoses

### 5. **Prescription Viewer** (`/prescriptions`)
- Search prescriptions by:
  - Patient ID
  - Medication name
  - Date range
  - Active prescriptions only
- Display: Patient, medication, dose, route, frequency, dates, provider
- Group by patient or by medication

### 6. **Medication Catalog** (`/medications`)
- Browse all medications
- Search by name, form
- Show: medication_id, name, strength, form
- For each medication: # of prescriptions, # of patients

### 7. **Provider Lookup** (`/providers`)
- Search by provider_id
- Show statistics for each provider:
  - # of admissions where they admitted patient
  - # of prescriptions ordered
  - # of general orders
- Most active providers

### 8. **Medical Images Browser** (`/images`)
- Filter by:
  - Patient
  - Date range
  - Viewpoint (ap, lateral, etc.)
  - Admission
- Display: image_id, study_id, acquisition_date, viewpoint
- Link to admission and patient

### 9. **Orders Viewer** (`/orders`)
- Search orders by:
  - Patient
  - Order type (Lab, Medications, General Care, etc.)
  - Date range
  - Provider
- Display: order details with patient and admission info

### 10. **Procedures Browser** (`/procedures`)
- Procedures catalog (86k procedures)
- Search by ICD code or name
- Show which procedures were actually performed
- Statistics: Most common procedures

### 11. **Analytics Dashboard** (`/analytics`)
**Important for README - Interesting Database Operations**
- **Query 1:** Patient demographics distribution (age groups, gender, race)
- **Query 2:** Admission patterns (by type, by month, average length of stay)
- **Query 3:** Top 10 most prescribed medications
- **Query 4:** Top 10 most common diagnoses
- **Query 5:** Medication prescribing patterns by provider
- **Query 6:** Imaging utilization (studies per patient, by modality)
- **Query 7:** Procedure trends over time
- **Query 8:** Patients with multiple chronic conditions (JOIN admission_diagnosis)

### 12. **Data Entry (Mock Operations)** (`/add`)
- Add new prescription (for testing)
- Add new order (mock)
- Form validation
- Success/error messages

---

## Technical Implementation Details

### Route Structure:
```python
/                          # Home dashboard
/patients                  # Patient search/list
/patient/<subject_id>      # Patient detail with full timeline
/admissions                # Admission search
/admission/<hadm_id>       # Admission detail
/conditions                # Condition browser
/condition/<icd_code>      # Condition detail with patients
/prescriptions             # Prescription search
/medications               # Medication catalog
/medication/<med_id>       # Medication detail
/providers                 # Provider lookup
/provider/<provider_id>    # Provider statistics
/images                    # Image browser
/orders                    # Orders viewer
/procedures                # Procedures catalog
/analytics                 # Analytics dashboard
/add/prescription          # Add prescription form
/add/order                 # Add order form
```

### Key SQL Patterns:

#### Patient Timeline (Most Complex):
```sql
-- Get all admissions for patient
SELECT * FROM wl2822.admission WHERE subject_id = :patient_id ORDER BY admission_intime;

-- For each admission, get diagnoses:
SELECT ad.*, c.condition_name
FROM wl2822.admission_diagnosis ad
JOIN wl2822.condition c ON ad.icd_code = c.icd_code AND ad.icd_version = c.icd_version
WHERE ad.hadm_id = :hadm_id
ORDER BY ad.rank;

-- Get prescriptions:
SELECT p.*, m.name, m.strength
FROM wl2822.prescription p
JOIN wl2822.medication m ON p.medication_id = m.medication_id
WHERE p.hadm_id = :hadm_id;

-- Get procedures:
SELECT pp.*, pr.procedure_name
FROM wl2822.procedures_performed pp
JOIN wl2822.procedures pr ON pp.icd_code = pr.icd_code AND pp.icd_version = pr.icd_version
WHERE pp.hadm_id = :hadm_id;

-- Get images:
SELECT * FROM wl2822.medical_images WHERE hadm_id = :hadm_id;

-- Get orders:
SELECT * FROM wl2822.orders WHERE hadm_id = :hadm_id;
```

#### Top Diagnoses (Analytics):
```sql
SELECT
    c.icd_code,
    c.condition_name,
    COUNT(DISTINCT ad.subject_id) as patient_count,
    COUNT(ad.hadm_id) as admission_count
FROM wl2822.admission_diagnosis ad
JOIN wl2822.condition c ON ad.icd_code = c.icd_code AND ad.icd_version = c.icd_version
GROUP BY c.icd_code, c.condition_name
ORDER BY patient_count DESC
LIMIT 10;
```

---

## Two Most Interesting Pages (for README)

### 1. Patient Timeline (`/patient/<subject_id>`)
**Why interesting:**
- Aggregates data from 6+ tables (admission, diagnosis, prescription, procedures, images, orders)
- Complex JOINs to show complete patient history
- Chronological ordering with nested data structures
- Real medical use case: reviewing complete patient chart

### 2. Condition Analytics (`/condition/<icd_code>`)
**Why interesting:**
- Shows prevalence of diagnosis across entire patient population
- Multi-table aggregation (COUNT DISTINCT for patients vs admissions)
- Demonstrates many-to-many relationship (patients ↔ conditions)
- Clinical analytics: understanding disease burden

---

## README Content Preview

### Parts Implemented:
✓ Patient records with demographics
✓ Admissions (as "encounters")
✓ Provider tracking
✓ Condition catalog with ICD codes
✓ Diagnoses per admission
✓ Prescription management
✓ Medication catalog
✓ Orders workflow
✓ Procedures performed
✓ Medical imaging records

### Parts Modified:
- **Ophthalmology-specific → General Medical:** Changed from eye clinic to general hospital records
- **Data source:** Used MIMIC-IV dataset instead of fabricated data (much larger scale)
- **Encounter → Admission:** Terminology change, same concept
- **Surgery → Procedures:** Broader scope, same relationship pattern
- **Provider participation:** Simplified to admit_provider + order_provider instead of many-to-many

### Parts Not Implemented:
- **PatientCondition table:** Empty in dataset (longitudinal problem list not used)
- **ImagingOrder explicit table:** Orders table combines all order types
- **Min-cardinality constraints:** Cannot enforce in PostgreSQL without triggers

### Why Changes:
- Real dataset provides better demonstration
- Larger scale (400 patients, 2100+ admissions vs planned 300-500)
- More realistic data distributions and relationships

---

## Development Priority

### Phase 1 (Core - Week 1):
1. Base templates
2. Patient list & search
3. Patient detail with timeline ✨
4. Admission search

### Phase 2 (Important - Week 1):
5. Condition browser with analytics ✨
6. Prescription viewer
7. Medication catalog
8. Provider lookup

### Phase 3 (Additional - Week 2):
9. Images browser
10. Orders viewer
11. Procedures browser
12. Analytics dashboard

### Phase 4 (Polish - Final days):
13. Data entry forms
14. Testing & bug fixes
15. README
16. Deployment

---

## Next Steps:
1. Create base HTML template structure
2. Implement patient routes first (most important)
3. Build incrementally, testing each feature
4. Keep SQL queries simple and readable
5. Focus on functionality over UI appearance
