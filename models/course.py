from config.db import db

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships
    modules = db.relationship('Module', backref='course', lazy='joined', cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', back_populates='course', lazy='joined', cascade='all, delete-orphan')
    quizzes = db.relationship('Quiz', backref='course', lazy='select', cascade='all, delete-orphan')
    progress_records = db.relationship('Progress', backref='course', lazy='select', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f"<Course {self.id} {self.title}>"

    def to_dict(self):
        return {
            "title":self.title,
            "description":self.description,
            "instructor_id":self.instructor_id,
            "modules":self.modules,
            "enrollments":self.enrollments
        }
