from app import db
from app.users import constants as USER

class User(db.Model):

      __tablename__ = 'users_user'
      id = db.Column(db.Integer, primary_key=True)
      name = db.Column(db.String(50), unique=True)
      email = db.Column(db.String(120), unique=True)
      password = db.Column(db.String(120))
      role = db.Column(db.SmallInteger, default=USER.USER)
      status = db.Column(db.SmallInteger, default=USER.NEW)
      rating = db.Column(db.Integer, server_default="0")

      def __init__(self, name=None, email=None, password=None):
        self.name = name
        self.email = email
        self.password = password

      def getStatus(self):
        return USER.STATUS[self.status]

      def getRole(self):
        return USER.ROLE[self.role]

      def __repr__(self):
          return '<User %r>' % (self.name)


class Debates(db.Model):

      __tablename__ = 'users_debates'
      did = db.Column(db.Integer, primary_key=True)
      uid = db.Column(db.Integer)
      title = db.Column(db.Text())
      text = db.Column(db.Text())
      sidea = db.Column(db.Text())
      sideb = db.Column(db.Text())
      rating = db.Column(db.Integer, server_default="0")

class Arguments(db.Model):

      __tablename__ = 'users_arguments'
      aid = db.Column(db.Integer, primary_key=True)
      did = db.Column(db.Integer)
      uid = db.Column(db.Integer)
      side = db.Column(db.Integer)
      argument = db.Column(db.Text())
      rating = db.Column(db.Integer, server_default="0")