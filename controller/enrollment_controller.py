# controller/enrollment_controller.py
"""Blueprint exposing enrollment endpoints.
Endpoints:
* POST   /courses/<int:course_id>/enroll   – student enrolls
* DELETE /courses/<int:course_id>/enroll   – student unenrolls
* GET    /my/enrollments                 – list logged‑in student's enrollments
* GET    /courses/<int:course_id>/enrollments – instructor/admin list enrollments for a course
"""

from flask import Blueprint, jsonify, request
from service.enrollment_service import (
    enroll_student,
    unenroll_student,
    list_my_enrollments,
    list_course_enrollments,
)
from utils.role_check import _ensure_student

enroll_bp = Blueprint("enrollment", __name__)

@enroll_bp.route("/courses/<int:course_id>/enroll", methods=["POST"])
def enroll(course_id):
    try:
        enroll_student(course_id)
        return jsonify({"message": "Enrolled successfully"}), 201
    except PermissionError as exc:
        return jsonify({"error": str(exc)}), 403
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

@enroll_bp.route("/courses/<int:course_id>/enroll", methods=["DELETE"])
def unenroll(course_id):
    try:
        unenroll_student(course_id)
        return jsonify({"message": "Unenrolled successfully"}), 200
    except PermissionError as exc:
        return jsonify({"error": str(exc)}), 403
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

@enroll_bp.route("/my/enrollments", methods=["GET"])
def my_enrollments():
    try:
        _ensure_student()
        enrolls = list_my_enrollments()
        payload = [
            {"course_id": e.course_id, "enrolled_at": e.enrolled_at.isoformat()}
            for e in enrolls
        ]
        return jsonify(payload), 200
    except PermissionError as exc:
        return jsonify({"error": str(exc)}), 401

@enroll_bp.route("/courses/<int:course_id>/enrollments", methods=["GET"])
def course_enrollments(course_id):
    try:
        enrolls = list_course_enrollments(course_id)
        payload = [
            {"user_id": e.user_id, "enrolled_at": e.enrolled_at.isoformat()}
            for e in enrolls
        ]
        return jsonify(payload), 200
    except PermissionError as exc:
        return jsonify({"error": str(exc)}), 403
