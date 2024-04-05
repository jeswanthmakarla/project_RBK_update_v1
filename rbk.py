#importing require libraries
import sqlite3
from functools import wraps
from flask import Flask, g, request, session, redirect, url_for, jsonify, render_template
import hashlib

#configuring the flask app and jinja env
app = Flask(__name__)
app.secret_key = 'my_admin_secret_key'
app.config['SESSION_COOKIE_NAME'] = 'rbk_app_session'
app.config['DATABASE'] = './database.db'

app.jinja_env.globals.update(format=format)


#function to create a thread connection to db
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    if 'db' in g:
        g.db.close()


#app's login_required decorator
def login_required(func):
    @wraps(func)
    def wraper(*args,**kwargs):
        if session.get('rbk_logged_in'):
            return func(*args, **kwargs)
        else:
            return redirect('/login')
    return wraper



#login route
@app.route('/login', methods=["GET","POST"])
def login():
    if not session.get('rbK_logged_in'):
        if request.method=='POST':
            form = request.form
            form_phone = form['username']
            form_password = hashlib.sha256(bytes(form['password'],'utf-8') ).hexdigest()

            con = get_db()
            cursor = con.execute(f'SELECT * FROM rbk_users WHERE phone={form_phone}')       #getting cred info from rbk_users table
            db_user = dict(cursor.fetchone())


            if form_password == db_user['password']:
                    session['rbk_logged_in'] = True
                    del db_user['password']
                    session['rbk_active_user'] = db_user
                    return redirect('/')
            else:
                return render_template('login', title='RBK', alert_script='<script>alert("Invalid login credentials. Retry again.")</script>', page='/rbk_reg')
        else:
            return render_template('login', title='RBK', alert_script='', page='/rbk_reg')
    else:
        return redirect('/')


#logout route
@app.route('/logout')
def logout():
    session.pop('rbk_logged_in', None)
    session.pop('rbk_active_user', None)
    return redirect('/login')


#for selecting mandals and villages in registration
@app.route('/get_place_info/<type_>')
def get_places(type_):
    con = get_db()
    if type_=='mandal':
        mandal = request.args.get('item_')
        cursor = con.execute(f'SELECT DISTINCT village FROM places WHERE mandal="{mandal}"')
        villages = [v for each in cursor.fetchall() for k,v in dict(each).items() ]

        return jsonify(villages)
    
    if type_ =='village':
        village = request.args.get('item_')
        cursor = con.execute(f'SELECT rbk_id, fullname FROM rbk_users WHERE village="{village}"')
        rbk_users = [dict(each) for each in cursor.fetchall()]

        return jsonify(rbk_users)


#signup route
@app.route('/signup')
def signup():
    return render_template('signup')




#rbk registration page
@app.route('/rbk_reg', methods=["POST","GET"])
def rbk_reg():
    if request.method=='GET':
        con = get_db()

        cursor = con.execute('SELECT DISTINCT mandal FROM places;')
        mandals = [v for each in cursor.fetchall() for k,v in dict(each).items() ]

        cursor = con.execute('SELECT village FROM places;')
        villages = [v for each in cursor.fetchall() for k,v in dict(each).items() ]

        return render_template('rbk_reg', title='RBK Registration form', reg_type='rbk_reg', mandals=mandals, villages=villages)        #rendering the show page along with fetched details
    
    if request.method=='POST':
        data = request.get_json()
        con = get_db()

        con.execute(f'INSERT INTO rbk_users (fullname, password, phone, mandal, village) VALUES (?,?,?,?,?)',   #inserting received data into tables
                (data['fullname'], data['password'], data['phone'], data['mandal'], data['village']) )
        con.commit()
        return jsonify({'status':'ok'})





