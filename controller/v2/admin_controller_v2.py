# controller/v2/admin_controller_v2.py
"""
v2 Admin API - JSON only endpoints.
"""

from flask import Blueprint, request, jsonify, abort
from utils.jwt_util import jwt_required
from utils.role_check import _ensure_admin
from service.user_service import (
    get_all_users_service,
    get_user_by_id_service,
    update_user_service,
    delete_user_service,
)
from service.course_service import list_courses_service, get_course_service
from config.db import db
from models.user import User
from models.course import Course
from models.enrollment import Enrollment
from models.quiz_result import QuizResult
from sqlalchemy import func

admin_v2_bp = Blueprint('admin_v2', __name__, url_prefix='/api/v2/admin')


@admin_v2_bp.route('/dashboard', methods=['GET'])
@jwt_required
def dashboard():
    _ensure_admin()
    
    # Core Counts
    total_users = db.session.query(User).count()
    course_count = db.session.query(Course).count()
    enrollment_count = db.session.query(Enrollment).count()
    quiz_attempts_count = db.session.query(QuizResult).count()
    
    # User Distribution
    student_count = db.session.query(User).filter_by(role='student').count()
    instructor_count = db.session.query(User).filter_by(role='instructor').count()
    admin_count = db.session.query(User).filter_by(role='admin').count()
    
    # Most Popular Courses
    popular_courses_query = db.session.query(
        Course.title, func.count(Enrollment.id).label('student_count')
    ).join(
        Enrollment, Course.id == Enrollment.course_id
    ).group_by(
        Course.id
    ).order_by(
        func.count(Enrollment.id).desc()
    ).limit(5).all()
    
    popular_courses = [
        {
            'title': title,
            'student_count': count
        }
        for title, count in popular_courses_query
    ]
    
    # Quiz Analytics
    results = db.session.query(QuizResult.score).all()
    avg_score = 0.0
    pass_rate = 0.0
    if results:
        scores = [r[0] for r in results]
        avg_score = sum(scores) / len(scores)
        passed = sum(1 for s in scores if s >= 70.0)
        pass_rate = (passed / len(scores)) * 100.0
    
    return jsonify({
        'total_users': total_users,
        'course_count': course_count,
        'enrollment_count': enrollment_count,
        'quiz_attempts_count': quiz_attempts_count,
        'user_distribution': {
            'students': student_count,
            'instructors': instructor_count,
            'admins': admin_count
        },
        'popular_courses': popular_courses,
        'quiz_analytics': {
            'average_score': round(avg_score, 1),
            'pass_rate': round(pass_rate, 1)
        }
    }), 200


@admin_v2_bp.route('/users', methods=['GET'])
@jwt_required
def list_users():
    _ensure_admin()
    
    search_query = request.args.get('q', '', type=str).strip()
    role_filter = request.args.get('role', '', type=str).strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 10
    
    combined_search = search_query
    if role_filter:
        combined_search = role_filter
    
    users, total = get_all_users_service(
        search=combined_search or None,
        page=page,
        per_page=per_page
    )
    
    total_pages = max(1, (total + per_page - 1) // per_page)
    
    if page > total_pages:
        page = total_pages
    
    payload = [
        {
            'id': u.id,
            'email': u.email,
            'role': u.role,
            'created_at': u.created_at.isoformat() if u.created_at else None
        }
        for u in users
    ]
    
    return jsonify({
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'users': payload
    }), 200


@admin_v2_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required
def get_user(user_id):
    _ensure_admin()
    
    user = get_user_by_id_service(user_id)
    if not user:
        abort(404, description='User not found')
    
    return jsonify({
        'id': user.id,
        'email': user.email,
        'role': user.role,
        'created_at': user.created_at.isoformat() if user.created_at else None
    }), 200


@admin_v2_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required
def update_user(user_id):
    _ensure_admin()
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400
    
    email = data.get('email')
    role = data.get('role')
    
    if not email or not role:
        return jsonify({'error': 'Email and role are required'}), 400
    
    updated_user = update_user_service(
        user_id=user_id,
        email=email,
        role=role
    )
    
    if not updated_user:
        abort(404, description='User not found')
    
    return jsonify({
        'id': updated_user.id,
        'email': updated_user.email,
        'role': updated_user.role
    }), 200


@admin_v2_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required
def delete_user(user_id):
    _ensure_admin()
    
    success = delete_user_service(user_id)
    
    if not success:
        abort(404, description='User not found')
    
    return jsonify({
        'message': 'User deleted successfully'
    }), 200


@admin_v2_bp.route('/courses', methods=['GET'])
@jwt_required
def list_courses():
    _ensure_admin()
    
    search_query = request.args.get('q', '', type=str).strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 10
    
    courses, total = list_courses_service(
        search=search_query or None,
        page=page,
        per_page=per_page
    )
    
    total_pages = max(1, (total + per_page - 1) // per_page)
    
    if page > total_pages:
        page = total_pages
    
    payload = [
        {
            'id': c.id,
            'title': c.title,
            'description': c.description,
            'instructor_id': c.instructor_id,
            'created_at': c.created_at.isoformat() if c.created_at else None
        }
        for c in courses
    ]
    
    return jsonify({
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'courses': payload
    }), 200


@admin_v2_bp.route('/courses/<int:course_id>', methods=['GET'])
@jwt_required
def get_course(course_id):
    _ensure_admin()
    
    try:
        course = get_course_service(course_id)
        return jsonify({
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'instructor_id': course.instructor_id,
            'created_at': course.created_at.isoformat() if course.created_at else None
        }), 200
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 404


@admin_v2_bp.route('/courses/<int:course_id>', methods=['PUT'])
@jwt_required
def update_course(course_id):
    _ensure_admin()
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400
    
    from service.course_service import admin_update_course_service, get_course_service
    
    try:
        # Get existing course to preserve instructor_id if not provided
        existing_course = get_course_service(course_id)
        instructor_id = data.get('instructor_id', existing_course.instructor_id)
        
        admin_update_course_service(
            course_id,
            {
                'title': data.get('title'),
                'description': data.get('description', ''),
                'instructor_id': instructor_id
            }
        )
        return jsonify({'message': 'Course updated successfully'}), 200
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400


@admin_v2_bp.route('/courses/<int:course_id>', methods=['DELETE'])
@jwt_required
def delete_course(course_id):
    _ensure_admin()
    
    from service.course_service import delete_course_service
    
    try:
        delete_course_service(course_id)
        return jsonify({'message': 'Course deleted successfully'}), 200
    except PermissionError as exc:
        return jsonify({'error': str(exc)}), 403