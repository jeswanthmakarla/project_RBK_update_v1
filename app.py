#importing require libraries
import sqlite3
from functools import wraps
from flask import Flask, g, request, session, redirect, url_for, jsonify, render_template
import hashlib

#configuring the flask app and jinja env
app = Flask(__name__)
app.secret_key = 'my_secret_key'
app.config['SESSION_COOKIE_NAME'] = 'regular_app_session'
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
        if session.get('logged_in'):
            return func(*args, **kwargs)
        else:
            return redirect('/login')
    return wraper



#default route
@app.route('/')
@login_required
def index():
    active_user = session.get('active_user')
    if active_user['user_type']=='farmer': return redirect('/farmer_index')
    if active_user['user_type']=='transport': return redirect('/transport_index')
    if active_user['user_type']=='ricemill': return redirect('/ricemill_index')
    if active_user['user_type']=='rbk': return redirect('/rbk_index')
    
    return render_template('base.html', temp=active_user)


#login route
@app.route('/login', methods=["GET","POST"])
def login():
    if not session.get('logged_in'):
        if request.method=='POST':
            form = request.form
            form_phone = form['username']
            form_password = hashlib.sha256(bytes(form['password'],'utf-8') ).hexdigest()

            con = get_db()
            cursor = con.execute(f'SELECT * FROM users WHERE phone={form_phone}')
            db_user = dict(cursor.fetchone())

            if form_password == db_user['password']:
                    session['logged_in'] = True
                    del db_user['password']
                    session['active_user'] = db_user
                    return redirect('/')
            else:
                return render_template('login', title='', alert_script='<script>alert("Invalid login credentials. Retry again.")</script>', page='/signup')
        else:
            return render_template('login', title='', alert_script='', page='/signup')
    else:
        return redirect('/')


#logout route
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
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
    con = get_db()

    cursor = con.execute('SELECT DISTINCT mandal FROM places;')
    mandals = [v for each in cursor.fetchall() for k,v in dict(each).items() ]

    return render_template('signup', mandals=mandals)




#send msg endpoint for any user to send message to respective RBK
@app.route('/send_msg', methods=["POST"])
@login_required
def send_msg():
    data = request.get_json()
    con = get_db()
    con.execute(f'INSERT INTO messages (c_fullname, c_phone, survey_no, message, assigned_rbk, status) VALUES (?,?,?,?,?,?)',
                (data['c_fullname'], data['c_phone'], data['survey_no'], data['message'], data['assigned_rbk'], 'in-progress') )
    con.commit()
    return jsonify({'status':'ok'})



#some global that require for registration for user
user_reg_mandal = ''
user_reg_village = ''
user_rbk_id = ''
user_type = ''



#Ricemill user registration endpoint returns {'status':'ok'} if all good
@app.route('/ricemill_reg', methods=["GET","POST"])
def ricemill_reg():
    if request.method=="GET":
        global user_reg_mandal
        global user_reg_village
        global user_rbk_id
        global user_type

        user_reg_mandal = request.args.get('mandal')
        user_reg_village = request.args.get('village')
        user_rbk_id = request.args.get('registred_rbK_id')
        user_type = 'ricemill'
        
        return render_template('ricemill_reg', reg_type="ricemill_reg")
        
    
    if request.method=="POST":
        data = request.get_json()

        con = get_db()
        con.execute('INSERT INTO users  (phone, password, user_type) VALUES (?,?,?)', 
                    (data['mill_phone'], data['password'], user_type))
        con.execute('INSERT INTO ricemill_owners (rbk_id, fullname, millname, mill_phone, storage_capacity, milling_capacity, dispatched_bags, address, mandal, village) VALUES (?,?,?,?,?,?,?,?,?,?)', 
                    ( user_rbk_id, data['fullname'], data['millname'], data['mill_phone'], data['storage_capacity'], data['milling_capacity'], 0, data['address'], user_reg_mandal, user_reg_village))
        
        con.commit()

        return jsonify({'status':'ok'})



