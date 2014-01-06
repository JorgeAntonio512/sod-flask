# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing

# configuration
DATABASE = 'flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close() 


@app.route('/updebate/<int:entries_did>')
def up_vote(entries_did):
    g.db.execute('update debates set rating = rating + 1 where did = "{0}"'.format(entries_did))  
    g.db.commit()
    return redirect(request.referrer)


@app.route('/downdebate/<int:entries_did>')
def down_vote(entries_did):
    g.db.execute('update debates set rating = rating - 1 where did = "{0}"'.format(entries_did))
    g.db.commit()
    return redirect(request.referrer)


@app.route('/upargument/<int:argumentsidea_aid>')
def up_argument(argumentsidea_aid):
    g.db.execute('update arguments set rating = rating + 1 where aid = "{0}"'.format(argumentsidea_aid))  
    g.db.commit()
    return redirect(request.referrer)


@app.route('/downargument/<int:argumentsideb_aid>')
def down_argument(argumentsideb_aid):
    g.db.execute('update arguments set rating = rating - 1 where aid = "{0}"'.format(argumentsideb_aid))
    g.db.commit()
    return redirect(request.referrer)




@app.route('/')
def show_entries():
    cur = g.db.execute('select did, title, text, rating from debates order by rating desc')
    db_result = cur.fetchall()
    entries = [dict(did=row[0], title=row[1], text=row[2], rating=row[3]) for row in db_result]
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    g.db.execute('insert into debates (title, text, sidea, sideb) values (?, ?, ?, ?)',
                 [request.form['title'], request.form['text'], request.form['sidea'], request.form['sideb']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))



@app.route('/adda', methods=['POST'])
def add_argumenta():
    g.db.execute('insert into arguments (did, argument, side) values (?, ?, ?)',
                 [request.form['did'], request.form['argument'], request.form['side']])
    g.db.commit()
    flash('New argument was successfully posted')
    return redirect(request.referrer) 

@app.route('/addb', methods=['POST'])
def add_argumentb():
    g.db.execute('insert into arguments (did, argument, side) values (?, ?, ?)',
                 [request.form['did'], request.form['argument'], request.form['side']])
    g.db.commit()
    flash('New argument was successfully posted')
    return redirect(request.referrer)       



@app.route('/debate/<int:entries_did>')
def debate_page(entries_did):
    query = 'select title, text, sidea, sideb, did from debates where did = "{0}"'.format(entries_did)
    cur = g.db.execute(query)
    db_result = cur.fetchall()
    entries = [dict(title=row[0], text=row[1], sidea=row[2], sideb=row[3], did=row[4]) for row in db_result]
    querytwo = 'select argument, aid, rating from arguments where did = "{0}" and side = "0" order by rating desc'.format(entries_did)
    cuv = g.db.execute(querytwo)
    db_resultr = cuv.fetchall()
    argumentsidea = [dict(argument=row[0], aid=row[1], rating=row[2]) for row in db_resultr]
    querythree = 'select argument, aid, rating from arguments where did = "{0}" and side = "1" order by rating desc'.format(entries_did)
    cuv = g.db.execute(querythree)
    db_resultq = cuv.fetchall()
    argumentsideb = [dict(argument=row[0], aid=row[1], rating=row[2]) for row in db_resultq]
    return render_template('debate_page.html', entries=entries, argumentsidea=argumentsidea, argumentsideb=argumentsideb)

@app.route('/createdebate')
def createdebate():
    return render_template('createdebate.html')


@app.route('/createuser')
def createuser():
    return render_template('createuser.html')

@app.route('/createuserforeal', methods=['POST'])
def createuserforeal():  
    g.db.execute('insert into users (username, password) values (?, ?)',
                 [request.form['username'], request.form['password']])
    g.db.commit()
    return render_template('layout.html')       

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/loginn', methods=['GET', 'POST'])
def loginn():
    return ('damn it, beevus!')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))    


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10080)

