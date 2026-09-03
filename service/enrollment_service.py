
from dao.enrollment_dao import (
    create_enrollment,
    is_user_enrolled,
    get_enrollments_by_user,
    get_enrollments_by_user_paginated,
    get_enrollments_by_course,
    count_students_by_instructor,
    delete_enrollment,
)
from utils.role_check import _ensure_student, _ensure_instructor, _ensure_admin, get_current_user_id, _ensure_instructor_or_admin


from utils.logger import log_student_action

class EnrollmentService:
    """Encapsulates enrollment operations."""

    def is_user_enrolled(self, user_id: int, course_id: int) -> bool:
        return is_user_enrolled(user_id, course_id)

    def enroll_student(self, course_id):
        _ensure_student()
        from dao.course_dao import get_course
        course = get_course(course_id)
        if not course:
            raise ValueError("Course not found")
        enrollment = create_enrollment(user_id=get_current_user_id(), course_id=course_id)
        log_student_action(f"Student (id={get_current_user_id()}) enrolled in course (id={course_id})", "info")
        return enrollment

    def unenroll_student(self, course_id):
        _ensure_student()
        result = delete_enrollment(user_id=get_current_user_id(), course_id=course_id)
        log_student_action(f"Student (id={get_current_user_id()}) unenrolled from course (id={course_id})", "info")
        return result

    def list_my_enrollments(self):
        student_id = get_current_user_id()
        if not student_id:
            raise PermissionError("Authentication required")
        return get_enrollments_by_user(student_id)

    def list_my_enrollments_paginated(self, page=1, per_page=10, search=None):
        student_id = get_current_user_id()
        if not student_id:
            raise PermissionError("Authentication required")
        items, total = get_enrollments_by_user_paginated(student_id, page, per_page, search)
        total_pages = max(1, (total + per_page - 1) // per_page)
        return {'results': items, 'total': total, 'page': page, 'total_pages': total_pages}

    def list_course_enrollments(self, course_id):
        _ensure_instructor_or_admin()
        return get_enrollments_by_course(course_id)

    def count_students_by_instructor(self, instructor_id):
        _ensure_instructor()
        return count_students_by_instructor(instructor_id)


enrollment_service = EnrollmentService()

def is_user_enrolled_service(*args, **kwargs):
    return enrollment_service.is_user_enrolled(*args, **kwargs)

def enroll_student(*args, **kwargs):
    return enrollment_service.enroll_student(*args, **kwargs)

def unenroll_student(*args, **kwargs):
    return enrollment_service.unenroll_student(*args, **kwargs)

def list_my_enrollments(*args, **kwargs):
    return enrollment_service.list_my_enrollments(*args, **kwargs)

def list_my_enrollments_paginated(*args, **kwargs):
    return enrollment_service.list_my_enrollments_paginated(*args, **kwargs)

def list_course_enrollments(*args, **kwargs):
    return enrollment_service.list_course_enrollments(*args, **kwargs)

def count_students_by_instructor_service(*args, **kwargs):
    return enrollment_service.count_students_by_instructor(*args, **kwargs)