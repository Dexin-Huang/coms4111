# Work Split - Part 3 Flask Application
**Team:** Michael Lau (wl2822), Dexin Huang (dh3172)

---

## Work Division Strategy

Since **wl2822** did most of the heavy lifting on Part 2 (database setup, data loading), we'll split Part 3 so that:
- **wl2822** handles simpler, straightforward pages (catalog browsing, simple lists)
- **dh3172** handles complex queries, multi-table JOINs, and analytics

Both parts can be developed independently and merged later.

---

## WL2822's Tasks (Simpler Pages - ~6 features)

### Setup (Do First):
- [ ] Create basic HTML templates folder structure
- [ ] Create `base.html` with navigation bar
- [ ] Test that Flask runs with templates

### Feature 1: Home/Dashboard (`/`)
**Difficulty: ⭐ Easy**
- Simple stats display (4 COUNT queries)
- No JOINs needed
```sql
SELECT COUNT(*) FROM wl2822.patient;
SELECT COUNT(*) FROM wl2822.admission;
SELECT COUNT(*) FROM wl2822.prescription;
SELECT COUNT(*) FROM wl2822.medical_images;
```
- Display in a simple HTML page with cards/boxes
- Add links to other pages

**Files to create:**
- Update `server.py`: `/` route
- `templates/index.html`

---

### Feature 2: Medication Catalog (`/medications`)
**Difficulty: ⭐ Easy**
- Simple SELECT * from single table
- Optional: search by name (WHERE LIKE)
- Display: medication_id, name, strength, form
- Pagination if needed (LIMIT/OFFSET)

**Files to create:**
- `server.py`: `/medications` route
- `templates/medications.html`

**SQL:**
```sql
-- List all medications
SELECT * FROM wl2822.medication ORDER BY name LIMIT 50;

-- Search (optional)
SELECT * FROM wl2822.medication
WHERE name ILIKE :search_term
ORDER BY name LIMIT 50;
```

---

### Feature 3: Medication Detail (`/medication/<medication_id>`)
**Difficulty: ⭐⭐ Easy-Medium**
- Show one medication details
- Count how many prescriptions use it (one simple JOIN)

**SQL:**
```sql
-- Get medication
SELECT * FROM wl2822.medication WHERE medication_id = :med_id;

-- Count prescriptions
SELECT COUNT(*) FROM wl2822.prescription WHERE medication_id = :med_id;
```

**Files to create:**
- `server.py`: `/medication/<medication_id>` route
- `templates/medication_detail.html`

---

### Feature 4: Provider Lookup (`/providers`)
**Difficulty: ⭐ Easy**
- Search for provider by ID
- Display provider info
- No complex queries

**Files to create:**
- `server.py`: `/providers` route
- `templates/providers.html`

**SQL:**
```sql
SELECT * FROM wl2822.provider WHERE provider_id = :provider_id;
```

---

### Feature 5: Medical Images Browser (`/images`)
**Difficulty: ⭐⭐ Easy-Medium**
- List medical images with filters
- Simple WHERE clauses, no complex JOINs
- Filter by: subject_id, date range, viewpoint

**Files to create:**
- `server.py`: `/images` route
- `templates/images.html`

**SQL:**
```sql
SELECT * FROM wl2822.medical_images
WHERE 1=1
  AND (:subject_id IS NULL OR subject_id = :subject_id)
  AND (:viewpoint IS NULL OR viewpoint = :viewpoint)
ORDER BY acquisition_date DESC
LIMIT 50;
```

---

### Feature 6: Orders Viewer (`/orders`)
**Difficulty: ⭐⭐ Easy-Medium**
- List orders with simple filters
- Filter by: subject_id, order_type, date
- No complex JOINs

**Files to create:**
- `server.py`: `/orders` route
- `templates/orders.html`

**SQL:**
```sql
SELECT * FROM wl2822.orders
WHERE 1=1
  AND (:subject_id IS NULL OR subject_id = :subject_id)
  AND (:order_type IS NULL OR order_type = :order_type)
ORDER BY order_time DESC
LIMIT 100;
```

---

## DH3172's Tasks (Complex Pages - ~6 features)

### Feature 1: Base Template Structure
**Difficulty: ⭐⭐ Medium**
- Create clean base template with Bootstrap
- Navigation bar with all links
- Responsive layout
- Shared CSS/styling

**Files to create:**
- `templates/base.html` (foundation for all pages)
- `static/style.css` (optional)

---

### Feature 2: Patient List & Search (`/patients`)
**Difficulty: ⭐⭐⭐ Medium**
- Search with multiple filters (sex, race, age range)
- Calculate age from date_of_birth
- Display with admission counts (requires JOIN)

**Files to create:**
- `server.py`: `/patients` route
- `templates/patients.html`

