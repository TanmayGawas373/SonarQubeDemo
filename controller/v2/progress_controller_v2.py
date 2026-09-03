# controller/v2/progress_controller_v2.py
"""
v2 Progress API - JSON only endpoints.
"""

from flask import Blueprint, request, jsonify, g
from utils.jwt_util import jwt_required
from service.progress_service import get_my_progress
from service.enrollment_service import list_my_enrollments

progress_v2_bp = Blueprint('progress_v2', __name__, url_prefix='/api/v2/courses')


@progress_v2_bp.route('/<int:course_id>/progress', methods=['GET'])
@jwt_required
def my_progress(course_id):
    try:
        data = get_my_progress(course_id)
        return jsonify(data), 200
    except PermissionError as exc:
        return jsonify({'error': str(exc)}), 401





@progress_v2_bp.route('/my/progress', methods=['GET'])
@jwt_required
def my_all_progress():
    """Get progress summary for all enrolled courses."""
    try:
        from service.enrollment_service import list_my_enrollments
        enrollments = list_my_enrollments()
        
        progress_data = []
        for enrollment in enrollments:
            try:
                prog = get_my_progress(enrollment.course_id)
                progress_data.append({
                    'course_id': enrollment.course_id,
                    'course_title': enrollment.course.title,
                    'completion_percent': prog.get('completion_percent', 0),
                    'lessons_completed': prog.get('lessons_completed', 0),
                    'total_lessons': prog.get('total_lessons', 0),
                    'quizzes_taken': prog.get('quizzes_taken', 0),
                    'total_quizzes': prog.get('total_quizzes', 0),
                    'average_score': prog.get('average_score', 0)
                })
            except Exception:
                progress_data.append({
                    'course_id': enrollment.course_id,
                    'course_title': enrollment.course.title,
                    'completion_percent': 0,
                    'lessons_completed': 0,
                    'total_lessons': 0,
                    'quizzes_taken': 0,
                    'total_quizzes': 0,
                    'average_score': 0
                })
        
        return jsonify(progress_data), 200
    except PermissionError as exc:
        return jsonify({'error': str(exc)}), 401