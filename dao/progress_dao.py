# dao/progress_dao.py
"""DAO for Progress model (class‑based)."""

from config.db import db
from models.progress import Progress


class ProgressDAO:
    """Encapsulates CRUD operations for Progress."""

    def get_progress(self, student_id, course_id):
        return Progress.query.filter_by(student_id=student_id, course_id=course_id).first()

    def update_progress(self, student_id, course_id, completion_percent):
        prog = self.get_progress(student_id, course_id)
        if not prog:
            prog = Progress(
                student_id=student_id,
                course_id=course_id,
                completion_percent=completion_percent,
            )
            db.session.add(prog)
        else:
            prog.completion_percent = completion_percent
        db.session.commit()
        return prog


# Module‑level singleton
progress_dao = ProgressDAO()

# Backward‑compatible wrappers
def get_progress(*args, **kwargs):
    return progress_dao.get_progress(*args, **kwargs)

def update_progress(*args, **kwargs):
    return progress_dao.update_progress(*args, **kwargs)
