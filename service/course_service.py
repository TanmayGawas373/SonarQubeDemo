"""Service layer for course management.
All functions are now methods of CourseService; wrappers preserve backward compatibility.
"""

from dao.course_dao import (
    create_course,
    get_course,
    list_courses,
    update_course,
    delete_course,
)
from utils.role_check import _ensure_admin, _ensure_instructor, get_current_user_id, _ensure_instructor_or_admin


from utils.logger import log_instructor_action, log_admin_action

class CourseService:
    """Encapsulates business logic for courses."""

    def create_course_service(self, data):
        _ensure_instructor_or_admin()
        instructor_id = data.get('instructor_id') or get_current_user_id()
        title = data.get('title')
        description = data.get('description', '')
        if not title:
            raise ValueError("Course title required")
        course = create_course(title=title, description=description, instructor_id=instructor_id)
        log_instructor_action(f"Created course (id={course.id}): Title='{title}', Instructor={instructor_id}", "info")
        return course

    def get_course_service(self, course_id):
        course = get_course(course_id)
        if not course:
            raise ValueError("Course not found")
        return course

    def list_courses_service(self, search=None, page=1, per_page=10):
        return list_courses(search, page, per_page)

    def update_course_service(self, course_id, data):
        _ensure_instructor()
        course = update_course(course_id, **data)
        log_instructor_action(f"Updated course (id={course_id}): {data}", "info")
        return course

    def delete_course_service(self, course_id):
        _ensure_instructor_or_admin()
        course = delete_course(course_id)
        log_instructor_action(f"Deleted course (id={course_id})", "info")
        return course

    def admin_update_course_service(self, course_id, data):
        course = update_course(course_id, **data)
        log_admin_action(f"Admin updated course (id={course_id}): {data}", "info")
        return course

    def list_courses_by_instructor(self, instructor_id):
        _ensure_instructor_or_admin()
        courses, _ = list_courses_service()
        return [c for c in courses if c.instructor_id == instructor_id]


course_service = CourseService()

def create_course_service(*args, **kwargs):
    return course_service.create_course_service(*args, **kwargs)

def get_course_service(*args, **kwargs):
    return course_service.get_course_service(*args, **kwargs)

def list_courses_service(*args, **kwargs):
    return course_service.list_courses_service(*args, **kwargs)

def update_course_service(*args, **kwargs):
    return course_service.update_course_service(*args, **kwargs)

def delete_course_service(*args, **kwargs):
    return course_service.delete_course_service(*args, **kwargs)

def admin_update_course_service(*args, **kwargs):
    return course_service.admin_update_course_service(*args, **kwargs)

def list_courses_by_instructor(*args, **kwargs):
    return course_service.list_courses_by_instructor(*args, **kwargs)
