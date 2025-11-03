
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
# accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, abort

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.139.8.30/proj1part2
#
# For example, if you had username ab1234 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://ab1234:123123@34.139.8.30/proj1part2"
#
# Modify these with your own credentials you received from TA!
DATABASE_USERNAME = "wl2822"
DATABASE_PASSWRD = "234471"
DATABASE_HOST = "34.139.8.30"
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
# Commented out the example code - uncomment when you're ready to test with actual tables
"""
with engine.connect() as conn:
	create_table_command = ""
	CREATE TABLE IF NOT EXISTS test (
		id serial,
		name text
	)
	""
	res = conn.execute(text(create_table_command))
	insert_table_command = ""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace')""
	res = conn.execute(text(insert_table_command))
	# you need to commit for create, insert, update queries to reflect
	conn.commit()
"""


@app.before_request
def before_request():
	"""
	This function is run at the beginning of every web request 
	(every time you enter an address in the web browser).
	We use it to setup a database connection that can be used throughout the request.

	The variable g is globally accessible.
	"""
	try:
		g.conn = engine.connect()
	except:
		print("uh oh, problem connecting to database")
		import traceback; traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):
	"""
	At the end of the web request, this makes sure to close the database connection.
	If you don't, the database could run out of memory!
	"""
	try:
		g.conn.close()
	except Exception as e:
		pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
	"""
	Home page with database statistics
	"""
	# Get statistics from database
	try:
		patient_count = g.conn.execute(text('SELECT COUNT(*) FROM wl2822.patient')).scalar()
		admission_count = g.conn.execute(text('SELECT COUNT(*) FROM wl2822.admission')).scalar()
		prescription_count = g.conn.execute(text('SELECT COUNT(*) FROM wl2822.prescription')).scalar()
		image_count = g.conn.execute(text('SELECT COUNT(*) FROM wl2822.medical_images')).scalar()

		stats = {
			'patient_count': patient_count,
			'admission_count': admission_count,
			'prescription_count': prescription_count,
			'image_count': image_count
		}
	except Exception as e:
		print(f"Error getting stats: {e}")
		stats = {
			'patient_count': 0,
			'admission_count': 0,
			'prescription_count': 0,
			'image_count': 0
		}

	return render_template("home.html", stats=stats)

# ==========================================
# PATIENT ROUTES
# ==========================================

@app.route('/patients')
def patients():
	"""
	Patient list with search/filter functionality
	"""
	# Get filter parameters from URL
	subject_id = request.args.get('subject_id', type=int)
	sex = request.args.get('sex', '')
	race = request.args.get('race', '')
	min_age = request.args.get('min_age', type=int)
	max_age = request.args.get('max_age', type=int)

	# Build query with filters
	query = text("""
		SELECT
			p.subject_id,
			p.sex,
			p.date_of_birth,
			p.race,
			2110 - EXTRACT(YEAR FROM p.date_of_birth) as age,
			COUNT(a.hadm_id) as admission_count
		FROM wl2822.patient p
		LEFT JOIN wl2822.admission a ON p.subject_id = a.subject_id
		WHERE (:subject_id IS NULL OR p.subject_id = :subject_id)
			AND (:sex = '' OR p.sex = :sex)
			AND (:race = '' OR p.race = :race)
		GROUP BY p.subject_id, p.sex, p.date_of_birth, p.race
		HAVING (:min_age IS NULL OR 2110 - EXTRACT(YEAR FROM p.date_of_birth) >= :min_age)
			AND (:max_age IS NULL OR 2110 - EXTRACT(YEAR FROM p.date_of_birth) <= :max_age)
		ORDER BY p.subject_id
		LIMIT 100
	""")

	try:
		result = g.conn.execute(query, {
			'subject_id': subject_id,
			'sex': sex,
			'race': race,
			'min_age': min_age,
			'max_age': max_age
		})
		patients = result.fetchall()
	except Exception as e:
		print(f"Error fetching patients: {e}")
		patients = []

	return render_template("patients.html", patients=patients)


