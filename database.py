from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/blog'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
        seed_roles()

from app.models.role import Role

def seed_roles():
    roles = [
        {'name': "Admin", 'description':"Administrator role with full access"},
        {'name': "Editor", 'description':"Editor role with limited access"},
        {'name': "User", 'description':"Regular user role"}
    ]

    for role_data in roles:
        role = Role.query.filter_by(name = role_data['name']).first()
        if not role:
            new_role=Role(name=role_data['name'], description = role_data['description'])
            db.session.add(new_role)
    db.session.commit()