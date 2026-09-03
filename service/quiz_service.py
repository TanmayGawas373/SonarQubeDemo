from dao.quiz_dao import (
    average_score_by_instructor,
    count_quizzes_by_instructor,
    create_quiz,
    get_instructor_students_paginated,
    get_quiz,
    list_quizzes_by_course,
    delete_quiz,
    create_question,
    get_question,
    list_questions_by_quiz,
    delete_question,
    submit_quiz_result,
    list_results_by_student,
    list_results_by_quiz,
    get_quiz_result,
    update_quiz_title,
    update_question,
    get_student_results_paginated,
    get_instructor_quiz_results_paginated,
    get_instructor_students,
)
from utils.role_check import _ensure_instructor, _ensure_student, get_current_user_id, _ensure_instructor_or_admin


from utils.logger import log_instructor_action, log_student_action

class QuizService:
    """Encapsulates all quiz‑related business logic as instance methods."""

    def create_quiz_service(self, course_id, data):
        _ensure_instructor()
        title = data.get("title")
        if not title:
            raise ValueError("Quiz title required")
        quiz = create_quiz(title, course_id, instructor_id=get_current_user_id())
        log_instructor_action(f"Created quiz (id={quiz.id}) for course (id={course_id}): Title='{title}'", "info")
        return quiz

    def get_quiz_service(self, quiz_id):
        quiz = get_quiz(quiz_id)
        if not quiz:
            raise ValueError("Quiz not found")
        return quiz

    def list_quizzes_service(self, course_id):
        return list_quizzes_by_course(course_id)

    def delete_quiz_service(self, quiz_id):
        _ensure_instructor()
        quiz = delete_quiz(quiz_id)
        log_instructor_action(f"Deleted quiz (id={quiz_id})", "info")
        return quiz

    def add_question_service(self, quiz_id, data):
        _ensure_instructor()
        prompt = data.get("prompt")
        options = data.get("options")
        if not prompt or not isinstance(options, list) or not options:
            raise ValueError("Prompt and non‑empty options list required")
        question = create_question(quiz_id, prompt, options)
        log_instructor_action(f"Added question (id={question.id}) to quiz (id={quiz_id})", "info")
        return question

    def list_questions_service(self, quiz_id):
        return list_questions_by_quiz(quiz_id)

    def delete_question_service(self, question_id):
        _ensure_instructor()
        question = delete_question(question_id)
        log_instructor_action(f"Deleted question (id={question_id})", "info")
        return question

    def submit_attempt_service(self, quiz_id, answers_dict):
        _ensure_student()
        questions = list_questions_by_quiz(quiz_id)
        if not questions:
            raise ValueError("Quiz has no questions")
        total = len(questions)
        correct = 0
        for q in questions:
            chosen = answers_dict.get(str(q.id))
            opts = q.get_options()
            correct_idx = next((i for i, o in enumerate(opts) if o.get("is_correct")), None)
            if chosen is not None and int(chosen) == correct_idx:
                correct += 1
        score = correct / total * 100
        result = submit_quiz_result(quiz_id, student_id=get_current_user_id(), answers_dict=answers_dict, score=score)
        log_student_action(f"Student (id={get_current_user_id()}) attempted quiz (id={quiz_id}) - Score: {score}%", "info")
        return result

    def get_student_results_service(self):
        _ensure_student()
        return list_results_by_student(get_current_user_id())

    def get_quiz_results_service(self, quiz_id):
        _ensure_instructor_or_admin()
        return list_results_by_quiz(quiz_id)

    def get_instructor_quiz_stats_service(self, instructor_id):
        _ensure_instructor()
        return {
            "total_quizzes": count_quizzes_by_instructor(instructor_id),
            "average_score": average_score_by_instructor(instructor_id),
        }

    def update_quiz_service(self, quiz_id, title):
        _ensure_instructor()
        if not title:
            raise ValueError("Quiz title required")
        quiz = update_quiz_title(quiz_id, title)
        log_instructor_action(f"Updated quiz title (id={quiz_id}) to '{title}'", "info")
        return quiz

    def update_question_service(self, question_id, data):
        _ensure_instructor()
        prompt = data.get("prompt")
        options = data.get("options")
        if not prompt or not isinstance(options, list) or not options:
            raise ValueError("Prompt and non‑empty options list required")
        question = update_question(question_id, prompt, options)
        log_instructor_action(f"Updated question (id={question_id}): Prompt='{prompt}'", "info")
        return question

    def get_quiz_result_detail_service(self, result_id):
        result = get_quiz_result(result_id)
        if not result:
            raise ValueError("Result not found")
        return result

    def get_student_results_paginated_service(self, page: int = 1, per_page: int = 10, search: str = None):
        _ensure_student()
        student_id = get_current_user_id()
        return get_student_results_paginated(student_id, page, per_page, search)

    def get_instructor_quiz_results_paginated_service(self, instructor_id: int, page: int = 1, per_page: int = 10, search: str = None):
        _ensure_instructor_or_admin()
        return get_instructor_quiz_results_paginated(instructor_id, page, per_page, search)

    def get_instructor_students_service(self, instructor_id: int):
        _ensure_instructor_or_admin()
        return get_instructor_students(instructor_id)

    def get_instructor_students_paginated_service(self, instructor_id: int, page: int = 1, per_page: int = 10, search: str = None):
        _ensure_instructor_or_admin()
        return get_instructor_students_paginated(instructor_id, page, per_page, search)


quiz_service = QuizService()

def create_quiz_service(*args, **kwargs):
    return quiz_service.create_quiz_service(*args, **kwargs)

def get_quiz_service(*args, **kwargs):
    return quiz_service.get_quiz_service(*args, **kwargs)

def list_quizzes_service(*args, **kwargs):
    return quiz_service.list_quizzes_service(*args, **kwargs)

def delete_quiz_service(*args, **kwargs):
    return quiz_service.delete_quiz_service(*args, **kwargs)

def add_question_service(*args, **kwargs):
    return quiz_service.add_question_service(*args, **kwargs)

def list_questions_service(*args, **kwargs):
    return quiz_service.list_questions_service(*args, **kwargs)

def delete_question_service(*args, **kwargs):
    return quiz_service.delete_question_service(*args, **kwargs)

def submit_attempt_service(*args, **kwargs):
    return quiz_service.submit_attempt_service(*args, **kwargs)

def get_student_results_service(*args, **kwargs):
    return quiz_service.get_student_results_service(*args, **kwargs)

def get_quiz_results_service(*args, **kwargs):
    return quiz_service.get_quiz_results_service(*args, **kwargs)

def get_instructor_quiz_stats_service(*args, **kwargs):
    return quiz_service.get_instructor_quiz_stats_service(*args, **kwargs)

def update_quiz_service(*args, **kwargs):
    return quiz_service.update_quiz_service(*args, **kwargs)

def update_question_service(*args, **kwargs):
    return quiz_service.update_question_service(*args, **kwargs)

def get_quiz_result_detail_service(*args, **kwargs):
    return quiz_service.get_quiz_result_detail_service(*args, **kwargs)

def get_student_results_paginated_service(*args, **kwargs):
    return quiz_service.get_student_results_paginated_service(*args, **kwargs)

def get_instructor_quiz_results_paginated_service(*args, **kwargs):
    return quiz_service.get_instructor_quiz_results_paginated_service(*args, **kwargs)

def get_instructor_students_service(*args, **kwargs):
    return quiz_service.get_instructor_students_service(*args, **kwargs)

def get_instructor_students_paginated_service(*args, **kwargs):
    return quiz_service.get_instructor_students_paginated_service(*args, **kwargs)
