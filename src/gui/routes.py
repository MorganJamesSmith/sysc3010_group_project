from flask import Flask, redirect, render_template, url_for, jsonify, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

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
    return jsonify({"data": []})

#
#   Users
#

@app.route('/users')
def users():
    return render_template('users.html')

@app.route('/users/data')
def users_ajax():
    u = [{"DT_RowID": 0, "first": "Robert", "last": "Smith", "id": 1}]

    return jsonify({"data": u})

@app.route('/users/add')
def add_user():
    if request.args:
        print('Got form!', request.args)
        return redirect('/users')

    return render_template('add_user.html')

@app.route('/users/delete')
def delete_user():
    print(f"Delete user: {request.args['row_id']}")

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
    d = [{"DT_RowID": 0, "name": "Main Entrance", "location": "North side", "type": "Entrance"}]

    return jsonify({"data": d})

@app.route('/doors/add')
def add_door():
    if request.args:
        print('Got form!', request.args)
        return redirect('/doors')

    return render_template('add_door.html')

@app.route('/doors/delete')
def delete_door():
    print(f"Delete door: {request.args['row_id']}")

    socketio.emit('doors', 'refresh')

    return '', 200

#
#   Settings
#

@app.route('/settings')
def settings():
    if request.args:
        print("Got Form!", request.args)

    return render_template('settings.html')


