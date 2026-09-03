# models/progress.py
"""Progress model aggregating lesson completions and quiz results per student per course."""

from config.db import db

class Progress(db.Model):
    __tablename__ = 'progress'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    completion_percent = db.Column(db.Float, nullable=False, default=0.0)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self) -> str:
        return f"<Progress s={self.student_id} c={self.course_id} {self.completion_percent}%>"
