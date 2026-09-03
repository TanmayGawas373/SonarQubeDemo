# models/quiz_result.py
"""QuizResult stores a student's attempt and score.
`answers_json` holds a mapping of question_id → selected option index.
"""

from config.db import db
import json

class QuizResult(db.Model):
    __tablename__ = "quiz_results"

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    score = db.Column(db.Float, nullable=False)
    submitted_at = db.Column(db.DateTime, server_default=db.func.now())
    answers_json = db.Column(db.Text, nullable=False)  # JSON dict {question_id: chosen_index}

    def set_answers(self, answers: dict):
        self.answers_json = json.dumps(answers)

    def get_answers(self):
        return json.loads(self.answers_json)

    def __repr__(self) -> str:
        return f"<QuizResult {self.id} student={self.student_id} score={self.score}>"
