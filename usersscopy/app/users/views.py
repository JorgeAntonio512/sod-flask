from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from werkzeug import check_password_hash, generate_password_hash

from app import db
from app.users.forms import RegisterForm, LoginForm
from app.users.models import User
from app.users.decorators import requires_login

mod = Blueprint('users', __name__, url_prefix='/users')



@mod.route('/me/')
@requires_login
def home():
  return render_template("users/profile.html", user=g.user)



# @mod.before_request
# def before_request():
    

# @mod.teardown_request
# def teardown_request(exception):
#     db = getattr(g, 'db', None)
#     if db is not None:
#         db.close()




@mod.before_request
def before_request():
  g.db = db
  """
  pull user's profile from the database before every request are treated
  """
  g.user = None
  if 'user_id' in session:
    g.user = User.query.get(session['user_id'])

   

@mod.route('/login/', methods=['GET', 'POST'])
def login():
  """
  Login form
  """
  form = LoginForm(request.form)
  # make sure data are valid, but doesn't validate password is right
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    # we use werzeug to validate user's password
    if user and check_password_hash(user.password, form.password.data):
      # the session can't be modified as it's signed, 
      # it's a safe place to store the user id
      session['user_id'] = user.id
      session['logged_in'] = True
      flash('Welcome %s' % user.name)
      return redirect(url_for('users.show_entries'))
    flash('Wrong email or password', 'error-message')
  return render_template("users/login.html", form=form)

@mod.route('/register/', methods=['GET', 'POST'])
def register():
  """
  Registration Form
  """
  form = RegisterForm(request.form)
  if form.validate_on_submit():
    # create an user instance not yet stored in the database
    user = User(name=form.name.data, email=form.email.data, \
      password=generate_password_hash(form.password.data))
    # Insert the record in our database and commit it
    db.session.add(user)
    db.session.commit()

    # Log the user in, as he now has an id
    session['user_id'] = user.id
    session['logged_in'] = True
    # flash will display a message to the user
    flash('Thanks for registering')
    # redirect user to the 'home' method of the user module.
    return redirect(url_for('users.show_entries'))
  return render_template("users/register.html", form=form)



@mod.route('/updebate/<int:entries_did>')
def up_vote(entries_did):
    connection = g.db.session.connection()
    g.db.engine.execute('update users_debates set rating = rating + 1 where did = "{0}"'.format(entries_did))  
    #g.db.commit()
    return redirect(request.referrer)


@mod.route('/downdebate/<int:entries_did>')
def down_vote(entries_did):
    connection = g.db.session.connection() 
    g.db.engine.execute('update users_debates set rating = rating - 1 where did = "{0}"'.format(entries_did))
    #g.db.commit()
    return redirect(request.referrer)


@mod.route('/upargument/<int:argumentsidea_aid>')
def up_argument(argumentsidea_aid):
    connection = g.db.session.connection()
    g.db.engine.execute('update users_arguments set rating = rating + 1 where aid = "{0}"'.format(argumentsidea_aid))  
    #g.db.commit()
    return redirect(request.referrer)


@mod.route('/downargument/<int:argumentsideb_aid>')
def down_argument(argumentsideb_aid):
    connection = g.db.session.connection()
    g.db.engine.execute('update users_arguments set rating = rating - 1 where aid = "{0}"'.format(argumentsideb_aid))
    #g.db.commit()
    return redirect(request.referrer)




@mod.route('/')
def show_entries():
    connection = g.db.session.connection()  
    cur = g.db.engine.execute('select did, title, text, rating from users_debates order by rating desc')
    db_result = cur.fetchall()
    entries = [dict(did=row[0], title=row[1], text=row[2], rating=row[3]) for row in db_result]
    return render_template('users/show_entries.html', entries=entries)

@mod.route('/add', methods=['POST'])
def add_entry():
    connection = g.db.session.connection()
    g.db.engine.execute('insert into users_debates (title, text, sidea, sideb) values (?, ?, ?, ?)',
                 [request.form['title'], request.form['text'], request.form['sidea'], request.form['sideb']])
    #g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('users.show_entries'))



@mod.route('/adda', methods=['POST'])
def add_argumenta():
    connection = g.db.session.connection()
    g.db.engine.execute('insert into users_arguments (did, argument, side) values (?, ?, ?)',
                 [request.form['did'], request.form['argument'], request.form['side']])
    #g.db.commit()
    flash('New argument was successfully posted')
    return redirect(request.referrer) 

@mod.route('/addb', methods=['POST'])
def add_argumentb():
    connection = g.db.session.connection()
    g.db.engine.execute('insert into users_arguments (did, argument, side) values (?, ?, ?)',
                 [request.form['did'], request.form['argument'], request.form['side']])
    #g.db.commit()
    flash('New argument was successfully posted')
    return redirect(request.referrer)       



@mod.route('/debate/<int:entries_did>')
def debate_page(entries_did):
    connection = g.db.session.connection()
    query = 'select title, text, sidea, sideb, did from users_debates where did = "{0}"'.format(entries_did)
    cur = g.db.engine.execute(query)
    db_result = cur.fetchall()
    entries = [dict(title=row[0], text=row[1], sidea=row[2], sideb=row[3], did=row[4]) for row in db_result]
    querytwo = 'select argument, aid, rating from users_arguments where did = "{0}" and side = "0" order by rating desc'.format(entries_did)
    cuv = g.db.engine.execute(querytwo)
    db_resultr = cuv.fetchall()
    argumentsidea = [dict(argument=row[0], aid=row[1], rating=row[2]) for row in db_resultr]
    querythree = 'select argument, aid, rating from users_arguments where did = "{0}" and side = "1" order by rating desc'.format(entries_did)
    cuv = g.db.engine.execute(querythree)
    db_resultq = cuv.fetchall()
    argumentsideb = [dict(argument=row[0], aid=row[1], rating=row[2]) for row in db_resultq]
    return render_template('users/debate_page.html', entries=entries, argumentsidea=argumentsidea, argumentsideb=argumentsideb)

@mod.route('/createdebate')
def createdebate():
    return render_template('users/createdebate.html')


@mod.route('/createuser')
def createuser():
    return render_template('users/createuser.html')


@mod.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('users.show_entries'))  