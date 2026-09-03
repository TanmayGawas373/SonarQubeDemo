# controller/v2/course_controller_v2.py
"""
v2 Course API - JSON only endpoints.
"""

from flask import Blueprint, request, jsonify, g
from utils.jwt_util import jwt_required
from service.course_service import (
    create_course_service,
    get_course_service,
    list_courses_service,
    update_course_service,
    delete_course_service,
)
from service.enrollment_service import list_my_enrollments
from utils.role_check import _ensure_instructor_or_admin

course_v2_bp = Blueprint('course_v2', __name__, url_prefix='/api/v2/courses')


@course_v2_bp.route('', methods=['POST'])
@jwt_required
def create_course():
    try:
        _ensure_instructor_or_admin()
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON body required'}), 400
        
        course = create_course_service(data)
        return jsonify({
            'id': course.id,
            'title': getattr(course, 'title', None),
            'description': getattr(course, 'description', None),
            'instructor_id': getattr(course, 'instructor_id', None)
        }), 201
    except (PermissionError, ValueError) as exc:
        return jsonify({'error': str(exc)}), 400


@course_v2_bp.route('', methods=['GET'])
@jwt_required
def list_courses():
    query = request.args.get('q')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    if per_page > 100:
        per_page = 100
    
    jwt_user = getattr(g, 'current_user', None)
    
    courses, total = list_courses_service(
        search=query,
        page=page,
        per_page=per_page
    )
    
    enrolled_courses_ids = set()
    if jwt_user and jwt_user.get('role') == 'student':
        enrolled_courses_ids = {e.course_id for e in list_my_enrollments()}
    
    payload = [
        {
            'id': c.id,
            'title': getattr(c, 'title', None),
            'description': getattr(c, 'description', None),
            'instructor_id': getattr(c, 'instructor_id', None),
            'is_enrolled': c.id in enrolled_courses_ids
        }
        for c in courses
    ]
    
    return jsonify({
        'page': page,
        'per_page': per_page,
        'total': total,
        'courses': payload,
    }), 200


@course_v2_bp.route('/<int:course_id>', methods=['GET'])
def get_course(course_id):
    try:
        c = get_course_service(course_id)
        return jsonify({
            'id': c.id,
            'title': getattr(c, 'title', None),
            'description': getattr(c, 'description', None),
            'instructor_id': getattr(c, 'instructor_id', None),
            'created_at': c.created_at.isoformat() if getattr(c, 'created_at', None) else None
        }), 200
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 404


@course_v2_bp.route('/<int:course_id>', methods=['PUT'])
@jwt_required
def update_course(course_id):
    try:
        _ensure_instructor_or_admin()
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON body required'}), 400
        
        c = update_course_service(course_id, data)
        return jsonify({
            'id': c.id,
            'title': getattr(c, 'title', None),
            'description': getattr(c, 'description', None)
        }), 200
    except (PermissionError, ValueError) as exc:
        return jsonify({'error': str(exc)}), 400


@course_v2_bp.route('/<int:course_id>', methods=['DELETE'])
@jwt_required
def delete_course(course_id):
    try:
        _ensure_instructor_or_admin()
        delete_course_service(course_id)
        return jsonify({'message': 'Course deleted'}), 200
    except PermissionError as exc:
        return jsonify({'error': str(exc)}), 403