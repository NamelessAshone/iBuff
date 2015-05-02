#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Joel Kaaberg (jkaberg), joel@jkaberg.com'

import os
from sqlite3 import dbapi2 as sqlite3
from datetime import datetime

from flask import Flask, request, session, g, redirect, url_for, render_template, flash


app = Flask(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'ibuff.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='joel',
    PASSWORD='test12'
))
app.config.from_envvar('IBUFF_SETTINGS', silent=True)


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('Initialized the database.')


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/', methods=['GET'])
def show_workouts():
    if not os.path.isfile(app.config['DATABASE']):
        init_db()

    db = get_db()
    cur = db.execute('SELECT title, comment, id FROM workouts ORDER BY id ASC')
    workouts = cur.fetchall()

    return render_template('show_workouts.html', workouts=workouts)


@app.route('/addWorkout', methods=['POST'])
def add_workout():
    if not session.get('logged_in'):
        flash('You need to login.')
        return redirect(url_for('login'))

    db = get_db()
    db.execute('INSERT INTO workouts (title, comment) VALUES (?, ?)',
               [request.form['title'], request.form['comment']])
    db.commit()

    flash('New workout successfully added.')
    return redirect(url_for('show_workouts'))


@app.route('/deleteWorkout/<wid>', methods=['GET'])
def delete_workout(wid):
    if not session.get('logged_in'):
        flash('You need to login.')
        return redirect(url_for('login'))

    db = get_db()
    # TODO: Recursive deletion from bottom and up would be a lot better.
    db.execute('DELETE FROM workouts WHERE id = (?)', (wid,))
    db.execute('DELETE FROM exercises WHERE workout_id = (?)', (wid,))
    db.execute('DELETE FROM history WHERE workout_id = (?)', (wid,))
    db.commit()

    flash('Successfully deleted workout.')
    return redirect(url_for('show_workouts'))


@app.route('/showWorkout/<wid>', methods=['GET'])
def show_workout(wid):
    if not session.get('logged_in'):
        flash('You need to login.')
        return redirect(url_for('login'))

    db = get_db()
    # TODO: Fix this mess, no need for 2 querys..
    cur = db.execute('SELECT title, comment FROM workouts WHERE id=(?)', (wid,))
    workout = cur.fetchone()

    cur = db.execute('SELECT id, title, comment, sets, reps FROM exercises WHERE workout_id=(?) ORDER BY id ASC', (wid,))
    exercises = cur.fetchall()
    if exercises:
        eid = exercises[0]['id']
    else:
        eid = 0

    return render_template('show_workout.html', workout=workout, exercises=exercises, wid=wid, eid=eid)


@app.route('/playWorkout/<wid>/<eid>/<count>', methods=['GET', 'POST'])
def play_workout(wid, eid, count):
    if not session.get('logged_in'):
        flash('You need to login.')
        return redirect(url_for('login'))

    db = get_db()
    count = int(count)
    eid = int(eid)
    last_eid = eid if count == 0 else eid - 1

    # TODO: Fix this mess, too many querys.....

    # Get the current exercise
    cur = db.execute('SELECT id, title, comment, sets, reps FROM exercises WHERE workout_id = (?) ORDER BY id ASC', (wid,))
    exercise = cur.fetchall()

    # Add history
    if request.method == 'POST' and count > 0:
        db.execute('INSERT INTO history (exercise_id, workout_id, sets, reps, weight, date_time) values (?, ? , ?, ?, ?, ?)',
                   [last_eid, wid, request.form['sets'], request.form['reps'], request.form['weight'], datetime.now()])
        db.commit()

    # If count equals number of exercises then we're done!
    if count == len(exercise):
        flash('Workout finished, well done!')
        return redirect(url_for('show_workout', wid=wid))

    cur = db.execute('SELECT weight FROM history WHERE workout_id = (?) AND exercise_id = (?) ORDER BY id DESC', (wid, eid,))
    weight = cur.fetchone()

    return render_template('play_workout.html',
                           exercise=exercise[count],
                           wid=wid,
                           eid=eid + 1,
                           last_weight=weight[0] if weight else 1,
                           count=count + 1)


@app.route('/showExercise/<wid>/<eid>', methods=['GET'])
def show_exercise(wid, eid):
    if not session.get('logged_in'):
        flash('You need to login.')
        return redirect(url_for('login'))

    db = get_db()
    cur = db.execute('SELECT id, title, comment, sets, reps FROM exercises WHERE workout_id = (?) AND id = (?)', (wid, eid,))
    exercise = cur.fetchone()

    return render_template('show_exercise.html', exercise=exercise, wid=wid)


@app.route('/addExercise/<wid>', methods=['POST'])
def add_exercise(wid):
    if not session.get('logged_in'):
        flash('You need to login.')
        return redirect(url_for('login'))

    db = get_db()
    db.execute('INSERT INTO exercises (title, workout_id, comment, sets, reps) values (?, ?, ?, ?, ?)',
               [request.form['title'], wid, request.form['comment'], request.form['sets'], request.form['reps']])
    db.commit()

    flash('New workout successfully added.')
    return redirect(url_for('show_workout', wid=wid))

@app.route('/updateExercise/<wid>/<eid>', methods=['POST'])
def update_exercise(wid, eid):
    if not session.get('logged_in'):
        flash('You need to login.')
        return redirect(url_for('login'))

    db = get_db()
    db.execute('UPDATE exercises SET title = (?), comment = (?), sets = (?), reps = (?) WHERE workout_id = (?) AND id = (?)',
               (request.form['title'], request.form['comment'], request.form['sets'], request.form['reps'], wid, eid,))
    db.commit()

    flash('Exercise successfully updated.')
    return redirect(url_for('show_workout', wid=wid))


@app.route('/deleteExercise/<eid>/<wid>', methods=['GET'])
def delete_exercise(eid, wid):
    if not session.get('logged_in'):
        flash('You need to login.')
        return redirect(url_for('login'))

    db = get_db()
    db.execute('DELETE FROM exercises WHERE id = (?)', (eid,))
    db.execute('DELETE FROM history WHERE exercise_id = (?)', (eid,))
    db.commit()

    flash('Successfully deleted exercise.')
    return redirect(url_for('show_workout', wid=wid))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            # TODO: http://flask.pocoo.org/docs/0.10/quickstart/#cookies
            session['logged_in'] = True
            flash('You were logged in.')
            return redirect(url_for('show_workouts'))
    return render_template('login.html', error=error)


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_workouts'))

if __name__ == '__main__':
    app.run(host='0.0.0.0')