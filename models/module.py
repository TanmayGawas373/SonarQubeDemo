from config.db import db

class Module(db.Model):
    __tablename__ = 'modules'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships
    lessons = db.relationship('Lesson', backref='module', lazy='joined', cascade='all, delete-orphan')
    materials = db.relationship('Material', backref='module', lazy='joined', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f"<Module {self.id} {self.title}>"