**SQL:**
```sql
SELECT
    p.*,
    EXTRACT(YEAR FROM AGE(p.date_of_birth)) as age,
    COUNT(a.hadm_id) as admission_count
FROM wl2822.patient p
LEFT JOIN wl2822.admission a ON p.subject_id = a.subject_id
WHERE 1=1
  AND (:sex IS NULL OR p.sex = :sex)
  AND (:race IS NULL OR p.race = :race)
GROUP BY p.subject_id
ORDER BY p.subject_id
LIMIT 50;
```

---

### Feature 3: Patient Detail with Timeline (`/patient/<subject_id>`)
**Difficulty: ⭐⭐⭐⭐⭐ Very Hard (SHOWCASE PAGE)**
- **Most important page for README**
- Complete patient medical history
- Multiple complex queries:
  - Patient demographics
  - All admissions (chronological)
  - For each admission:
    - Diagnoses (JOIN condition table)
    - Prescriptions (JOIN medication table)
    - Procedures (JOIN procedures table)
    - Medical images
    - Orders
- Nested data structure
- Timeline visualization

**Files to create:**
- `server.py`: `/patient/<subject_id>` route (multiple queries)
- `templates/patient_detail.html` (complex layout)

**SQL Queries needed:**
```sql
-- 1. Patient info
SELECT * FROM wl2822.patient WHERE subject_id = :subject_id;

-- 2. All admissions
SELECT * FROM wl2822.admission
WHERE subject_id = :subject_id
ORDER BY admission_intime;

-- 3. For each admission - Diagnoses:
SELECT ad.*, c.condition_name, c.icd_code
FROM wl2822.admission_diagnosis ad
JOIN wl2822.condition c
  ON ad.icd_code = c.icd_code
  AND ad.icd_version = c.icd_version
WHERE ad.hadm_id = :hadm_id
ORDER BY ad.rank;

-- 4. For each admission - Prescriptions:
SELECT p.*, m.name, m.strength, m.form
FROM wl2822.prescription p
JOIN wl2822.medication m ON p.medication_id = m.medication_id
WHERE p.hadm_id = :hadm_id
ORDER BY p.start_time;

-- 5. For each admission - Procedures:
SELECT pp.*, pr.procedure_name
FROM wl2822.procedures_performed pp
JOIN wl2822.procedures pr
  ON pp.icd_code = pr.icd_code
  AND pp.icd_version = pr.icd_version
WHERE pp.hadm_id = :hadm_id
ORDER BY pp.procedure_date;

-- 6. For each admission - Images:
SELECT * FROM wl2822.medical_images
WHERE hadm_id = :hadm_id
ORDER BY acquisition_date;

-- 7. For each admission - Orders:
SELECT * FROM wl2822.orders
WHERE hadm_id = :hadm_id
ORDER BY order_time;
```

---

### Feature 4: Admission Search (`/admissions`)
**Difficulty: ⭐⭐⭐ Medium-Hard**
- Filter admissions by multiple criteria
- JOIN with patient for display
- Filter by: date range, type, location, provider

**Files to create:**
- `server.py`: `/admissions` route
- `templates/admissions.html`

**SQL:**
```sql
SELECT
    a.*,
    p.name as patient_name,
    p.sex,
    p.date_of_birth
FROM wl2822.admission a
JOIN wl2822.patient p ON a.subject_id = p.subject_id
WHERE 1=1
  AND (:admission_type IS NULL OR a.admission_type = :admission_type)
  AND (:location IS NULL OR a.admission_location ILIKE :location)
  AND (:date_from IS NULL OR a.admission_intime >= :date_from)
  AND (:date_to IS NULL OR a.admission_intime <= :date_to)
ORDER BY a.admission_intime DESC
LIMIT 100;
```

---

### Feature 5: Condition Browser & Analytics (`/conditions`)
**Difficulty: ⭐⭐⭐⭐ Hard (SHOWCASE PAGE)**
- **Second most important page for README**
- Browse conditions catalog
- Search by ICD code or name
- Show analytics: patient count, admission count
- Click condition → see all patients with it

**Files to create:**
- `server.py`: `/conditions` route
- `server.py`: `/condition/<icd_code>/<icd_version>` route
- `templates/conditions.html`
- `templates/condition_detail.html`

**SQL:**
```sql
-- List conditions with stats:
SELECT
    c.icd_code,
    c.icd_version,
    c.condition_name,
    COUNT(DISTINCT ad.subject_id) as patient_count,
    COUNT(ad.hadm_id) as diagnosis_count
FROM wl2822.condition c
LEFT JOIN wl2822.admission_diagnosis ad
  ON c.icd_code = ad.icd_code
  AND c.icd_version = ad.icd_version
WHERE (:search IS NULL OR c.condition_name ILIKE :search)
GROUP BY c.icd_code, c.icd_version, c.condition_name
HAVING COUNT(ad.hadm_id) > 0
ORDER BY diagnosis_count DESC
LIMIT 50;

-- Condition detail - all patients with this diagnosis:
SELECT
    p.subject_id,
    p.name,
    p.sex,
    p.date_of_birth,
    ad.diagnosed_on,
    ad.rank,
    a.admission_type
FROM wl2822.admission_diagnosis ad
JOIN wl2822.patient p ON ad.subject_id = p.subject_id
JOIN wl2822.admission a ON ad.hadm_id = a.hadm_id
WHERE ad.icd_code = :icd_code
  AND ad.icd_version = :icd_version
ORDER BY ad.diagnosed_on DESC;
```

