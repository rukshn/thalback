from flask import Flask
from flask import request
from flask import jsonify
import psycopg2
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists
from flask_cors import CORS, cross_origin
import json
import time


# urlparse.uses_netloc.append("postgres")
# url = urlparse.urlparse("postgresql://postgres:pos123@localhost/thalsys")

def connect(user,password,host,port,dbname):
	url = 'postgresql://{}:{}@{}:{}/{}'
	url = url.format(user, password, host, port, dbname)

	con = sqlalchemy.create_engine(url, client_encoding='utf8')

	meta = sqlalchemy.MetaData(bind=con, reflect=True)

	return con, meta

def connect_db():
	connection,meta = connect('postgres','pos123','localhost',5432,'thalsys')
	return connection,meta

def patient_exsists(clinic_number):
	connection, meta = connect_db()
	tbl_patient = meta.tables['patient_details']

	Session = sessionmaker(bind= connection)
	session = Session()

	select_patient = session.query(exists().where(tbl_patient.c.clinic_number== str(clinic_number))).scalar()
	
	if select_patient == True:
		return True
	else:
		return False

app = Flask('__FLASK_APP__')
CORS(app)

@app.route('/')
def index():
	connection,meta = connect_db()
	print meta

	return 'flask server'

@app.route('/add_new_patient', methods=['POST'])
def add_patient():
	connection,meta = connect_db()
	tbl_patient = meta.tables['patient_details']
	Session = sessionmaker(bind=connection)
	session = Session()

	content = request.get_json()

	select_patient = session.query(exists().where(tbl_patient.c.clinic_number== str(content['clinic_number']))).scalar()

	if select_patient == True:
		return 'patient_exsists'
	else:
		insert_record = {}
		insert_record['clinic_number'] = content['clinic_number']
		insert_record['first_name'] = content['first_name']
		insert_record['last_name'] = content['last_name']
		insert_record['birthday'] = content['xdob']
		insert_record['date_of_reg'] = content['xdor']
		insert_record['address'] = content['address']
		insert_record['district'] = content['district']
		insert_record['province'] = content['province']
		insert_record['telephone'] = content['telephone']
		insert_record['email'] = content['email']
		insert_record['staus'] = content['civil_status']
		insert_record['gname'] = content['g_name']
		insert_record['gcontact'] = content['g_contact']
		insert_record['gender'] = content['gender']
		insert_record['nic'] = content['id_number']
		insert_record['occupation'] = content['occupation']
		insert_record['religion'] = content['religion']

		result = connection.execute(tbl_patient.insert().returning(tbl_patient.c.id), insert_record)

		for id in result:
			ins_id = id[0]
			ptn_id = 1000 + ins_id

		update = tbl_patient.update().where(tbl_patient.c.id == ins_id).values(patient_id=ptn_id)
		connection.execute(update)

	return jsonify(user=ptn_id)

