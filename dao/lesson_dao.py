# dao/lesson_dao.py
"""DAO for Lesson model (class‑based)."""

from config.db import db
from models.lesson import Lesson


class LessonDAO:
    """Encapsulates CRUD operations for Lesson."""

    def create_lesson(self, module_id, title, content='', order=0):
        lesson = Lesson(module_id=module_id, title=title, content=content, order=order)
        db.session.add(lesson)
        db.session.commit()
        return lesson

    def get_lesson(self, lesson_id):
        return Lesson.query.get(lesson_id)

    def list_lessons_by_module(self, module_id):
        return Lesson.query.filter_by(module_id=module_id).all()

    def update_lesson(self, lesson_id, **kwargs):
        lesson = self.get_lesson(lesson_id)
        if not lesson:
            raise ValueError("Lesson not found")
        for k, v in kwargs.items():
            setattr(lesson, k, v)
        db.session.commit()
        return lesson

    def delete_lesson(self, lesson_id):
        lesson = self.get_lesson(lesson_id)
        if not lesson:
            raise ValueError("Lesson not found")
        db.session.delete(lesson)
        db.session.commit()
        return True


# Module‑level singleton
lesson_dao = LessonDAO()

# Backward‑compatible wrappers
def create_lesson(*args, **kwargs):
    return lesson_dao.create_lesson(*args, **kwargs)

def get_lesson(*args, **kwargs):
    return lesson_dao.get_lesson(*args, **kwargs)

def list_lessons_by_module(*args, **kwargs):
    return lesson_dao.list_lessons_by_module(*args, **kwargs)

def update_lesson(*args, **kwargs):
    return lesson_dao.update_lesson(*args, **kwargs)

def delete_lesson(*args, **kwargs):
    return lesson_dao.delete_lesson(*args, **kwargs)
