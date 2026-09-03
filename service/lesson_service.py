from dao.lesson_dao import (
    create_lesson,
    get_lesson,
    list_lessons_by_module,
    update_lesson,
    delete_lesson,
)
from dao.lesson_completion_dao import mark_completed
from utils.role_check import _ensure_instructor, _ensure_student, get_current_user_id


from utils.logger import log_instructor_action, log_student_action

class LessonService:
    """Encapsulates lesson CRUD operations."""

    def create_lesson(self, module_id, data):
        _ensure_instructor()
        lesson = create_lesson(module_id=module_id, **data)
        log_instructor_action(f"Created lesson (id={lesson.id}) for module (id={module_id}): {data}", "info")
        return lesson

    def get_lesson(self, lesson_id):
        lesson = get_lesson(lesson_id)
        if not lesson:
            raise ValueError("Lesson not found")
        return lesson

    def list_lessons(self, module_id):
        return list_lessons_by_module(module_id)

    def update_lesson(self, lesson_id, data):
        _ensure_instructor()
        lesson = update_lesson(lesson_id, **data)
        log_instructor_action(f"Updated lesson (id={lesson_id}): {data}", "info")
        return lesson

    def delete_lesson(self, lesson_id):
        _ensure_instructor()
        lesson = delete_lesson(lesson_id)
        log_instructor_action(f"Deleted lesson (id={lesson_id})", "info")
        return lesson

    def complete_lesson(self, lesson_id):
        _ensure_student()
        student_id = get_current_user_id()
        completion = mark_completed(student_id, lesson_id)
        log_student_action(f"Student (id={student_id}) completed lesson (id={lesson_id})", "info")
        return completion


lesson_service = LessonService()

def create_lesson_service(*args, **kwargs):
    return lesson_service.create_lesson(*args, **kwargs)

def get_lesson_service(*args, **kwargs):
    return lesson_service.get_lesson(*args, **kwargs)

def list_lessons_service(*args, **kwargs):
    return lesson_service.list_lessons(*args, **kwargs)

def update_lesson_service(*args, **kwargs):
    return lesson_service.update_lesson(*args, **kwargs)

def delete_lesson_service(*args, **kwargs):
    return lesson_service.delete_lesson(*args, **kwargs)

def complete_lesson_service(*args, **kwargs):
    return lesson_service.complete_lesson(*args, **kwargs)