#farmer user registration endpoint returns {'status':'ok'} if all good
@app.route('/farmer_reg', methods=["GET","POST"])
def farmer_reg():
    if request.method=="GET":
        global user_reg_mandal
        global user_reg_village
        global user_rbk_id
        global user_type

        user_reg_mandal = request.args.get('mandal')
        user_reg_village = request.args.get('village')
        user_rbk_id = request.args.get('registred_rbK_id')
        user_type = 'farmer'
        
        return render_template('farmer_reg', reg_type="farmer_reg")
        
    
    if request.method=="POST":
        data = request.get_json()

        con = get_db()
        con.execute('INSERT INTO users  (phone, password, user_type) VALUES (?,?,?)', 
                    (data['phone'], hashlib.sha256(bytes(data['password'],'utf-8') ).hexdigest(), user_type))
        con.execute('INSERT INTO farmers  (rbk_id, fullname, phone, bank_ac, aadhaar_no, address, mandal, village) VALUES (?,?,?,?,?,?,?,?)', 
                    ( user_rbk_id, data['fullname'], data['phone'], data['bank_ac'], data['aadhaar_no'], data['address'], user_reg_mandal, user_reg_village))
        con.execute('INSERT INTO surveys  (phone, survey_no, land_capacity, land_passbook) VALUES (?,?,?,?)', 
                    (data['phone'], data['survey_no'], data['land_capacity'], data['land_passbook'],))
        
        con.commit()

        return jsonify({'status':'ok'})




#Transport user registration endpoint returns {'status':'ok'} if all good
@app.route('/transport_reg', methods=["GET","POST"])
def transport_reg():
    if request.method=="GET":
        global user_reg_mandal
        global user_reg_village
        global user_rbk_id
        global user_type

        user_reg_mandal = request.args.get('mandal')
        user_reg_village = request.args.get('village')
        user_rbk_id = request.args.get('registred_rbK_id')
        user_type = 'transport'
        
        return render_template('transport_reg', reg_type="transport_reg")
        
    
    if request.method=="POST":
        data = request.get_json()

        con = get_db()
        con.execute('INSERT INTO users  (phone, password, user_type) VALUES (?,?,?)', 
                    (data['phone'], data['password'], user_type))
        con.execute('INSERT INTO transport_owners (rbk_id, fullname, phone, trips, vehicle_type, vehicle_no, vehicle_rec, available_dates, address, mandal, village) VALUES (?,?,?,?,?,?,?,?,?,?,?)', 
                    (user_rbk_id, data['fullname'], data['phone'], 0, data['vehicle_type'], data['vehicle_no'], data['vehicle_rec'], '[]', data['address'], user_reg_mandal, user_reg_village))
        
        con.commit()

        return jsonify({'status':'ok'})



#as per the user logged in session the ricemill user index page along with its defaults
@app.route('/ricemill_index')
@login_required
def ricemill_index():
    active_user = session.get('active_user')

    if active_user['user_type']=='ricemill':
        con = get_db()

        mill_phone = active_user['phone']
        cursor = con.execute(f'SELECT * FROM ricemill_owners where mill_phone="{ mill_phone }"')
        mill_details = [dict(each) for each in cursor.fetchall()][0]

        millname = mill_details['millname']
        cursor = con.execute(f'SELECT * FROM ricemill_queue where millname="{ millname }"')
        mill_queue = [dict(each) for each in cursor.fetchall()]

        return render_template('ricemill_index', user_details=mill_details, queue=mill_queue)
    else:
        return '<h3>Error : You does not have access to this page.</h3>'



