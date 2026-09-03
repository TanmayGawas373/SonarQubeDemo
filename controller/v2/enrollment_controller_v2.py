# controller/v2/enrollment_controller_v2.py
"""
v2 Enrollment API - JSON only endpoints.
"""

from flask import Blueprint, request, jsonify
from utils.jwt_util import jwt_required
from utils.role_check import _ensure_student
from service.enrollment_service import (
    enroll_student,
    unenroll_student,
    list_my_enrollments,
    list_course_enrollments,
)

enrollment_v2_bp = Blueprint('enrollment_v2', __name__, url_prefix='/api/v2')


@enrollment_v2_bp.route('/courses/<int:course_id>/enroll', methods=['POST'])
@jwt_required
def enroll(course_id):
    try:
        _ensure_student()
        enroll_student(course_id)
        return jsonify({'message': 'Enrolled successfully'}), 201
    except PermissionError as exc:
        return jsonify({'error': str(exc)}), 403
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400


@enrollment_v2_bp.route('/courses/<int:course_id>/enroll', methods=['DELETE'])
@jwt_required
def unenroll(course_id):
    try:
        _ensure_student()
        unenroll_student(course_id)
        return jsonify({'message': 'Unenrolled successfully'}), 200
    except PermissionError as exc:
        return jsonify({'error': str(exc)}), 403
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400


@enrollment_v2_bp.route('/my/enrollments', methods=['GET'])
@jwt_required
def my_enrollments():
    try:
        _ensure_student()
        enrolls = list_my_enrollments()
        payload = [
            {
                'course_id': e.course_id,
                'course_title': e.course.title,
                'enrolled_at': e.enrolled_at.isoformat() if e.enrolled_at else None
            }
            for e in enrolls
        ]
        return jsonify(payload), 200
    except PermissionError as exc:
        return jsonify({'error': str(exc)}), 401


@enrollment_v2_bp.route('/courses/<int:course_id>/enrollments', methods=['GET'])
@jwt_required
def course_enrollments(course_id):
    try:
        from service.enrollment_service import _ensure_instructor_or_admin
        _ensure_instructor_or_admin()
        
        enrolls = list_course_enrollments(course_id)
        payload = [
            {
                'user_id': e.user_id,
                'user_email': e.user.email,
                'enrolled_at': e.enrolled_at.isoformat() if e.enrolled_at else None
            }
            for e in enrolls
        ]
        return jsonify(payload), 200
    except PermissionError as exc:
        return jsonify({'error': str(exc)}), 403