@app.route('/patient/<int:subject_id>')
def patient_detail(subject_id):
	"""
	Patient detail page with complete medical timeline
	SHOWCASE PAGE - Complex multi-table JOINs
	"""
	try:
		# 1. Get patient basic info
		patient_query = text("SELECT * FROM wl2822.patient WHERE subject_id = :subject_id")
		patient_result = g.conn.execute(patient_query, {'subject_id': subject_id})
		patient = patient_result.fetchone()

		if not patient:
			return "Patient not found", 404

		# 2. Get all admissions for this patient (chronological)
		admissions_query = text("""
			SELECT * FROM wl2822.admission
			WHERE subject_id = :subject_id
			ORDER BY admission_intime DESC
		""")
		admissions_result = g.conn.execute(admissions_query, {'subject_id': subject_id})
		admissions = admissions_result.fetchall()

		# 3. For each admission, get detailed information
		admission_details = []
		for admission in admissions:
			hadm_id = admission.hadm_id

			# Get diagnoses with condition names
			diagnoses_query = text("""
				SELECT ad.*, c.condition_name
				FROM wl2822.admission_diagnosis ad
				JOIN wl2822.condition c
					ON ad.icd_code = c.icd_code
					AND ad.icd_version = c.icd_version
				WHERE ad.hadm_id = :hadm_id
				ORDER BY ad.rank
			""")
			diagnoses = g.conn.execute(diagnoses_query, {'hadm_id': hadm_id}).fetchall()

			# Get prescriptions with medication details
			prescriptions_query = text("""
				SELECT p.*, m.name as medication_name, m.strength, m.form
				FROM wl2822.prescription p
				JOIN wl2822.medication m ON p.medication_id = m.medication_id
				WHERE p.hadm_id = :hadm_id
				ORDER BY p.start_time
				LIMIT 20
			""")
			prescriptions = g.conn.execute(prescriptions_query, {'hadm_id': hadm_id}).fetchall()

			# Get procedures with procedure names
			procedures_query = text("""
				SELECT pp.*, pr.procedure_name
				FROM wl2822.procedures_performed pp
				JOIN wl2822.procedures pr
					ON pp.icd_code = pr.icd_code
					AND pp.icd_version = pr.icd_version
				WHERE pp.hadm_id = :hadm_id
				ORDER BY pp.procedure_date
			""")
			procedures = g.conn.execute(procedures_query, {'hadm_id': hadm_id}).fetchall()

			# Get medical images
			images_query = text("""
				SELECT * FROM wl2822.medical_images
				WHERE hadm_id = :hadm_id
				ORDER BY acquisition_date
			""")
			images = g.conn.execute(images_query, {'hadm_id': hadm_id}).fetchall()

			# Get orders
			orders_query = text("""
				SELECT * FROM wl2822.orders
				WHERE hadm_id = :hadm_id
				ORDER BY order_time
				LIMIT 20
			""")
			orders = g.conn.execute(orders_query, {'hadm_id': hadm_id}).fetchall()

			# Compile all data for this admission
			admission_details.append({
				'admission': admission,
				'diagnoses': diagnoses,
				'prescriptions': prescriptions,
				'procedures': procedures,
				'images': images,
				'orders': orders
			})

		# Calculate patient age
		from datetime import date
		if patient.date_of_birth:
			today = date.today()
			age = today.year - patient.date_of_birth.year - ((today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day))
		else:
			age = None

		return render_template("patient_detail.html",
			patient=patient,
			age=age,
			admission_details=admission_details,
			total_admissions=len(admissions))

	except Exception as e:
		print(f"Error fetching patient details: {e}")
		import traceback
		traceback.print_exc()
		return f"Error loading patient: {str(e)}", 500


# ==========================================
# CONDITION ROUTES
# ==========================================

@app.route('/conditions')
def conditions():
	"""
	Condition analytics browser - SHOWCASE PAGE
	Displays conditions with patient counts and diagnosis statistics
	"""
	search = request.args.get('search', '')

	# Complex analytics query with JOINs and aggregations
	query = text("""
		SELECT
			c.icd_code,
			c.icd_version,
			c.condition_name,
			COUNT(DISTINCT ad.subject_id) as patient_count,
			COUNT(ad.hadm_id) as diagnosis_count,
			MIN(ad.diagnosed_on) as first_diagnosis,
			MAX(ad.diagnosed_on) as latest_diagnosis
		FROM wl2822.condition c
		LEFT JOIN wl2822.admission_diagnosis ad
			ON c.icd_code = ad.icd_code
			AND c.icd_version = ad.icd_version
		WHERE
			(:search = '' OR
			 LOWER(c.condition_name) LIKE LOWER(:search_pattern) OR
			 c.icd_code LIKE :search_pattern)
		GROUP BY c.icd_code, c.icd_version, c.condition_name
		ORDER BY patient_count DESC NULLS LAST, diagnosis_count DESC
		LIMIT 100
	""")

	try:
		search_pattern = f'%{search}%' if search else ''
		result = g.conn.execute(query, {
			'search': search,
			'search_pattern': search_pattern
		})
		conditions = result.fetchall()
	except Exception as e:
		print(f"Error fetching conditions: {e}")
		import traceback
		traceback.print_exc()
		conditions = []

	return render_template("conditions.html", conditions=conditions, search=search)


