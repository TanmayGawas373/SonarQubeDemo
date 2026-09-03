from config.db import db

class Lesson(db.Model):
    __tablename__ = 'lessons'

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships
    completions = db.relationship('LessonCompletion', backref='lesson', lazy='select', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f"<Lesson {self.id} {self.title}>"