#rbk index page sending info of crops_queue, avalable transports, and ricemills
@app.route('/')
@login_required
def index():
    rbk_active_user = session.get('rbk_active_user')
    rbk_id = rbk_active_user['rbk_id']

    con = get_db()
    
    mandal = rbk_active_user['mandal']
    cursor = con.execute(f'SELECT * FROM crops_queue WHERE rbk_id="{rbk_id}" and status="Processing"')
    crops_queue = [dict(each) for each in cursor.fetchall()]
    
    cursor = con.execute(f'SELECT trips, vehicle_type, vehicle_no, available_dates FROM transport_owners WHERE mandal="{mandal}"')
    transport_owners = [dict(row) for row in cursor.fetchall()]
    transports = []
    for every_owner in transport_owners:
        every_owner['available_dates'] = eval(every_owner['available_dates'])

        for date_ in every_owner['available_dates']:

            transports.append({'trips':every_owner['trips'], 'vehicle_type':every_owner['vehicle_type'], 'vehicle_no':every_owner['vehicle_no'], 'available_on':date_})

    cursor = con.execute(f'SELECT millname, village, mandal FROM ricemill_owners')
    ricemills = [dict(row) for row in cursor.fetchall()]
    
    cursor = con.execute(f'SELECT * FROM messages WHERE assigned_rbk={rbk_id}')
    messages = [dict(row) for row in cursor.fetchall()]


    return render_template('rbk_index', user_details=rbk_active_user, crops_queue=crops_queue, transports=transports, ricemills=ricemills, messages=messages)        #rendering the show page along with fetched details




#rbk_assign is the endpoint that recievs data from rbk to inser new or update existing queue records
@app.route('/rbk_assign', methods=["POST"])
@login_required
def rbk_assign():
    data = request.get_json()
    rbk_id = data['rbk_id']
    type_ = data['type_']
    con = get_db()

    crop_id=data['crop_id']
    vehicle_no, pick_up_date =data['selected_transport'].split(';')
    millname, mill_mandal = data['selected_mill'].split(';')

    con.execute(f'UPDATE crops_queue SET qc_check="True", bags_req= ?, amount= ?  WHERE crop_id= ?', ( data['crop_bags'], data['crop_amount'], crop_id ) )

    cursor = con.execute(f'SELECT * FROM crops_queue WHERE crop_id={crop_id}')
    crop_queue = dict(cursor.fetchone())

    survey_no = crop_queue['survey_no']
    cursor = con.execute(f'SELECT * FROM farmers WHERE phone in (SELECT phone from surveys WHERE survey_no={survey_no})')
    farmer = dict(cursor.fetchone())

    cursor = con.execute(f'SELECT * FROM transport_owners WHERE vehicle_no="{vehicle_no}"')
    transport_owner = dict(cursor.fetchone())

    if type_=='update':
        
        con.execute(f'UPDATE transport_queue SET date_booked= ?, vehicle_type= ?, vehicle_no= ?  WHERE crop_id= ?', ( pick_up_date, transport_owner['vehicle_type'], vehicle_no, crop_id ) )
        
    else:
        con.execute('INSERT INTO transport_queue (crop_id, c_fullname, c_phone, d_fullname, d_phone, date_booked, time_slot, vehicle_type, Vehicle_no, status) VALUES (?,?,?,?,?,?,?,?,?,?)',
                (crop_id, farmer['fullname'], farmer['phone'], transport_owner['fullname'], transport_owner['phone'], pick_up_date, crop_queue['pick_up_time'], transport_owner['vehicle_type'], vehicle_no, 'In-Progress'))


    cursor = con.execute('SELECT MAX(track_id), vehicle_no FROM transport_queue')
    track_id = dict(cursor.fetchone())['MAX(track_id)']

    cursor = con.execute(f'SELECT COUNT(vehicle_no) FROM transport_queue WHERE vehicle_no="{vehicle_no}" AND status="Completed"')
    ct = dict(cursor.fetchone())['COUNT(vehicle_no)']

    cursor = con.execute(f'SELECT COUNT(vehicle_no) FROM transport_queue WHERE vehicle_no="{vehicle_no}"')
    tt = dict(cursor.fetchone())['COUNT(vehicle_no)']

    con.execute('UPDATE transport_owners SET trips= ? WHERE vehicle_no= ?',( f'{ct}/{tt}', vehicle_no ))
    

    cursor = con.execute(f'SELECT * FROM ricemill_owners WHERE millname="{millname}" AND mandal="{mill_mandal}"')
    ricemill = dict(cursor.fetchone())

    if type_=='update':
        
        con.execute('UPDATE ricemill_queue SET millname= ?, mill_phone= ?, crop_get_date= ?, no_of_bags= ?, t_fullname= ?, t_phone= ?, vehicle_type= ?, Vehicle_no= ? WHERE crop_id= ? AND track_id= ?',
                (millname, ricemill['mill_phone'],  pick_up_date, crop_queue['bags_req'], transport_owner['fullname'], transport_owner['phone'], transport_owner['vehicle_type'], vehicle_no, crop_id, track_id))
        
        con.execute('UPDATE transport_queue SET from_ = ?, to_ = ? WHERE track_id=?', (farmer['address'], ricemill['address'], track_id))

    else:
        con.execute('INSERT INTO ricemill_queue (millname, mill_phone, crop_id, survey_no, crop_get_date, c_fullname, c_phone, no_of_bags, track_id, t_fullname, t_phone, vehicle_type, Vehicle_no) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
                (millname, ricemill['mill_phone'], crop_id, survey_no, pick_up_date, farmer['fullname'], farmer['phone'], crop_queue['bags_req'], track_id, transport_owner['fullname'], transport_owner['phone'], transport_owner['vehicle_type'], vehicle_no))
        
        con.execute('UPDATE transport_queue SET from_ = ?, to_ = ? WHERE track_id=?', (farmer['address'], ricemill['address'], track_id))

    con.commit()

    return jsonify({'status':'ok'})