@app.route('/condition/<icd_code>/<int:icd_version>')
def condition_detail(icd_code, icd_version):
	"""
	Detailed view of a specific condition showing all diagnosed patients
	"""
	try:
		# Get condition info
		condition_query = text("""
			SELECT * FROM wl2822.condition
			WHERE icd_code = :icd_code AND icd_version = :icd_version
		""")
		condition_result = g.conn.execute(condition_query, {
			'icd_code': icd_code,
			'icd_version': icd_version
		})
		condition = condition_result.fetchone()

		if not condition:
			return "Condition not found", 404

		# Get all patients diagnosed with this condition
		patients_query = text("""
			SELECT
				p.subject_id,
				p.sex,
				p.date_of_birth,
				p.race,
				2110 - EXTRACT(YEAR FROM p.date_of_birth) as age,
				ad.hadm_id,
				ad.diagnosed_on,
				ad.rank,
				a.admission_intime,
				a.admission_type
			FROM wl2822.admission_diagnosis ad
			JOIN wl2822.patient p ON ad.subject_id = p.subject_id
			JOIN wl2822.admission a ON ad.hadm_id = a.hadm_id
			WHERE ad.icd_code = :icd_code AND ad.icd_version = :icd_version
			ORDER BY ad.diagnosed_on DESC, ad.rank
			LIMIT 200
		""")
		patients = g.conn.execute(patients_query, {
			'icd_code': icd_code,
			'icd_version': icd_version
		}).fetchall()

		# Get statistics
		stats_query = text("""
			SELECT
				COUNT(DISTINCT subject_id) as total_patients,
				COUNT(*) as total_diagnoses,
				AVG(rank) as avg_rank,
				MIN(diagnosed_on) as first_diagnosis,
				MAX(diagnosed_on) as latest_diagnosis
			FROM wl2822.admission_diagnosis
			WHERE icd_code = :icd_code AND icd_version = :icd_version
		""")
		stats = g.conn.execute(stats_query, {
			'icd_code': icd_code,
			'icd_version': icd_version
		}).fetchone()

		return render_template("condition_detail.html",
			condition=condition,
			patients=patients,
			stats=stats)

	except Exception as e:
		print(f"Error fetching condition details: {e}")
		import traceback
		traceback.print_exc()
		return f"Error loading condition: {str(e)}", 500


# ==========================================
# ADMISSION ROUTES
# ==========================================

@app.route('/admissions')
def admissions():
	"""
	Admission search and browse functionality
	"""
	# Get filter parameters
	hadm_id = request.args.get('hadm_id', type=int)
	subject_id = request.args.get('subject_id', type=int)
	admission_type = request.args.get('admission_type', '')
	admission_location = request.args.get('admission_location', '')
	from_date = request.args.get('from_date', '')
	to_date = request.args.get('to_date', '')

	# Build query with filters
	query = text("""
		SELECT
			a.*,
			p.sex,
			p.race,
			2110 - EXTRACT(YEAR FROM p.date_of_birth) as patient_age,
			COUNT(DISTINCT ad.icd_code) as diagnosis_count,
			COUNT(DISTINCT pr.prescription_id) as prescription_count
		FROM wl2822.admission a
		JOIN wl2822.patient p ON a.subject_id = p.subject_id
		LEFT JOIN wl2822.admission_diagnosis ad ON a.hadm_id = ad.hadm_id
		LEFT JOIN wl2822.prescription pr ON a.hadm_id = pr.hadm_id
		WHERE 1=1
			AND (:hadm_id IS NULL OR a.hadm_id = :hadm_id)
			AND (:subject_id IS NULL OR a.subject_id = :subject_id)
			AND (:admission_type = '' OR a.admission_type = :admission_type)
			AND (:admission_location = '' OR a.admission_location = :admission_location)
			AND (:from_date = '' OR a.admission_intime >= :from_date::timestamp)
			AND (:to_date = '' OR a.admission_intime <= :to_date::timestamp)
		GROUP BY a.hadm_id, a.subject_id, a.admission_intime, a.admission_outtime,
				 a.admission_type, a.admission_location, a.discharge_location,
				 p.sex, p.race, p.date_of_birth
		ORDER BY a.admission_intime DESC
		LIMIT 100
	""")

	try:
		result = g.conn.execute(query, {
			'hadm_id': hadm_id,
			'subject_id': subject_id,
			'admission_type': admission_type,
			'admission_location': admission_location,
			'from_date': from_date,
			'to_date': to_date
		})
		admissions = result.fetchall()
	except Exception as e:
		print(f"Error fetching admissions: {e}")
		import traceback
		traceback.print_exc()
		admissions = []

	# Get unique admission types and locations for filter dropdowns
	try:
		types_result = g.conn.execute(text("SELECT DISTINCT admission_type FROM wl2822.admission ORDER BY admission_type"))
		admission_types = [row[0] for row in types_result.fetchall()]

		locations_result = g.conn.execute(text("SELECT DISTINCT admission_location FROM wl2822.admission ORDER BY admission_location"))
		admission_locations = [row[0] for row in locations_result.fetchall()]
	except Exception as e:
		print(f"Error fetching filter options: {e}")
		admission_types = []
		admission_locations = []

	return render_template("admissions.html",
		admissions=admissions,
		admission_types=admission_types,
		admission_locations=admission_locations)


