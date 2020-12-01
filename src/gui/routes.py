from flask import Flask, redirect, render_template, url_for, jsonify, request, flash, g
from flask_socketio import SocketIO, emit

import sqlite3

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.before_request
def open_db():
    g.db = sqlite3.connect('security_system.db')

@app.teardown_request
def close_db(error=None):
    if 'db' in g:
        try:
            g.db.close()
        except Excpetion as e:
            print(f"Failed to close database after request!\n{e}")

@app.route('/')
def home():
    return redirect(url_for('access_summary'))

#
#   Acess summary
#

@app.route('/access_summary')
def access_summary():
    return render_template('access_summary.html')

@app.route('/access_summary/data')
def access_ajax():
    access_data = []
    for row in g.db.execute('SELECT employee_info.first_name, employee_info.middle_name, ' +
                            ' employee_info.last_name, node_info.address, ' +
                            'access_summary.access_type, access_summary.temp_reading, ' + 
                            'access_summary.access_datetime FROM access_summary INNER JOIN ' +
                            'employee_info ON employee_info.employee_id == ' + 
                            'access_summary.employee_id INNER JOIN node_info ON ' +
                            'node_info.node_id = access_summary.access_node'):
        access_data.append({"first": row[0], "middle": row[1], "last": row[2], "door": row[3],
                            "type": row[4], "temp": row[5], "timestamp": row[6]})

    return jsonify({"data": access_data})

#
#   Users
#

@app.route('/users')
def users():
    return render_template('users.html')

@app.route('/users/data')
def users_ajax():
    user_data = []
    for row in g.db.execute('SELECT employee_id, first_name, last_name, nfc_id FROM employee_info'):
        user_data.append({"DT_RowID": row[0], "first": row[1], "last": row[2], "id": row[3].hex()})

    return jsonify({"data": user_data})

@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    if request.form:
        first = request.form.get('fname', None)
        last = request.form.get('lname', None)
        badge_id = request.form.get('badgeid', None)

        if badge_id is not None:
            try:
                badge_id = bytes.fromhex(badge_id)
            except ValueError:
                pass

        if first is None or first.strip() == '':
            flash('Invalid first name', 'error')
        elif last is None or last.strip() == '':
            flash('Invalid last anme', 'error')
        elif badge_id is None or len(badge_id) != 16:
            flash('Invalid badge ID', 'error')
        else:
            with g.db:
                g.db.execute('INSERT INTO employee_info (first_name, last_name, admin, nfc_id) ' + 
                             'VALUES (?, ?, "N", ?)', (first.strip(), last.strip(), badge_id))
            return redirect('/users')

    return render_template('add_user.html')

@app.route('/users/delete')
def delete_user():
    if 'row_id' not in request.args:
        return 'Invalid request', 400

    with g.db:
        g.db.execute('DELETE FROM employee_info WHERE employee_id == ?', (request.args['row_id'],))
    
    socketio.emit('users', 'refresh')
    return '', 200

#
#   Doors
#

@app.route('/doors')
def doors():
    return render_template('doors.html')

@app.route('/doors/data')
def doors_ajax():
    door_data = []

    for row in g.db.execute('SELECT node_id, address, location, node_type FROM node_info'):
        door_data.append({"DT_RowID": row[0], "name": row[1], "location": row[2], "type": row[3]})

    return jsonify({"data": door_data})

@app.route('/doors/add', methods=['GET', 'POST'])
def add_door():
    if request.forms:
        name = request.forms.get('name', None)
        location = request.forms.get('location', None)
        door_type = request.forms.get('type', None)

        if name is None or name.strip() == '':
            flash('Invalid name', 'error')
        elif location is None or location.strip() == '':
            flash('Invalid location', 'error')
        elif door_type is None or not (door_type.strip() == 'entry' or door_type.strip() == 'exit'):
            flash('Invalid type', 'error')
        else:
            with g.db:
                g.db.execute('INSERT INTO node_info (address, location, node_type) VALUES (?, ?, ?)',
                             (name.strip(), location.strip(), door_type))
            return redirect('/doors')

    return render_template('add_door.html')

@app.route('/doors/delete')
def delete_door():
    if 'row_id' not in request.args:
        return 'Invalid request', 400

    with g.db:
        g.db.execute('DELETE FROM node_info WHERE node_id == ?', (request.args['row_id'],))

    socketio.emit('doors', 'refresh')
    return '', 200

#
#   Settings
#

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.form:
        print("Got Form!", request.form)
        
        maximum_occupancy = request.form.get('maximum_occupancy', None)
        min_user_temp = request.form.get('min_user_temp', None)
        max_user_temp = request.form.get('max_user_temp', None)

        max_occ_val = None
        min_temp_val = None
        max_temp_val = None

        try:
            max_occ_val = int(maximum_occupancy)
            min_temp_val = float(min_user_temp)
            max_temp_val = float(max_user_temp)
        except ValueError:
            if max_occ_val is None:
                flash('Invalid maximum occupancy', 'error')
            elif min_temp_val is None:
                flash('Invalid minimum temperature', 'error')
            elif max_temp_val is None:
                flash('Invalid maximum temperature', 'error')
        else:
            flash('Settings updated')
    else:
        maximum_occupancy = 50
        min_user_temp = 28
        max_user_temp = 37.5

    return render_template('settings.html', max_occ = maximum_occupancy,
                           min_temp = min_user_temp, max_temp = max_user_temp)