---

### Feature 6: Analytics Dashboard (`/analytics`)
**Difficulty: ⭐⭐⭐⭐ Hard**
- Multiple complex aggregation queries
- Charts/tables of interesting statistics
- Top diagnoses, top medications, trends

**Files to create:**
- `server.py`: `/analytics` route
- `templates/analytics.html`

**SQL Queries:**
```sql
-- Top 10 diagnoses:
SELECT
    c.condition_name,
    c.icd_code,
    COUNT(DISTINCT ad.subject_id) as patient_count,
    COUNT(ad.hadm_id) as diagnosis_count
FROM wl2822.admission_diagnosis ad
JOIN wl2822.condition c
  ON ad.icd_code = c.icd_code
  AND ad.icd_version = c.icd_version
GROUP BY c.condition_name, c.icd_code
ORDER BY patient_count DESC
LIMIT 10;

-- Top 10 prescribed medications:
SELECT
    m.name,
    m.strength,
    COUNT(p.prescription_id) as prescription_count,
    COUNT(DISTINCT p.subject_id) as patient_count
FROM wl2822.prescription p
JOIN wl2822.medication m ON p.medication_id = m.medication_id
GROUP BY m.name, m.strength
ORDER BY prescription_count DESC
LIMIT 10;

-- Age distribution:
SELECT
    CASE
        WHEN EXTRACT(YEAR FROM AGE(date_of_birth)) < 18 THEN '0-17'
        WHEN EXTRACT(YEAR FROM AGE(date_of_birth)) < 30 THEN '18-29'
        WHEN EXTRACT(YEAR FROM AGE(date_of_birth)) < 50 THEN '30-49'
        WHEN EXTRACT(YEAR FROM AGE(date_of_birth)) < 65 THEN '50-64'
        ELSE '65+'
    END as age_group,
    COUNT(*) as patient_count
FROM wl2822.patient
GROUP BY age_group
ORDER BY age_group;

-- Admission type distribution:
SELECT
    admission_type,
    COUNT(*) as count
FROM wl2822.admission
GROUP BY admission_type
ORDER BY count DESC;
```

---

## Optional Features (If Time Permits)

### Either Person Can Do:

1. **Prescription Viewer** (`/prescriptions`) - ⭐⭐ Medium
   - List prescriptions with filters
   - JOIN patient + medication tables

2. **Procedures Browser** (`/procedures`) - ⭐⭐ Medium
   - Browse procedure catalog
   - Show which were performed (JOIN)

3. **Add Prescription Form** (`/add/prescription`) - ⭐⭐ Medium
   - Simple form with dropdowns
   - INSERT query

4. **Provider Statistics** (`/provider/<provider_id>`) - ⭐⭐⭐ Medium-Hard
   - Count admissions, prescriptions, orders by provider

---

## Coordination & Integration

### Shared Files:
- `server.py` - We'll both edit this, but different routes (no conflicts)
- `templates/base.html` - DH3172 creates first, wl2822 uses

### Git Workflow (if using):
```bash
# wl2822 works on: simple-pages branch
# dh3172 works on: complex-features branch
# Merge before submission
```

### Testing Together:
- Each person tests their own routes
- Final integration test before demo

---

## Summary

### WL2822 (Simpler - ~6 features):
1. ✅ Home dashboard
2. ✅ Medication catalog + detail
3. ✅ Provider lookup
4. ✅ Medical images browser
5. ✅ Orders viewer
6. ✅ Base HTML template setup

**Estimated Time:** 8-10 hours

### DH3172 (Complex - ~6 features):
1. ✅ Base template structure (Bootstrap/styling)
2. ✅ Patient list & search
3. ✅ **Patient timeline** (SHOWCASE - hardest)
4. ✅ Admission search
5. ✅ **Condition analytics** (SHOWCASE)
6. ✅ Analytics dashboard

**Estimated Time:** 15-20 hours

### Both Together:
- README writing
- Final testing
- Deployment to GCP

---

## Communication

**Before starting:**
- Confirm wl2822 is okay with this split
- Share this document
- Agree on template structure (navigation bar links)

**During development:**
- Quick check-in every 2-3 days
- Share progress
- Help if stuck

**Integration:**
- Meet to combine code
- Test all routes together
- Fix any conflicts

---

This split is fair because:
✓ wl2822 did Part 2 database work (heavy lifting)
✓ dh3172 handles complex SQL queries now
✓ Both contribute meaningful features
✓ Can work independently
✓ Clear deliverables for each person
