# dao/enrollment_dao.py
"""DAO for Enrollment model (class‑based)."""

from config.db import db
from models.enrollment import Enrollment
from models.course import Course
from models.quiz import Quiz
from models.quiz_result import QuizResult
from sqlalchemy import func


class EnrollmentDAO:
    """Encapsulates CRUD operations for Enrollment."""

    def create_enrollment(self, user_id, course_id):
        enrollment = Enrollment(user_id=user_id, course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()
        return enrollment

    def is_user_enrolled(self, user_id, course_id):
        return (
            Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()
            is not None
        )

    def get_enrollment(self, enrollment_id):
        return Enrollment.query.get(enrollment_id)

    def get_enrollments_by_user(self, user_id):
        return Enrollment.query.filter_by(user_id=user_id).all()

    def get_enrollments_by_user_paginated(self, user_id, page=1, per_page=10, search=None):
        query = (
            Enrollment.query
            .join(Course, Enrollment.course_id == Course.id)
            .filter(Enrollment.user_id == user_id)
        )
        if search:
            query = query.filter(Course.title.ilike(f'%{search}%'))
        query = query.order_by(Enrollment.enrolled_at.desc())
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        return items, total

    def count_students_by_instructor(self, instructor_id):
        return (
            db.session.query(Enrollment.user_id)
            .join(Course, Enrollment.course_id == Course.id)
            .filter(Course.instructor_id == instructor_id)
            .distinct()
            .count()
        )

    def get_enrollments_by_course(self, course_id):
        return Enrollment.query.filter_by(course_id=course_id).all()

    def delete_enrollment(self, user_id, course_id):
        enrollment = Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()
        if not enrollment:
            raise ValueError("Enrollment not found")
        db.session.delete(enrollment)
        db.session.commit()
        return True


# Module‑level singleton
enrollment_dao = EnrollmentDAO()

# Backward‑compatible wrappers
def create_enrollment(*args, **kwargs):
    return enrollment_dao.create_enrollment(*args, **kwargs)

def is_user_enrolled(*args, **kwargs):
    return enrollment_dao.is_user_enrolled(*args, **kwargs)

def get_enrollment(*args, **kwargs):
    return enrollment_dao.get_enrollment(*args, **kwargs)

def get_enrollments_by_user(*args, **kwargs):
    return enrollment_dao.get_enrollments_by_user(*args, **kwargs)

def get_enrollments_by_user_paginated(*args, **kwargs):
    return enrollment_dao.get_enrollments_by_user_paginated(*args, **kwargs)

def count_students_by_instructor(*args, **kwargs):
    return enrollment_dao.count_students_by_instructor(*args, **kwargs)

def get_enrollments_by_course(*args, **kwargs):
    return enrollment_dao.get_enrollments_by_course(*args, **kwargs)

def delete_enrollment(*args, **kwargs):
    return enrollment_dao.delete_enrollment(*args, **kwargs)
