from app.database import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    bio = db.Column(db.Text())
    profile_picture = db.Column(db.String(200))

    role = db.relationship('Role', backref=db.backref('users', lazy=True))

    def __init__(self, username, email, password, role_id, first_name=None, last_name=None, bio=None, profile_picture=None):
        self.username = username
        self.email = email
        self.password = password
        self.role_id = role_id
        self.first_name = first_name
        self.last_name = last_name
        self.bio = bio
        self.profile_picture = profile_picture