# ==========================================
# ANALYTICS DASHBOARD
# ==========================================

@app.route('/analytics')
def analytics():
	"""
	Comprehensive analytics dashboard with multiple aggregation queries
	"""
	try:
		# 1. Top 10 most common diagnoses
		top_diagnoses_query = text("""
			SELECT
				c.condition_name,
				c.icd_code,
				COUNT(DISTINCT ad.subject_id) as patient_count,
				COUNT(*) as total_diagnoses
			FROM wl2822.condition c
			JOIN wl2822.admission_diagnosis ad
				ON c.icd_code = ad.icd_code
				AND c.icd_version = ad.icd_version
			GROUP BY c.condition_name, c.icd_code
			ORDER BY patient_count DESC
			LIMIT 10
		""")
		top_diagnoses = g.conn.execute(top_diagnoses_query).fetchall()

		# 2. Top 10 most prescribed medications
		top_medications_query = text("""
			SELECT
				m.name as medication_name,
				m.strength,
				COUNT(*) as prescription_count
			FROM wl2822.medication m
			JOIN wl2822.prescription p ON m.medication_id = p.medication_id
			GROUP BY m.name, m.strength
			ORDER BY prescription_count DESC
			LIMIT 10
		""")
		top_medications = g.conn.execute(top_medications_query).fetchall()

		# 3. Admission statistics by type
		admission_stats_query = text("""
			SELECT
				admission_type,
				COUNT(*) as admission_count,
				COUNT(DISTINCT subject_id) as unique_patients,
				AVG(EXTRACT(days FROM (admission_outtime::timestamp - admission_intime::timestamp))) as avg_length_days
			FROM wl2822.admission
			WHERE admission_outtime IS NOT NULL
			GROUP BY admission_type
			ORDER BY admission_count DESC
		""")
		admission_stats = g.conn.execute(admission_stats_query).fetchall()

		# 4. Patient demographics breakdown
		demographics_query = text("""
			SELECT
				p.sex,
				p.race,
				COUNT(DISTINCT p.subject_id) as patient_count,
				AVG(2110 - EXTRACT(YEAR FROM p.date_of_birth)) as avg_age
			FROM wl2822.patient p
			LEFT JOIN wl2822.admission a ON p.subject_id = a.subject_id
			GROUP BY p.sex, p.race
			ORDER BY patient_count DESC
			LIMIT 15
		""")
		demographics = g.conn.execute(demographics_query).fetchall()

		# 5. Medical imaging statistics
		imaging_stats_query = text("""
			SELECT
				viewpoint,
				COUNT(*) as image_count,
				COUNT(DISTINCT subject_id) as patient_count
			FROM wl2822.medical_images
			GROUP BY viewpoint
			ORDER BY image_count DESC
		""")
		imaging_stats = g.conn.execute(imaging_stats_query).fetchall()

		# 6. Provider order statistics
		provider_stats_query = text("""
			SELECT
				p.provider_id,
				COUNT(DISTINCT o.hadm_id) as admissions_served,
				COUNT(o.poe_id) as total_orders,
				COUNT(DISTINCT o.order_type) as order_types
			FROM wl2822.provider p
			LEFT JOIN wl2822.orders o ON p.provider_id = o.order_provider_id
			GROUP BY p.provider_id
			ORDER BY total_orders DESC
			LIMIT 10
		""")
		provider_stats = g.conn.execute(provider_stats_query).fetchall()

		# 7. Monthly admission trends (last 12 months of data)
		monthly_trends_query = text("""
			SELECT
				TO_CHAR(admission_intime, 'YYYY-MM') as month,
				COUNT(*) as admission_count,
				COUNT(DISTINCT subject_id) as unique_patients
			FROM wl2822.admission
			GROUP BY TO_CHAR(admission_intime, 'YYYY-MM')
			ORDER BY month DESC
			LIMIT 12
		""")
		monthly_trends = g.conn.execute(monthly_trends_query).fetchall()

		# 8. Overall database statistics
		overall_stats = {
			'patient_count': g.conn.execute(text('SELECT COUNT(*) FROM wl2822.patient')).scalar(),
			'admission_count': g.conn.execute(text('SELECT COUNT(*) FROM wl2822.admission')).scalar(),
			'prescription_count': g.conn.execute(text('SELECT COUNT(*) FROM wl2822.prescription')).scalar(),
			'condition_count': g.conn.execute(text('SELECT COUNT(*) FROM wl2822.condition')).scalar(),
			'medication_count': g.conn.execute(text('SELECT COUNT(*) FROM wl2822.medication')).scalar(),
			'image_count': g.conn.execute(text('SELECT COUNT(*) FROM wl2822.medical_images')).scalar(),
			'provider_count': g.conn.execute(text('SELECT COUNT(*) FROM wl2822.provider')).scalar(),
			'procedure_count': g.conn.execute(text('SELECT COUNT(*) FROM wl2822.procedures_performed')).scalar()
		}

		return render_template("analytics.html",
			top_diagnoses=top_diagnoses,
			top_medications=top_medications,
			admission_stats=admission_stats,
			demographics=demographics,
			imaging_stats=imaging_stats,
			provider_stats=provider_stats,
			monthly_trends=monthly_trends,
			overall_stats=overall_stats)

	except Exception as e:
		print(f"Error loading analytics: {e}")
		import traceback
		traceback.print_exc()
		return f"Error loading analytics: {str(e)}", 500


