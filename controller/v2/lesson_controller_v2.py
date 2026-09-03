# controller/v2/lesson_controller_v2.py
"""
v2 Lesson API - JSON only endpoints.
"""

from flask import Blueprint, request, jsonify
from utils.jwt_util import jwt_required
from service.module_service import get_module_service
from utils.role_check import _ensure_student, get_current_user_id, _ensure_instructor_or_admin
from dao.lesson_completion_dao import mark_completed
from service.lesson_service import (
    create_lesson_service,
    get_lesson_service,
    list_lessons_service,
    update_lesson_service,
    delete_lesson_service,
)

lesson_v2_bp = Blueprint('lesson_v2', __name__, url_prefix='/api/v2/modules/<int:module_id>/lessons')


@lesson_v2_bp.route('', methods=['POST'])
@jwt_required
def create_lesson(module_id):
    try:
        _ensure_instructor_or_admin()
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON body required'}), 400
        
        l = create_lesson_service(module_id, data)
        return jsonify({
            'id': l.id,
            'title': getattr(l, 'title', None),
            'content': getattr(l, 'content', None),
            'module_id': module_id,
            'order': getattr(l, 'order', None)
        }), 201
    except (PermissionError, ValueError) as exc:
        return jsonify({'error': str(exc)}), 400


@lesson_v2_bp.route('', methods=['GET'])
def list_lessons(module_id):
    try:
        lessons = list_lessons_service(module_id)
        payload = [
            {
                'id': l.id,
                'title': getattr(l, 'title', None),
                'content': getattr(l, 'content', None),
                'order': getattr(l, 'order', None)
            }
            for l in lessons
        ]
        return jsonify(payload), 200
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 404


@lesson_v2_bp.route('/<int:lesson_id>', methods=['GET'])
def get_lesson(module_id, lesson_id):
    try:
        l = get_lesson_service(lesson_id)
        return jsonify({
            'id': l.id,
            'title': getattr(l, 'title', None),
            'content': getattr(l, 'content', None),
            'module_id': module_id,
            'order': getattr(l, 'order', None)
        }), 200
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 404


@lesson_v2_bp.route('/<int:lesson_id>/complete', methods=['POST'])
@jwt_required
def complete_lesson(module_id, lesson_id):
    try:
        _ensure_student()
        lesson = get_lesson_service(lesson_id)
        mark_completed(get_current_user_id(), lesson_id)
        return jsonify({
            'message': 'Lesson marked complete',
            'lesson_id': lesson_id
        }), 200
    except (PermissionError, ValueError) as exc:
        return jsonify({'error': str(exc)}), 400


@lesson_v2_bp.route('/<int:lesson_id>', methods=['PUT'])
@jwt_required
def update_lesson(module_id, lesson_id):
    try:
        _ensure_instructor_or_admin()
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON body required'}), 400
        
        l = update_lesson_service(lesson_id, data)
        return jsonify({
            'id': l.id,
            'title': getattr(l, 'title', None),
            'content': getattr(l, 'content', None),
            'order': getattr(l, 'order', None)
        }), 200
    except (PermissionError, ValueError) as exc:
        return jsonify({'error': str(exc)}), 400


@lesson_v2_bp.route('/<int:lesson_id>', methods=['DELETE'])
@jwt_required
def delete_lesson(module_id, lesson_id):
    try:
        _ensure_instructor_or_admin()
        delete_lesson_service(lesson_id)
        return jsonify({'message': 'Lesson deleted'}), 200
    except PermissionError as exc:
        return jsonify({'error': str(exc)}), 403
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 404