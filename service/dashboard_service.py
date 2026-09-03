"""Business logic for instructor dashboard (Phase 3) and admin dashboard."""

from service.enrollment_service import count_students_by_instructor_service
from service.course_service import list_courses_by_instructor
from service.quiz_service import (
    count_quizzes_by_instructor,
    average_score_by_instructor,
)
from dao.analytics_dao import (
    get_course_performance,
    get_quiz_performance,
    get_admin_dashboard_stats,
)


class DashboardService:
    """Encapsulates dashboard data aggregation for instructors."""

    def get_instructor_dashboard(self, instructor_id):
        courses = list_courses_by_instructor(instructor_id)
        total_courses = len(courses)
        total_students = count_students_by_instructor_service(instructor_id)
        total_quizzes = count_quizzes_by_instructor(instructor_id)
        average_score = average_score_by_instructor(instructor_id)
        course_performance = get_course_performance(instructor_id)
        quiz_performance = get_quiz_performance(instructor_id)
        return {
            "courses": courses,
            "total_courses": total_courses,
            "total_students": total_students,
            "total_quizzes": total_quizzes,
            "average_score": average_score,
            "course_performance": course_performance,
            "quiz_performance": quiz_performance,
        }

    def get_admin_dashboard(self):
        return get_admin_dashboard_stats()


dashboard_service = DashboardService()

def get_instructor_dashboard_service(*args, **kwargs):
    return dashboard_service.get_instructor_dashboard(*args, **kwargs)

def get_admin_dashboard_service(*args, **kwargs):
    return dashboard_service.get_admin_dashboard(*args, **kwargs)