# dao/analytics_dao.py

from sqlalchemy import func, case

from models.course import Course
from models.enrollment import Enrollment
from models.quiz import Quiz
from models.quiz_result import QuizResult

from config.db import db

def get_course_performance(instructor_id):

    results = (
        db.session.query(
            Course.id,
            Course.title,

            func.count(
                func.distinct(Enrollment.user_id)
            ).label("student_count"),

            func.avg(
                QuizResult.score
            ).label("avg_score")
        )
        .outerjoin(
            Enrollment,
            Enrollment.course_id == Course.id
        )
        .outerjoin(
            Quiz,
            Quiz.course_id == Course.id
        )
        .outerjoin(
            QuizResult,
            QuizResult.quiz_id == Quiz.id
        )
        .filter(
            Course.instructor_id == instructor_id
        )
        .group_by(
            Course.id,
            Course.title
        )
        .all()
    )

    return results

def get_quiz_performance(instructor_id):

    results = (
        db.session.query(
            Quiz.id,
            Quiz.title,

            func.count(
                QuizResult.id
            ).label("attempts"),

            func.avg(
                QuizResult.score
            ).label("avg_score"),

            (
                func.sum(
                    case(
                        (QuizResult.score >= 40, 1),
                        else_=0
                    )
                ) * 100.0
                /
                func.nullif(
                    func.count(QuizResult.id),
                    0
                )
            ).label("pass_rate")
        )
        .join(
            Course,
            Course.id == Quiz.course_id
        )
        .outerjoin(
            QuizResult,
            QuizResult.quiz_id == Quiz.id
        )
        .filter(
            Course.instructor_id == instructor_id
        )
        .group_by(
            Quiz.id,
            Quiz.title
        )
        .all()
    )

    return results

def get_admin_dashboard_stats():
    """Return core statistics for admin dashboard."""
    from models.user import User
    from models.course import Course
    from models.enrollment import Enrollment
    from models.quiz_result import QuizResult
    
    total_users = db.session.query(User).count()
    course_count = db.session.query(Course).count()
    enrollment_count = db.session.query(Enrollment).count()
    quiz_attempts_count = db.session.query(QuizResult).count()

    student_count = db.session.query(User).filter_by(role='student').count()
    instructor_count = db.session.query(User).filter_by(role='instructor').count()
    admin_count = db.session.query(User).filter_by(role='admin').count()

    popular_courses_query = db.session.query(
        Course.title, func.count(Enrollment.id).label('student_count')
    ).join(
        Enrollment, Course.id == Enrollment.course_id
    ).group_by(
        Course.id
    ).order_by(
        func.count(Enrollment.id).desc()
    ).limit(3).all()
    
    popular_courses = []
    for title, count in popular_courses_query:
        popular_courses.append({
            "title": title,
            "student_count": count
        })

    results = db.session.query(QuizResult.score).all()
    avg_score = 0.0
    pass_rate = 0.0
    if results:
        scores = [r[0] for r in results]
        avg_score = sum(scores) / len(scores)
        passed = sum(1 for s in scores if s >= 70.0)
        pass_rate = (passed / len(scores)) * 100.0

    return {
        'total_users': total_users,
        'course_count': course_count,
        'enrollment_count': enrollment_count,
        'quiz_attempts_count': quiz_attempts_count,
        'student_count': student_count,
        'instructor_count': instructor_count,
        'admin_count': admin_count,
        'popular_courses': popular_courses,
        'avg_quiz_score': round(avg_score, 1),
        'quiz_pass_rate': round(pass_rate, 1)
    }