# ==========================================
# MEDICATION ROUTES
# ==========================================

@app.route('/medications')
def medications():
	"""
	Medication catalog with search functionality
	"""
	search = request.args.get('search', '')
	form = request.args.get('form', '')

	# Build query with filters
	query = text("""
		SELECT
			m.medication_id,
			m.name,
			m.strength,
			m.form,
			COUNT(DISTINCT p.subject_id) as patient_count,
			COUNT(p.prescription_id) as prescription_count
		FROM wl2822.medication m
		LEFT JOIN wl2822.prescription p ON m.medication_id = p.medication_id
		WHERE
			(:search = '' OR LOWER(m.name) LIKE LOWER(:search_pattern))
			AND (:form = '' OR m.form = :form)
		GROUP BY m.medication_id, m.name, m.strength, m.form
		ORDER BY prescription_count DESC NULLS LAST, m.name
		LIMIT 100
	""")

	try:
		search_pattern = f'%{search}%' if search else ''
		result = g.conn.execute(query, {
			'search': search,
			'search_pattern': search_pattern,
			'form': form
		})
		medications = result.fetchall()

		# Get unique medication forms for filter dropdown
		forms_result = g.conn.execute(text("SELECT DISTINCT form FROM wl2822.medication WHERE form IS NOT NULL ORDER BY form"))
		medication_forms = [row[0] for row in forms_result.fetchall()]

	except Exception as e:
		print(f"Error fetching medications: {e}")
		import traceback
		traceback.print_exc()
		medications = []
		medication_forms = []

	return render_template("medications.html",
		medications=medications,
		medication_forms=medication_forms,
		search=search)


# ==========================================
# PRESCRIPTION ROUTES
# ==========================================