@app.route('/new_medical_details', methods=['post'])
def new_medical_details():
	connection, meta = connect_db()
	tbl_patient = meta.tables['patient_details']
	tbl_pmh = meta.tables['med_conditions']
	tbl_diabetes = meta.tables['diabetes']
	tbl_pth = meta.tables['hypopth']
	tbh_tsh = meta.tables['hypotsh']
	tbl_liverproblems = meta.tables['liver_problems']
	tbl_puberty = meta.tables['puberty_problems']
	Session = sessionmaker(bind=connection)
	session = Session()
	content = request.get_json()
	select_patient = session.query(exists().where(tbl_patient.c.patient_id == str(content['pid']))).scalar()

	if select_patient == True:
		if content['diabetes'] == True:
			diabetes_value = 1
		else:
			diabetes_value = 0

		if content['puberty'] == True:
			puberty_value = 1
		else:
			puberty_value = 0

		if content['altered_liver'] == True:
			altered_liver_value = 1
		else:
			altered_liver_value = 0

		if content['hypothyroid'] == True:
			hypothyroid_value = 1
		else:
			hypothyroid = 0

		if content['hypoparathyroid'] == True:
			hypoparathyroid_value = 1
		else:
			hypoparathyroid_value = 0
		
		curr_time =  int(time.time())

		tbl_patient_update= tbl_patient.update().where(tbl_patient.c.patient_id == content['pid']).values(dict(diabetes = diabetes_value, diabetes_dday = content['xddiabetes'], diabetes_mng = content['dmmng'], hypotsh = hypoparathyroid_value, hypotsh_dday = content['xtshdate'], hypotsh_mng = content['tshmng'], hypopth = hypoparathyroid_value, hypopth_dday = content['xpthdate'], hypopth_mng = content['pthmng'], liver = altered_liver_value, liver_dday = content['xliverdate'], liver_mng = content['livermng'], puberty = puberty_value, puberty_dday = content['xpubertydate'], puberty_mng = content['pubmng'], diagnosis = content['diagnosis'], ix_for_diagnosis = content['diagnosis_mode'], hb_at_diagnosis = content['hb_diagnosis'], diagnosis_age = content['diagnosis_age'], notes = content['notes'], up_time = curr_time))

		connection.execute(tbl_patient_update)

		med_conditions = []

		for pmhs in content['pmh']:
			# print pmhs['condition']
			med_condition = {}
			med_condition['patient_id'] = content['pid']
			med_condition['condition'] = pmhs['condition']
			med_condition['condition_date'] = pmhs['xcondate']
			med_condition['condition_management'] = pmhs['management']
			med_condition['management_uptime'] = int(time.time())

			med_conditions.append(med_condition)

		pmh_ins = tbl_pmh.insert().execute(med_conditions)

	return jsonify(user=content['pid'])


@app.route('/new_surgical_details', methods = ['post'])
def new_surgical_details():
	connection,meta = connect_db()
	tbl_patient = meta.tables['patient_details']
	Session = sessionmaker(bind= connection)
	session = Session()
	content = request.get_json()

	select_patient = session.query(exists().where(tbl_patient.c.patient_id == str(content['pid']))).scalar()

	if select_patient == True:
		if content['splenectomy'] == True:
			spleenectomy = 1
		else:
			spleenectomy = 0
		
		if content['cholecystectomy'] == True:
			cholecystectomy = 1
		else:
			cholecystectomy = 0

		if content['legulcer'] == True:
			has_legulcer = 1
		else:
			has_legulcer = 0

		if content['pathological_fracture'] == True
			has_fracture = 1
		else:
			has_fracture = 0

		curr_time =  int(time.time())
		tbl_patient_update = tbl_patient.update().where(tbl_patient.c.patient_id == content['pid']).values(dict(up_time = curr_time, spleen = spleenectomy, spleen_date = content['splenectomy_xdate'], path_fracture = has_fracture, chole = cholecystectomy, chole_date = content['cholecystectomy_xdate'], legulcer = has_legulcer, sur_notes = content['notes']))

		run_update = connection.execute(tbl_patient_update)
		
		if run_update:
			return jsonify(state = 200)
		else:
			return jsonify(state = 500)
	
@app.route('/new_tsh_data', method=['post'])
def new_tsh_data():
	connection, meta = connect_db()
	tbl_tsh = meta.tables['tbl_tsh'] #todo change table name 
	content = request.get_json()
	pid = content['patient_id']
	patient_exist = patient_exsists(pid)

	if patient_exist == True:
		tsh_details = {}
		tsh_details['pid'] = content['pid']
		tsh_details['investigation_date_x'] = content['investigation_date_x']
		tsh_details['ft3'] = conten['ft3']
		tsh_details['ft4'] = content['ft4']
		tsh_details['remarks'] = content['remarks']
		tsh_details['uptime'] = int(time.time())
	
		tsh_ins = tbl_tsh.insert().execute(tsh_details)

		return jsonify(state = 200)
	else:
		return jsonify(state = 500)

