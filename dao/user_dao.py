from config.db import db
from models.user import User


def create_user(email, password_hash, role='student', full_name=None, education=None):
    user = User(
        email=email,
        password_hash=password_hash,
        role=role,
        full_name=full_name,
        education=education
    )

    db.session.add(user)
    db.session.commit()

    return user


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_all_users():
    return User.query.all()


def update_user(user_id, email, role):
    user = User.query.get(user_id)

    if not user:
        return None

    user.email = email
    user.role = role

    db.session.commit()

    return user


def delete_user_by_id(user_id):
    user = User.query.get(user_id)

    if user:
        db.session.delete(user)
        db.session.commit()

        return True

    return False