@app.route('/prescriptions')
def prescriptions():
	"""
	Prescription browser with filtering
	"""
	# Get filter parameters
	subject_id = request.args.get('subject_id', type=int)
	medication_name = request.args.get('medication_name', '')
	route = request.args.get('route', '')
	from_date = request.args.get('from_date', '')
	to_date = request.args.get('to_date', '')

	# Build query with filters
	query = text("""
		SELECT
			p.prescription_id,
			a.subject_id,
			p.hadm_id,
			m.name as medication_name,
			m.strength,
			m.form,
			p.dose,
			p.route,
			p.frequency,
			p.start_time,
			p.end_time,
			pat.sex,
			2110 - EXTRACT(YEAR FROM pat.date_of_birth) as patient_age
		FROM wl2822.prescription p
		JOIN wl2822.medication m ON p.medication_id = m.medication_id
		JOIN wl2822.admission a ON p.hadm_id = a.hadm_id
		JOIN wl2822.patient pat ON a.subject_id = pat.subject_id
		WHERE (:subject_id IS NULL OR a.subject_id = :subject_id)
			AND (:medication_name = '' OR LOWER(m.name) LIKE LOWER(:medication_pattern))
			AND (:route = '' OR p.route = :route)
			AND (:from_date = '' OR p.start_time >= :from_date::timestamp)
			AND (:to_date = '' OR p.start_time <= :to_date::timestamp)
		ORDER BY p.start_time DESC
		LIMIT 100
	""")

	try:
		medication_pattern = f'%{medication_name}%' if medication_name else ''
		result = g.conn.execute(query, {
			'subject_id': subject_id,
			'medication_name': medication_name,
			'medication_pattern': medication_pattern,
			'route': route,
			'from_date': from_date,
			'to_date': to_date
		})
		prescriptions = result.fetchall()

		# Get unique routes for filter dropdown
		routes_result = g.conn.execute(text("SELECT DISTINCT route FROM wl2822.prescription WHERE route IS NOT NULL ORDER BY route"))
		prescription_routes = [row[0] for row in routes_result.fetchall()]

	except Exception as e:
		print(f"Error fetching prescriptions: {e}")
		import traceback
		traceback.print_exc()
		prescriptions = []
		prescription_routes = []

	return render_template("prescriptions.html",
		prescriptions=prescriptions,
		prescription_routes=prescription_routes)


# ==========================================
# PROCEDURE ROUTES
# ==========================================

@app.route('/procedures')
def procedures():
	"""
	Procedure catalog with statistics
	"""
	search = request.args.get('search', '')
	icd_version = request.args.get('icd_version', type=int)

	# Build query with filters - similar to medications
	query = text("""
		SELECT
			pr.icd_code,
			pr.icd_version,
			pr.procedure_name,
			COUNT(DISTINCT pp.subject_id) as patient_count,
			COUNT(pp.hadm_id) as procedure_count,
			MIN(pp.procedure_date) as first_performed,
			MAX(pp.procedure_date) as last_performed
		FROM wl2822.procedures pr
		LEFT JOIN wl2822.procedures_performed pp
			ON pr.icd_code = pp.icd_code
			AND pr.icd_version = pp.icd_version
		WHERE
			(:search = '' OR
			 LOWER(pr.procedure_name) LIKE LOWER(:search_pattern) OR
			 pr.icd_code LIKE :search_pattern)
			AND (:icd_version IS NULL OR pr.icd_version = :icd_version)
		GROUP BY pr.icd_code, pr.icd_version, pr.procedure_name
		ORDER BY procedure_count DESC NULLS LAST, patient_count DESC
		LIMIT 100
	""")

	try:
		search_pattern = f'%{search}%' if search else ''
		result = g.conn.execute(query, {
			'search': search,
			'search_pattern': search_pattern,
			'icd_version': icd_version
		})
		procedures = result.fetchall()

	except Exception as e:
		print(f"Error fetching procedures: {e}")
		import traceback
		traceback.print_exc()
		procedures = []

	return render_template("procedures.html",
		procedures=procedures,
		search=search)


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
	# accessing form inputs from user
	name = request.form['name']

	# Commented out - replace with your actual database insert
	# passing params in for each variable into query
	# params = {}
	# params["new_name"] = name
	# g.conn.execute(text('INSERT INTO test(name) VALUES (:new_name)'), params)
	# g.conn.commit()

	print(f"Received name: {name}")  # For testing
	return redirect('/')


@app.route('/login')
def login():
	abort(401)
	# Your IDE may highlight this as a problem - because no such function exists (intentionally).
	# This code is never executed because of abort().
	this_is_never_executed()


if __name__ == "__main__":
	import click

	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8111, type=int)
	def run(debug, threaded, host, port):
		"""
		This function handles command line parameters.
		Run the server using:

			python server.py

		Show the help text using:

			python server.py --help

		"""

		HOST, PORT = host, port
		print("running on %s:%d" % (HOST, PORT))
		app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

run()
