from dao.user_dao import (
    get_all_users,
    get_user_by_id,
    update_user,
    delete_user_by_id
)


from sqlalchemy import or_

from models.user import User


def get_all_users_service(search=None, page=1, per_page=10):
    """
    Returns (users, total_count) for the given page, optionally filtered
    by a case-insensitive match against email or role.
    """
    query = User.query

    if search:
        like_pattern = f"%{search}%"
        query = query.filter(
            or_(
                User.email.ilike(like_pattern),
                User.role.ilike(like_pattern)
            )
        )

    total = query.count()

    users = (
        query.order_by(User.id.asc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return users, total


def get_user_by_id_service(user_id):
    return get_user_by_id(user_id)


from utils.logger import log_admin_action

def update_user_service(user_id, email, role):
    log_admin_action(f"Updating user (id={user_id}) - Email: {email}, Role: {role}", "info")
    return update_user(
        user_id,
        email,
        role
    )


def delete_user_service(user_id):
    log_admin_action(f"Deleting user (id={user_id})", "info")
    return delete_user_by_id(user_id)

def get_all_instructors_service():
    users = get_all_users()
    return [user for user in users if user.role == 'instructor']