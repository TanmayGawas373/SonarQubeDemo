# models/enrollment.py
"""Enrollment model linking a student (user) to a course.
Only a student role may create an enrollment; an instructor or admin can view
all enrollments for a course. The model stores timestamps for audit purposes.
"""

from config.db import db

class Enrollment(db.Model):
    __tablename__ = "enrollments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    enrolled_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships (optional, but handy for eager loading)
    user = db.relationship("User", back_populates="enrollments", lazy="joined")
    course = db.relationship("Course", back_populates="enrollments", lazy="joined")

    __table_args__ = (
        db.UniqueConstraint("user_id", "course_id", name="uq_user_course"),
    )

    def __repr__(self) -> str:
        return f"<Enrollment u={self.user_id} c={self.course_id}>"

    def to_dict(self):
        return {
            "user_id":self.user_id,
            "course_id":self.course_id,
            "course":self.course.to_dict(),
            "user":self.user.to_dict()
        }
