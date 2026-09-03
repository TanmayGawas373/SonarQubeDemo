# controller/v2/material_controller_v2.py
"""
v2 Material API - JSON only endpoints.
"""

from flask import Blueprint, request, jsonify, current_app, send_from_directory, abort
from utils.jwt_util import jwt_required
from service.module_service import get_module_service
from service.material_service import (
    upload_material_service,
    list_materials_service,
    delete_material_service,
)
from service.enrollment_service import is_user_enrolled
from utils.role_check import get_current_user_id, _ensure_instructor_or_admin
from werkzeug.utils import secure_filename
import os

material_v2_bp = Blueprint('material_v2', __name__, url_prefix='/api/v2')


@material_v2_bp.route('/modules/<int:module_id>/materials', methods=['POST'])
@jwt_required
def upload_material(module_id):
    _ensure_instructor_or_admin()
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        material = upload_material_service(module_id, file)
        return jsonify({
            'id': material.id,
            'filename': secure_filename(file.filename),
            'file_path': getattr(material, 'file_path', None),
            'file_type': getattr(material, 'file_type', None),
            'module_id': module_id
        }), 201
    except (PermissionError, ValueError) as exc:
        return jsonify({'error': str(exc)}), 400


@material_v2_bp.route('/modules/<int:module_id>/materials', methods=['GET'])
@jwt_required
def list_materials(module_id):
    try:
        materials = list_materials_service(module_id)
        payload = [
            {
                'id': m.id,
                'filename': os.path.basename(getattr(m, 'file_path', '')),
                'file_path': getattr(m, 'file_path', None),
                'file_type': getattr(m, 'file_type', None),
                'uploaded_by': getattr(m, 'uploaded_by', None),
                'created_at': m.created_at.isoformat() if getattr(m, 'created_at', None) else None
            }
            for m in materials
        ]
        return jsonify(payload), 200
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 404


@material_v2_bp.route('/modules/<int:module_id>/materials/<int:material_id>', methods=['DELETE'])
@jwt_required
def delete_material(module_id, material_id):
    try:
        _ensure_instructor_or_admin()
        delete_material_service(material_id)
        return jsonify({'message': 'Material deleted'}), 200
    except PermissionError as exc:
        return jsonify({'error': str(exc)}), 403
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 404


from utils.logger import log_student_action

@material_v2_bp.route('/courses/<int:course_id>/modules/<int:module_id>/materials/<path:filename>', methods=['GET'])
@jwt_required
def download_material(course_id, module_id, filename):
    user_id = get_current_user_id()
    if not user_id:
        abort(401, description='Authentication required')
    
    # Verify enrollment
    if not is_user_enrolled(user_id=user_id, course_id=course_id):
        abort(403, description='User not enrolled in this course')
    
    # Build absolute path to the upload directory
    upload_root = os.path.join(current_app.root_path, 'uploads', str(module_id))
    # Ensure the requested file resides within the upload_root to prevent path traversal
    safe_path = os.path.abspath(os.path.join(upload_root, filename))
    if not safe_path.startswith(os.path.abspath(upload_root)):
        abort(400, description='Invalid file path')
    if not os.path.isfile(safe_path):
        abort(404, description='File not found')
    
    log_student_action(f"Student (id={user_id}) downloaded material: {filename} from course (id={course_id}) via v2", "info")
    # Use Flask's send_from_directory to stream the file
    return send_from_directory(upload_root, filename, as_attachment=True)