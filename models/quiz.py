# models/quiz.py
"""Quiz model representing a set of questions belonging to a course.
Each quiz is owned by an instructor (user) and tied to a course.
"""

from config.db import db

class Quiz(db.Model):
    __tablename__ = "quizzes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships
    questions = db.relationship("Question", backref="quiz", lazy="joined", cascade="all, delete-orphan")
    results = db.relationship("QuizResult", backref="quiz", lazy="joined", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Quiz {self.id} {self.title}>"
