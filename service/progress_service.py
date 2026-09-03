from dao.progress_dao import get_progress, update_progress
from dao.lesson_completion_dao import count_completed_lessons, total_lessons_in_course
from dao.quiz_dao import get_quiz_results_by_student_and_course
from utils.role_check import _ensure_student, get_current_user_id

def get_my_progress(course_id):
    _ensure_student()
    student_id = get_current_user_id()

    total_lessons = total_lessons_in_course(course_id)
    completed = count_completed_lessons(student_id, course_id)
    lesson_pct = (completed / total_lessons) if total_lessons else 0.0

    results = get_quiz_results_by_student_and_course(student_id, course_id)
    if results:
        avg_score = sum(r.score for r in results) / len(results)
        quiz_pct = avg_score / 100.0
    else:
        avg_score = 0
        quiz_pct = 0.0

    overall = (lesson_pct * 0.7 + quiz_pct * 0.3) * 100
    update_progress(student_id, course_id, overall)
    return {
        "completion_percent": round(overall, 2),
        "lessons_completed": completed,
        "total_lessons": total_lessons,
        "quizzes_taken": len(results),
        "total_quizzes": len(results),
        "average_score": round(avg_score, 2) if results else 0
    }

def recalculate_progress(student_id, course_id):
    total_lessons = total_lessons_in_course(course_id)
    completed = count_completed_lessons(student_id, course_id)
    lesson_pct = (completed / total_lessons) if total_lessons else 0.0
    results = get_quiz_results_by_student_and_course(student_id, course_id)
    if results:
        avg_score = sum(r.score for r in results) / len(results)
        quiz_pct = avg_score / 100.0
    else:
        quiz_pct = 0.0
    overall = (lesson_pct * 0.7 + quiz_pct * 0.3) * 100
    return update_progress(student_id, course_id, overall)
