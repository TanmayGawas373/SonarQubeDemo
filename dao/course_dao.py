# dao/course_dao.py
"""DAO for Course model (class‑based)."""

from config.db import db
from models.course import Course
from models.user import User


class CourseDAO:
    """Encapsulates CRUD operations for Course."""

    def create_course(self, title, description, instructor_id):
        course = Course(title=title, description=description, instructor_id=instructor_id)
        db.session.add(course)
        db.session.commit()
        return course

    def get_course(self, course_id):
        return Course.query.get(course_id)

    def list_courses(self, search=None, page=1, per_page=10):
        """Returns (courses, total_count) optionally filtered by search term.
        Search matches case‑insensitive title or instructor email.
        """
        from sqlalchemy import or_
        query = Course.query
        if search:
            like_pattern = f"%{search}%"
            query = query.join(User, Course.instructor_id == User.id).filter(
                or_(Course.title.ilike(like_pattern), User.email.ilike(like_pattern))
            )
        total = query.count()
        courses = (
            query.order_by(Course.id.asc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return courses, total

    def update_course(self, course_id, **kwargs):
        course = self.get_course(course_id)
        if not course:
            raise ValueError("Course not found")
        for k, v in kwargs.items():
            setattr(course, k, v)
        db.session.commit()
        return course

    def delete_course(self, course_id):
        course = self.get_course(course_id)
        if not course:
            raise ValueError("Course not found")
        db.session.delete(course)
        db.session.commit()
        return True


# Module‑level singleton
course_dao = CourseDAO()

# Backward‑compatible wrappers
def create_course(*args, **kwargs):
    return course_dao.create_course(*args, **kwargs)

def get_course(*args, **kwargs):
    return course_dao.get_course(*args, **kwargs)

def list_courses(*args, **kwargs):
    return course_dao.list_courses(*args, **kwargs)

def update_course(*args, **kwargs):
    return course_dao.update_course(*args, **kwargs)

def delete_course(*args, **kwargs):
    return course_dao.delete_course(*args, **kwargs)
