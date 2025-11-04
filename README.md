# COMS W4111 Project Part 3 - Medical Records Web Application

**Columbia University - Introduction to Databases (Fall 2025)**

**Team Members:**
- Michael Lau (wl2822)
- Dexin Huang (dh3172)

**Database:** `wl2822` schema on Google Cloud PostgreSQL
**Live Application:** http://34.139.8.30:8111 (once deployed)

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Important: Changes from Original Proposal](#important-changes-from-original-proposal)
3. [Database Schema](#database-schema)
4. [Application Features](#application-features)
5. [Showcase Pages](#showcase-pages)
6. [Running the Application Locally](#running-the-application-locally)
7. [Deployment to Google Cloud](#deployment-to-google-cloud)
8. [Technical Highlights](#technical-highlights)
9. [Team Contributions](#team-contributions)

---

## Project Overview

This web application provides a comprehensive interface for browsing and analyzing medical records from the **MIMIC-IV** (Medical Information Mart for Intensive Care) database. The application demonstrates complex SQL queries, multi-table JOINs, aggregation functions, and professional web development practices.

**Key Statistics:**
- **400 patients** with complete medical histories
- **2,147 hospital admissions** spanning multiple years
- **88,901 prescription records** with detailed medication information
- **12,910 medical conditions** catalogued with ICD codes
- **6,413 medical images** with metadata
- **4,982 healthcare providers** tracked

---

## Important: Changes from Original Proposal

### Original Proposal (Part 1)
Our initial proposal in Part 1 was for an **Ophthalmology Patient Management System** focused specifically on eye care, including:
- Ophthalmology-specific patient records
- Vision test results and measurements
- Eye disease diagnoses
- Specialized optical prescriptions
- Ophthalmic procedures

**Proposed Schema:** Custom-designed ophthalmology tables with fields like visual acuity, intraocular pressure, and retinal examination results.

### Actual Implementation (Parts 2 & 3)
**What We Built:** A comprehensive **General Medical Records System** using the MIMIC-IV dataset

### Why Did We Change?

**Reason 1: Data Availability and Quality**
- **MIMIC-IV** is a real, de-identified medical database from Beth Israel Deaconess Medical Center
- Contains actual patient data (anonymized) rather than synthetic/fabricated data
- Provides rich, complex relationships that better demonstrate database concepts
- Already well-structured and validated by medical informatics researchers

**Reason 2: Academic Value**
- Working with real-world medical data provides more authentic learning experience
- MIMIC-IV is widely used in academic research, making it more relevant
- Demonstrates ability to work with production-quality database schemas
- Better showcases complex SQL queries on meaningful, realistic data

**Reason 3: Scope and Complexity**
- MIMIC-IV's complexity (12 tables with intricate relationships) better demonstrates our database skills
- Ophthalmology-specific data would have been narrower in scope
- General medical records allow us to showcase more diverse query types
- Better alignment with the course's emphasis on complex JOINs and aggregations

**Reason 4: Team Decision**
- After completing Part 2 (database implementation), we realized the MIMIC-IV dataset offered:
  - More interesting analytics opportunities
  - Richer multi-table relationships to showcase
  - Better demonstration of SQL complexity
  - More practical real-world relevance

### What Stayed the Same

Despite the change in domain, we maintained the core project requirements:
- **Complex multi-table database schema** (12 tables, even more than originally proposed)
- **Multiple relationships** (one-to-many, many-to-many)
- **Comprehensive web interface** for data exploration
- **Advanced SQL queries** with JOINs, aggregations, and filtering
- **Two showcase pages** demonstrating query complexity (as required)

### Schema Comparison

**Original (Proposed):**
- 8 tables focused on ophthalmology
- Patient → Appointment → Exam → Prescription flow
- Specialized fields for eye care

**Actual (Implemented):**
- 12 tables covering general medical care
- Patient → Admission → Diagnoses/Prescriptions/Procedures/Images flow
- Comprehensive medical record structure

Both schemas demonstrate:
- Proper normalization
- Foreign key relationships
- One-to-many and many-to-many relationships
- Real-world data modeling

---

## Database Schema

Our database contains **12 interconnected tables** in the `wl2822` schema:

### Core Entities

**1. patient** - Patient demographic information
```sql
- subject_id (PK)
- sex, date_of_birth, race
```

**2. provider** - Healthcare providers
```sql
- provider_id (PK)
```

**3. medication** - Medication catalog
```sql
- medication_id (PK)
- name, strength, form
```

**4. condition** - Medical conditions catalog (ICD codes)
```sql
- icd_code, icd_version (PK)
- condition_name
```

**5. procedures** - Medical procedures catalog (ICD codes)
```sql
- icd_code, icd_version (PK)
- procedure_name
```

### Transactional Tables

**6. admission** - Hospital admissions
```sql
- hadm_id (PK)
- subject_id (FK → patient)
- admission_intime, admission_outtime
- admission_type, admission_location
```

**7. admission_diagnosis** - Diagnoses made during admissions
```sql
- hadm_id, icd_code, icd_version (PK)
- subject_id (FK → patient)
- diagnosed_on, rank
```

**8. prescription** - Medication prescriptions
```sql
- prescription_id (PK)
- subject_id, hadm_id (FK)
- medication_id (FK → medication)
- dose, route, frequency, start_time, end_time
```

**9. procedures_performed** - Procedures performed during admissions
```sql
- hadm_id, icd_code, icd_version (PK)
- subject_id (FK → patient)
- procedure_date
```

**10. orders** - Medical orders
```sql
- order_id (PK)
- hadm_id, subject_id (FK)
- order_provider_id (FK → provider)
- order_type, order_time
```

**11. medical_images** - Medical imaging records
```sql
- image_id (PK)
- subject_id, hadm_id (FK)
- study_id, viewpoint
- acquisition_date
```

**12. patient_condition** - Long-term patient conditions
```sql
- subject_id, icd_code, icd_version (PK)
```

### Key Relationships

- **One-to-Many:** Patient → Admissions → Diagnoses/Prescriptions/Procedures
- **Many-to-Many:** Patients ↔ Conditions (through patient_condition)
- **Many-to-Many:** Procedures ↔ Admissions (through procedures_performed)
- **Referential Integrity:** All foreign keys properly enforced

---

## Application Features

Our web application provides **10 comprehensive pages** for exploring medical data:

### 1. Homepage Dashboard
- Database statistics overview
- Quick search functionality
- Navigation to all features

### 2. Patient Directory
**Route:** `/patients`
- Search by patient ID, sex, race, age range
- Display all patients with admission counts
- Age calculation from date of birth

### 3. Patient Timeline **SHOWCASE PAGE #1**
**Route:** `/patient/<subject_id>`
- **Complete medical history for individual patients**
- **7 complex SQL queries** with multi-table JOINs
- Displays:
  - Patient demographics with calculated age
  - All hospital admissions (chronological)
  - Diagnoses with condition names (JOIN condition table)
  - Prescriptions with medication details (JOIN medication table)
  - Procedures performed (JOIN procedures table)
  - Medical images
  - Provider orders
- **Technical Complexity:** 6+ table JOINs in a single page load

### 4. Condition Analytics **SHOWCASE PAGE #2**
**Route:** `/conditions`
- **Medical condition analytics with aggregated statistics**
- **Complex GROUP BY query** with COUNT DISTINCT
- Shows per condition:
  - Number of unique patients diagnosed
  - Total diagnosis count across all admissions
  - First and most recent diagnosis dates
- Search by condition name or ICD code
- Sorted by prevalence (most common first)

### 5. Condition Detail
**Route:** `/condition/<icd_code>/<icd_version>`
- Individual condition analysis
- List all patients diagnosed with specific condition
- Statistical breakdown by demographics
- Diagnosis rank distribution

### 6. Admission Search
**Route:** `/admissions`
- Hospital admission browser
- Filter by: admission ID, patient ID, type, location, date range
- Aggregated diagnosis and prescription counts
- Quick statistics display

### 7. Analytics Dashboard
**Route:** `/analytics`
- **8 complex aggregation queries:**
  1. Top 10 most common diagnoses
  2. Top 10 most prescribed medications
  3. Admission statistics by type (with average length of stay)
  4. Patient demographics breakdown
  5. Medical imaging statistics
  6. Provider order volumes
  7. Monthly admission trends (time series)
  8. Overall database statistics
- Visual presentation with charts and tables

### 8. Medications Catalog
**Route:** `/medications`
- Browse all available medications
- Search by name, filter by form (tablet, injection, etc.)
- Usage statistics per medication
- Link to view all prescriptions for each medication

### 9. Prescriptions Browser
**Route:** `/prescriptions`
- Comprehensive prescription records
- Filter by: patient, medication name, route, date range
- Shows detailed dosage information
- Links to patient records

### 10. Procedures Catalog
**Route:** `/procedures`
- Medical procedures catalog with statistics
- Search by procedure name or ICD code
- Shows frequency and patient counts
- First/last performed dates

---

## Showcase Pages

As required by the project specifications, we have **two showcase pages** that demonstrate complex SQL queries:

### Showcase Page #1: Patient Timeline
**Route:** `/patient/<subject_id>` (e.g., `/patient/10020740`)

**Why This Is Complex:**

**SQL Queries (7 total):**

```python
# Query 1: Patient basic information
SELECT * FROM patient WHERE subject_id = :subject_id

# Query 2: All admissions (chronological)
SELECT * FROM admission
WHERE subject_id = :subject_id
ORDER BY admission_intime DESC

# Query 3: Diagnoses with condition names (JOIN)
SELECT ad.*, c.condition_name
FROM admission_diagnosis ad
JOIN condition c
  ON ad.icd_code = c.icd_code
  AND ad.icd_version = c.icd_version
WHERE ad.hadm_id = :hadm_id
ORDER BY ad.rank

# Query 4: Prescriptions with medication details (JOIN)
SELECT p.*, m.name, m.strength, m.form
FROM prescription p
JOIN medication m ON p.medication_id = m.medication_id
WHERE p.hadm_id = :hadm_id
ORDER BY p.start_time

# Query 5: Procedures with procedure names (JOIN)
SELECT pp.*, pr.procedure_name
FROM procedures_performed pp
JOIN procedures pr
  ON pp.icd_code = pr.icd_code
  AND pp.icd_version = pr.icd_version
WHERE pp.hadm_id = :hadm_id

# Query 6: Medical images
SELECT * FROM medical_images
WHERE hadm_id = :hadm_id

# Query 7: Provider orders
SELECT * FROM orders
WHERE hadm_id = :hadm_id
```

**Complexity Highlights:**
- **Multi-table JOINs:** Combines data from 6+ tables
- **Nested iteration:** Loops through admissions, then queries each admission's details
- **Multiple relationship types:** One-to-many, many-to-many through junction tables
- **Composite keys:** Handles multi-column JOINs (icd_code + icd_version)
- **Data aggregation:** Organizes hierarchical patient → admission → details structure

**Demonstrates:**
- Complex SQL JOINs
- Nested data structures
- Comprehensive patient view
- Real-world medical record complexity

**Try it:** Visit `/patient/10020740` to see a complete patient medical history

---

### Showcase Page #2: Condition Analytics
**Route:** `/conditions`

**Why This Is Complex:**

**SQL Query:**

```sql
SELECT
    c.icd_code,
    c.icd_version,
    c.condition_name,
    COUNT(DISTINCT ad.subject_id) as patient_count,
    COUNT(ad.hadm_id) as diagnosis_count,
    MIN(ad.diagnosed_on) as first_diagnosis,
    MAX(ad.diagnosed_on) as latest_diagnosis
FROM condition c
LEFT JOIN admission_diagnosis ad
    ON c.icd_code = ad.icd_code
    AND c.icd_version = ad.icd_version
WHERE
    (:search = '' OR
     LOWER(c.condition_name) LIKE LOWER(:search_pattern) OR
     c.icd_code LIKE :search_pattern)
GROUP BY c.icd_code, c.icd_version, c.condition_name
ORDER BY patient_count DESC NULLS LAST, diagnosis_count DESC
LIMIT 100
```

**Complexity Highlights:**
- **Aggregation functions:** COUNT, COUNT DISTINCT, MIN, MAX
- **GROUP BY:** Multi-column grouping
- **LEFT JOIN:** Includes conditions even if never diagnosed
- **Multiple aggregations:** Different counts for patients vs. diagnoses
- **Complex filtering:** Search across multiple fields
- **Sorting with NULL handling:** NULLS LAST for conditions without diagnoses

**Demonstrates:**
- Advanced GROUP BY with aggregations
- COUNT DISTINCT for unique patient counting
- LEFT JOIN semantics (conditions catalog vs. actual diagnoses)
- Statistical analysis across relationships
- Real-world medical analytics

**Additional Query (Condition Detail):**

```sql
SELECT
    p.subject_id,
    p.sex,
    p.race,
    EXTRACT(YEAR FROM AGE(p.date_of_birth)) as age,
    ad.hadm_id,
    ad.diagnosed_on,
    ad.rank,
    a.admission_intime,
    a.admission_type
FROM admission_diagnosis ad
JOIN patient p ON ad.subject_id = p.subject_id
JOIN admission a ON ad.hadm_id = a.hadm_id
WHERE ad.icd_code = :icd_code AND ad.icd_version = :icd_version
ORDER BY ad.diagnosed_on DESC, ad.rank
```

**Demonstrates:**
- 3-table JOIN
- Date calculations (AGE function)
- Filtering on composite keys

**Try it:** Visit `/conditions` and search for "hypertension" or "diabetes"

---

## Running the Application Locally

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Access to the Google Cloud PostgreSQL database

### Step 1: Clone/Extract the Project

```bash
cd /path/to/project/Part3
```

### Step 2: Set Up Virtual Environment

**On Windows:**
```bash
cd webserver
python -m venv venv
.\venv\Scripts\activate
```

**On macOS/Linux:**
```bash
cd webserver
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install flask sqlalchemy psycopg2-binary click
```

**Or using requirements.txt (if provided):**
```bash
pip install -r requirements.txt
```

### Step 4: Verify Database Credentials

Open `server.py` and confirm the database credentials:

```python
DATABASE_USERNAME = "wl2822"
DATABASE_PASSWRD = "234471"
DATABASE_HOST = "34.139.8.30"
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/proj1part2"
```

### Step 5: Run the Application

```bash
python server.py
```

You should see:
```
running on 0.0.0.0:8111
 * Running on http://127.0.0.1:8111
```

### Step 6: Access the Application

Open your web browser and navigate to:
```
http://127.0.0.1:8111
```

or

```
http://localhost:8111
```

---

## Deployment to Google Cloud

### Prerequisites

- Google Cloud VM instance (already set up)
- SSH access to the VM
- Installed: Python, pip, git

### Deployment Steps

**1. SSH into Google Cloud VM:**
```bash
gcloud compute ssh <your-vm-name> --zone=<your-zone>
```

**2. Clone/Upload the project:**
```bash
cd ~
# Upload via SCP or git clone
```

**3. Set up the environment:**
```bash
cd Part3/webserver
python3 -m venv venv
source venv/bin/activate
pip install flask sqlalchemy psycopg2-binary click
```

**4. Run the application:**

**Option A: Foreground (for testing):**
```bash
python server.py
```

**Option B: Background with nohup:**
```bash
nohup python server.py > flask.log 2>&1 &
```

**Option C: Using screen (recommended):**
```bash
screen -S flask
python server.py
# Press Ctrl+A, then D to detach
# To reattach: screen -r flask
```

**5. Configure firewall (if needed):**
```bash
gcloud compute firewall-rules create allow-flask \
    --allow tcp:8111 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow Flask app on port 8111"
```

**6. Access the deployed application:**
```
http://<your-vm-external-ip>:8111
```

### Production Considerations

For a production deployment, consider:
- Using **Gunicorn** or **uWSGI** instead of Flask's development server
- Setting up **Nginx** as a reverse proxy
- Enabling **HTTPS** with SSL certificates
- Setting up **systemd** service for automatic restart
- Implementing proper **logging** and **monitoring**

---

## Implementation Notes

### Age Calculation and Data Normalization

**Challenge:** The MIMIC-IV dataset uses anonymized dates that have been shifted to protect patient privacy. This results in:
- Birth years: 2011-2085
- Admission years: 2110-2211 (spanning 101 years)

**Problem:** Using age-at-admission calculations (`admission_year - birth_year`) would give ages ranging from 25 to 200 years, with an average of ~115 years - completely unrealistic.

**Solution:** We normalized all ages to a single reference year: **2110** (the earliest admission year in the dataset).

**Implementation:**
```sql
-- Age calculation used throughout the application:
2110 - EXTRACT(YEAR FROM p.date_of_birth) as age
```

**Result:**
- Realistic age range: 25-99 years
- Average age: ~60-65 years
- Consistent age values across all pages
- Ages represent "age at dataset start" rather than "age at admission"

**Where Applied:**
- Patient directory listing (server.py:158)
- Patient detail/timeline page (server.py:447)
- Condition detail page (server.py:378)
- Analytics dashboard demographics (server.py:563)
- Prescriptions browser (server.py:729)
- Age filtering in patient search (server.py:166-167)

**Rationale:**
While this doesn't show exact age at time of admission, it provides:
- Consistent, meaningful age values across the entire application
- Realistic statistical analysis (averages, distributions)
- Better user experience (no confusing 115+ year averages)
- Simple, maintainable calculation

This is a common approach when working with anonymized medical datasets where temporal relationships are preserved but absolute dates are shifted.

---

## Technical Highlights

### SQL Complexity

Our application demonstrates:

**1. Complex JOINs**
- Multi-table JOINs (6+ tables in patient timeline)
- Composite key JOINs (e.g., `icd_code + icd_version`)
- LEFT JOINs for optional relationships
- Multiple JOINs in single query

**2. Aggregation Functions**
- `COUNT(*)` - Total record counts
- `COUNT(DISTINCT ...)` - Unique entity counts
- `AVG()` - Average calculations
- `MIN()` / `MAX()` - Range analysis
- `GROUP BY` - Multi-column grouping

**3. Advanced SQL Features**
- Subqueries for complex filtering
- Date calculations (`EXTRACT`, `AGE`)
- String pattern matching (`LIKE`, `LOWER`)
- `ORDER BY` with `NULLS LAST`
- Parameterized queries (SQL injection prevention)

**4. Database Best Practices**
- Foreign key constraints
- Proper indexing on frequently queried columns
- Normalized schema (3NF)
- Referential integrity maintained

### Application Architecture

**Backend:**
- Flask web framework
- SQLAlchemy for database connections
- Prepared statements (parameterized queries)
- Connection pooling
- Error handling and logging

**Frontend:**
- Bootstrap 5 responsive design
- Jinja2 templating
- Mobile-friendly interface
- Form validation
- Dynamic filtering

**Security:**
- Parameterized queries prevent SQL injection
- Database credentials in configuration
- Input validation on all forms
- Error messages don't expose sensitive info

---

## To Do

**Remaining Pages:**

1. **Provider Lookup Page** (`/providers`)
   - [ ] List all providers with basic information
   - [ ] Search/filter by provider ID
   - [ ] Display order counts per provider
   - [ ] Link to orders placed by each provider

2. **Orders Browser Page** (`/orders`)
   - [ ] Browse all medical orders
   - [ ] Filter by: patient ID, admission ID, order type, date range
   - [ ] Display provider information (JOIN provider table)
   - [ ] Show order details and timestamps

3. **Medical Images Browser Page** (`/images`)
   - [ ] Display all medical imaging records
   - [ ] Filter by: patient ID, admission ID, study type
   - [ ] Show acquisition dates and viewpoint information
   - [ ] Link to patient records

**Additional Tasks:**
- [ ] **Deployment to Google Cloud** - Deploy application to VM, configure firewall
- [ ] **Final testing** - Test all pages end-to-end
- [ ] **Quality assurance** - Verify all queries return correct results

---

## Project Files

```
Part3/
├── webserver/
│   ├── server.py              # Main Flask application (830+ lines)
│   ├── templates/
│   │   ├── base.html          # Base template with navigation
│   │   ├── home.html          # Homepage dashboard
│   │   ├── patients.html      # Patient directory
│   │   ├── patient_detail.html # SHOWCASE #1: Patient timeline
│   │   ├── conditions.html    # SHOWCASE #2: Condition analytics
│   │   ├── condition_detail.html
│   │   ├── admissions.html    # Admission search
│   │   ├── analytics.html     # Analytics dashboard
│   │   ├── medications.html   # Medication catalog
│   │   ├── prescriptions.html # Prescription browser
│   │   └── procedures.html    # Procedures catalog
│   └── venv/                  # Virtual environment (not in git)
├── FLASK_APP_PLAN.md          # Development plan
├── WORK_SPLIT.md              # Team work division
├── PROGRESS_SUMMARY.md        # Detailed progress report
└── README.md                  # This file
```

---

## Database Statistics

Current database contains:
- **400** patients with complete demographics
- **2,147** hospital admissions
- **88,901** medication prescriptions
- **12,910** medical conditions (ICD codes)
- **5,115** unique medications
- **6,413** medical images
- **4,982** healthcare providers
- **Thousands** of procedures performed

All data is from the MIMIC-IV medical dataset (anonymized, real patient data).

---

## Acknowledgments

- **MIMIC-IV Dataset:** Johnson, A., Bulgarelli, L., Pollard, T., Horng, S., Celi, L. A., & Mark, R. (2023). MIMIC-IV (version 2.2). PhysioNet. https://doi.org/10.13026/6mm1-ek67
- **Columbia University:** COMS W4111 Course Staff
- **Flask Framework:** Pallets Projects
- **Bootstrap:** Twitter Bootstrap team

---

## Contact

For questions or issues:
- **Dexin Huang (dh3172):** dh3172@columbia.edu
- **Michael Lau (wl2822):** wl2822@columbia.edu

**Course:** COMS W4111.001 - Introduction to Databases
**Semester:** Fall 2025
**Institution:** Columbia University
