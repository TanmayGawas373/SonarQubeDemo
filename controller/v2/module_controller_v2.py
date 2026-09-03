# controller/v2/module_controller_v2.py
"""
v2 Module API - JSON only endpoints.
"""

from flask import Blueprint, request, jsonify
from utils.jwt_util import jwt_required
from service.course_service import get_course_service
from utils.role_check import _ensure_instructor_or_admin
from service.module_service import (
    create_module_service,
    get_module_service,
    list_modules_service,
    update_module_service,
    delete_module_service,
)

module_v2_bp = Blueprint('module_v2', __name__, url_prefix='/api/v2/courses/<int:course_id>/modules')


@module_v2_bp.route('', methods=['POST'])
@jwt_required
def create_module(course_id):
    try:
        _ensure_instructor_or_admin()
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON body required'}), 400
        
        m = create_module_service(course_id, data)
        return jsonify({
            'id': m.id,
            'title': getattr(m, 'title', None),
            'course_id': course_id,
            'order': getattr(m, 'order', None)
        }), 201
    except (PermissionError, ValueError) as exc:
        return jsonify({'error': str(exc)}), 400


@module_v2_bp.route('', methods=['GET'])
@jwt_required
def list_modules(course_id):
    try:
        modules = list_modules_service(course_id)
        payload = [
            {
                'id': m.id,
                'title': getattr(m, 'title', None),
                'order': getattr(m, 'order', None)
            }
            for m in modules
        ]
        return jsonify(payload), 200
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 404


@module_v2_bp.route('/<int:module_id>', methods=['GET'])
@jwt_required
def get_module(course_id, module_id):
    try:
        m = get_module_service(module_id)
        return jsonify({
            'id': m.id,
            'title': getattr(m, 'title', None),
            'course_id': course_id,
            'order': getattr(m, 'order', None)
        }), 200
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 404


@module_v2_bp.route('/<int:module_id>', methods=['PUT'])
@jwt_required
def update_module(course_id, module_id):
    try:
        _ensure_instructor_or_admin()
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON body required'}), 400
        
        m = update_module_service(module_id, data)
        return jsonify({
            'id': m.id,
            'title': getattr(m, 'title', None),
            'order': getattr(m, 'order', None)
        }), 200
    except (PermissionError, ValueError) as exc:
        return jsonify({'error': str(exc)}), 400


@module_v2_bp.route('/<int:module_id>', methods=['DELETE'])
@jwt_required
def delete_module(course_id, module_id):
    try:
        _ensure_instructor_or_admin()
        delete_module_service(module_id)
        return jsonify({'message': 'Module deleted'}), 200
    except PermissionError as exc:
        return jsonify({'error': str(exc)}), 403