#update mill bags_status and self details and returns {'status':'ok'} if all good
@app.route('/mill_update/<type_>', methods=["POST","GET"])
@login_required
def mill_update(type_):
    active_user = session.get('active_user')

    if request.method=="POST":
        if type_=='bags_status':
            data = request.get_json()
            print(data)
            con = get_db()

            if data['status']=='dispatched':

                phone = active_user['phone']
                cursor = con.execute(f'SELECT storage_capacity, dispatched_bags FROM ricemill_owners WHERE mill_phone={phone}')
                record = [dict(each) for each in cursor.fetchall()][0]
                 
                storage_capacity = record['storage_capacity'] - int(data['no_of_bags']) 
                dispatched_bags = record['dispatched_bags'] + int(data['no_of_bags'])

                con.execute(f'UPDATE ricemill_owners SET storage_capacity=?, dispatched_bags=?  WHERE mill_phone=?',
                            ( storage_capacity, dispatched_bags , active_user['phone'] ) )
            
            if data['status']=='dispatched received':
                con.execute('UPDATE crops_queue SET status="Completed" WHERE crop_id={}'.format(data['crop_id']) )
                con.execute('UPDATE transport_queue SET status="Completed" WHERE track_id={}'.format(data['track_id']))

                cursor = con.execute('SELECT vehicle_no FROM transport_queue WHERE track_id={}'.format(data['track_id']))
                vehicle_no = dict(cursor.fetchone())['vehicle_no']

                cursor = con.execute(f'SELECT COUNT(vehicle_no) FROM transport_queue WHERE vehicle_no="{vehicle_no}" AND status="Completed"')
                ct = dict(cursor.fetchone())['COUNT(vehicle_no)']

                cursor = con.execute(f'SELECT COUNT(vehicle_no) FROM transport_queue WHERE vehicle_no="{vehicle_no}"')
                tt = dict(cursor.fetchone())['COUNT(vehicle_no)']

                con.execute('UPDATE transport_owners SET trips= ? WHERE vehicle_no= ?',( f'{ct}/{tt}', vehicle_no ))

            con.execute(f'UPDATE ricemill_queue SET bags_status=? WHERE id=?', ( data['status'], data['id']) )
            con.commit()

            return jsonify({'status':'ok'})
        
        if type_=='mill':
            form = request.get_json()

            con = get_db()
            con.execute(f'UPDATE ricemill_owners SET storage_capacity=?, milling_capacity=?, dispatched_bags=?  WHERE mill_phone=?',
                         ( form['storage_capacity'], form['milling_capacity'], form['dispatched_bags'], active_user['phone'] ) )
            con.commit()

            return jsonify({'status':'ok'})




#as per the user logged in session the farmer user index page along with its defaults
@app.route('/farmer_index')
@login_required
def farmer_index():
    active_user = session.get('active_user')

    if active_user['user_type']=='farmer':
        con = get_db()

        phone = active_user['phone']

        cursor = con.execute(f'SELECT * FROM farmers where phone="{ phone }"')
        farmer_details = [dict(each) for each in cursor.fetchall()][0]

        
        cursor = con.execute(f'SELECT * FROM surveys where phone="{ phone }"')
        surveys = [dict(each) for each in cursor.fetchall()]

        crops = []
        for each_survey in surveys:
            survey_no = each_survey['survey_no']
            cursor = con.execute(f'SELECT * FROM crops_queue where survey_no="{ survey_no }"')
            for each in cursor.fetchall():
                crops.append(dict(each))
        
        transports = []
        for each_crop in crops:
            crop_id = each_crop['crop_id']
            cursor = con.execute(f'SELECT * FROM transport_queue where crop_id="{ crop_id }"')
            for each in cursor.fetchall():
                transports.append(dict(each))
        
        return render_template('farmer_index', user_details=farmer_details, surveys=surveys, crops=crops, transports=transports)
    
    else:
        return '<h3>Error : You does not have access to this page.</h3>'


#update crops queue and returns {'status':'ok'} if all good
@app.route('/crops_sell', methods=["POST"])
@login_required
def crops_sell():
    active_user = session.get('active_user')
    data = request.get_json()
    con = get_db()

    columns = ', '.join(data.keys())
    placeholders = ', '.join('?' * len(data))
    sql = 'INSERT INTO crops_queue ({}) VALUES ({})'.format(columns, placeholders)
    values = [v for k,v in data.items()]

    con.execute(sql, values)
    con.commit()

    return jsonify({'status':'ok'})




#as per the user logged in session the transport user index page along with its defaults
@app.route('/transport_index')
@login_required
def transport_index():
    active_user = session.get('active_user')

    if active_user['user_type']=='transport':
        con = get_db()

        phone = active_user['phone']

        cursor = con.execute(f'SELECT * FROM transport_owners where phone="{ phone }"')
        transport_owner_details = [dict(each) for each in cursor.fetchall()][0]
        
        cursor = con.execute(f'SELECT * FROM transport_queue where d_phone="{ phone }"')
        transport_queue = [dict(each) for each in cursor.fetchall()]
        
        return render_template('transport_index', user_details=transport_owner_details, queue=transport_queue)
    
    else:
        return '<h3>Error : You does not have access to this page.</h3>'



#update transport user avaiable dates and returns {'status':'ok'} if all good
@app.route('/transport_update/<type_>', methods=["POST"])
@login_required
def transport_update(type_):
        if type_=='available_dates':
            data = request.get_json()

            con = get_db()
            con.execute(f'UPDATE transport_owners SET available_dates=? WHERE phone=?', ( data['available_dates'], data['phone']) )
            con.commit()

            return jsonify({'status':'ok'})



#main execution
if __name__=="__main__":
    app.run(debug=True)