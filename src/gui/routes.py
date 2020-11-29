#! /usr/bin/env python3

from flask import Flask, redirect, render_template, url_for, jsonify
app = Flask(__name__)

@app.route('/')
def home():
    return redirect(url_for('access_summary'))

@app.route('/access_summary')
def access_summary():
    return render_template('access_summary.html')

@app.route('/access_summary/data')
def access_ajax():
    return jsonify({"data": []})

@app.route('/users')
def users():
    return render_template('users.html')

@app.route('/users/data')
def users_ajax():
    u = [{"first": "Robert", "last": "Smith", "id": 1}]

    return jsonify({"data": u})

@app.route('/doors')
def doors():
    return render_template('doors.html')

@app.route('/doors/data')
def doors_ajax():
    d = [{"name": "Main Entrance", "location": "North side", "type": "Entrance"}]

    return jsonify({"data": d})

@app.route('/settings')
def settings():
    return render_template('settings.html')