#when requested for sepcific details the endpoint is called
@app.route('/rbk_get_details/<type_>')
@login_required
def rbk_get_details(type_):
    rbk_active_user = session.get('rbk_active_user')
    mandal = rbk_active_user['mandal']
    rbk_id = rbk_active_user['rbk_id']

    con = get_db()

    cursor = con.execute(f'SELECT * FROM crops_queue WHERE rbk_id={rbk_id} and status="Completed"')
    db_crops = [dict(each) for each in cursor.fetchall()]
    crop_ids = [row['crop_id'] for row in db_crops ]

    if type_ == 'db_crops':

        return jsonify(db_crops)

    if type_ == 'db_transport_queue':        
        
        db_transport_queue = []

        for crop_id in crop_ids:
            cursor = con.execute(f'SELECT * FROM transport_queue WHERE crop_id={crop_id}')
            db_transport_queue.append(dict(cursor.fetchone()))
        
        return jsonify(db_transport_queue)

    if type_ =='db_farmers_surveys':

        cursor = con.execute(f'SELECT * FROM farmers WHERE rbk_id="{rbk_id}" ')
        db_farmers = [dict(each) for each in cursor.fetchall()]

        for every in db_farmers:
            user_phone = every['phone']
            cursor = con.execute(f'SELECT * FROM surveys WHERE phone="{user_phone}" ')
            db_surveys = [dict(each) for each in cursor.fetchall()]
            for each in db_surveys:
                every.update(each)
        
        return jsonify(db_farmers)

    if type_ == 'db_transport_owners':

        cursor = con.execute(f'SELECT * FROM transport_owners WHERE mandal="{mandal}" ')
        db_transport_owners = [dict(each) for each in cursor.fetchall()]

        return jsonify(db_transport_owners)
    
    if type_ == 'db_ricemill_owners':

        cursor = con.execute(f'SELECT * FROM ricemill_owners')
        db_ricemill_owners = [dict(each) for each in cursor.fetchall()]

        print(db_ricemill_owners)
        return jsonify(db_ricemill_owners)



#main execution
if __name__=="__main__":
    app.run(debug=True, port=5001)