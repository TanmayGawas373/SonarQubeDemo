# models/question.py
"""Question model for a quiz.
Supports multiple‑choice style with a list of options stored as JSON.
"""

from config.db import db
import json

class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    # Stored as JSON string: [{"option": "A", "is_correct": true}, ...]
    options_json = db.Column(db.Text, nullable=False)

    def set_options(self, options: list):
        """Serialize a list of option dictionaries to JSON string."""
        self.options_json = json.dumps(options)

    def get_options(self):
        return json.loads(self.options_json)

    def __repr__(self) -> str:
        return f"<Question {self.id} quiz={self.quiz_id}>"
