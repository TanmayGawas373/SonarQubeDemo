# dao/lesson_completion_dao.py
"""DAO for LessonCompletion model."""

from config.db import db
from models.lesson_completion import LessonCompletion


def mark_completed(student_id: int, lesson_id: int):
    """Create a completion record if it does not already exist."""
    existing = (
        LessonCompletion.query.filter_by(student_id=student_id, lesson_id=lesson_id).first()
    )
    if existing:
        return existing
    lc = LessonCompletion(student_id=student_id, lesson_id=lesson_id)
    db.session.add(lc)
    db.session.commit()
    return lc


def count_completed_lessons(student_id: int, course_id: int) -> int:
    """Return the number of lessons in the given course that the student has completed."""
    from models.lesson import Lesson
    from models.module import Module
    return (
        LessonCompletion.query.join(Lesson)
        .join(Module, Lesson.module_id == Module.id)
        .filter(LessonCompletion.student_id == student_id, Module.course_id == course_id)
        .count()
    )


def total_lessons_in_course(course_id: int) -> int:
    """Return total lesson count for a course."""
    from models.lesson import Lesson
    from models.module import Module
    return (
        Lesson.query.join(Module, Lesson.module_id == Module.id)
        .filter(Module.course_id == course_id)
        .count()
    )
