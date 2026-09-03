# controller/progress_controller.py
"""Blueprint for student progress view (Phase 6)."""

from flask import Blueprint, jsonify, render_template, request
from utils.jwt_util import jwt_required
from service.progress_service import get_my_progress

progress_bp = Blueprint('progress', __name__, url_prefix='/courses')

@progress_bp.route('/<int:course_id>/progress', methods=['GET'])
@jwt_required
def my_progress(course_id):
    try:
        data = get_my_progress(course_id)
        if 'text/html' in request.headers.get('Accept', ''):
            return render_template('progress/progress.html', course_id=course_id, progress=data), 200
        return jsonify(data), 200
    except PermissionError as exc:
        return jsonify({'error': str(exc)}), 401