@app.route('/new_lft', method['post'])
def new_lft():
	connection, meta = connect_db()
	tbl_tsh = meta.tables['tbl_lft'] #todo change table name 
	content = request.get_json()
	pid = content['pid']
	patient_exist = patient_exsists(pid)

	if patient_exist == True:	
		lft_details = {}
		lft_details['patient_id'] = content['pid']
		lft_details['investigation_date_x'] = content['investigation_date_x']
		lft_details['billc'] = content['billc']
		lft_details['billuc'] = content['billuc']
		lft_details['sgpt'] = content['sgpt']
		lft_details['sgot'] = content['sgot']
		lft_details['alp'] = content['alp']
		lft_details['albumine'] = content['albumine']
		lft_details['globuline'] = content['globuline']
		lft_details['investigation_number'] = content['investigation_number']
		lft_details['uptime'] = int(time.time())

		lft_ins = tbl_tsh.insert().execute(lft_details)
		
		return jsonify(state = 200)
	else:
		return jsonify(state = 500)
	
@app.route('/new_hormone_investigation', method=['post'])
def new_hormone_investigation():
	connection, meta = connect_db()
	tbl_hormone = meta.tables['tbl_hormone'] #todo change table name 
	content = request.get_json()
	pid = content['pid']
	patient_exist = patient_exsists(pid)

	if patient_exist == True:
		horm_details = {}
		horm_details['patient_id'] = content['pid']
		horm_details['patieinvestigation_date_xnt_id'] = content['investigation_date_x']
		horm_details['remarks'] = content['remarks']
		horm_details['fsh'] = content['fsh']
		horm_details['lh'] = content['lh']
		horm_details['testosterone'] = content['testosterone']
		horm_details['sic'] = content['sic']
		horm_details['sip'] = content['sip']
		horm_details['invesgigation_number'] = content['invesgigation_number']
		horm_details['oestrodiol'] = content['oestrodiol']
		horm_details['uptime'] = int(time.time())

		horm_ins = tbl_hormone.insert().execute(horm_details)

		return jsonify(state = 200)
	else
		return jsonify(state = 500)

@app.route('/new_fbc', method=['post'])
def new_fbc():
	connection, meta = connect_db()
	tbl_fbc = meta.tables['tbl_fbc'] #todo change table name 
	content = request.get_json()
	pid = content['pid']
	patient_exist = patient_exsists(pid)

	if patient_exist == True:
		new_fbc = {}
		new_fbc['rbc'] = content['rbc'] 
		new_fbc['plt'] = content['plt'] 
		new_fbc['hbg'] = content['hbg'] 
		new_fbc['mcv'] = content['mcv'] 
		new_fbc['mch'] = content['mch'] 
		new_fbc['mchc'] = content['mchc']
		new_fbc['rdwcv'] = content['rdwcv']
		new_fbc['rdwsd'] = content['rdwsd']
		new_fbc['neu'] = content['neu']
		new_fbc['lym'] = content['lym']
		new_fbc['mono'] = content['mono']
		new_fbc['baso'] = content['baso']
		new_fbc['eosi'] = content['eosi']
		new_fbc['neup'] = content['neup']
		new_fbc['lymp'] = content['lymp']
		new_fbc['eosip'] = content['eosip']
		new_fbc['monop'] = content['monop']
		new_fbc['uptime'] = int(time.time())

		fbc_ins = tbl_fbc.insert().execute(new_fbc)

		return jsonify(state = 200)
	else:
		return jsonify(state = 500)

@app.route('/new_tx', method=['post'])
def new_tx():
	connection, meta = connect_db()
	tbl_newtx = meta.tables['tbl_newtx'] #todo change table name 
	content = request.get_json()
	pid = content['pid']
	patient_exist = patient_exsists(pid)

	if patient_exist == True:
		tx_info = {}
		tx_info['patient_id'] = content['pid'']
		tx_info['packs'] = content['packs']
		tx_info['reactions'] = content['reactions']
		tx_info['reaction_note'] = content['reaction_note']
		tx_info['tx_date'] = content['tx_date_x']
		tx_info['uptime'] = int(time.time())

		new_tx = tbl_newtx.insert().execute(tx_info)

		return jsonify(state = 200)
	else:
		return jsonify(state = 500)		

if __name__ == "__main__":
    app.run()
