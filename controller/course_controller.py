from flask import Blueprint, request, jsonify, render_template, g, redirect, url_for, flash
from service.enrollment_service import _ensure_instructor_or_admin, list_my_enrollments
from utils.jwt_util import jwt_required
from service.course_service import (
    create_course_service,
    get_course_service,
    list_courses_service,
    update_course_service,
    delete_course_service,
)

course_bp = Blueprint('course', __name__, url_prefix='/courses')

@course_bp.route('', methods=['POST'])
@jwt_required
def create_course():
    try:
        _ensure_instructor_or_admin()
        data = request.form if request.form else request.get_json()
        course = create_course_service(data)
        if request.form:
            flash('Course created.', 'success')
            return redirect(url_for('dashboard.home'))
        return jsonify({'id': course.id, 'title': getattr(course, 'title', None)}), 201
    except (PermissionError, ValueError) as exc:
        return jsonify({'error': str(exc)}), 400

@course_bp.route('', methods=['GET'])
@jwt_required
def list_courses():
    query = request.args.get('q')
    page = int(request.args.get('page', 1))
    per_page = 10

    jwt_user = getattr(g, 'current_user', None)

    courses, total = list_courses_service(
        search=query,
        page=page,
        per_page=per_page
    )

    enrolled_courses_ids = set()

    if jwt_user and jwt_user.get('role') == 'student':
        enrolled_courses_ids = {e.course_id for e in list_my_enrollments()}

    if 'text/html' in request.headers.get('Accept', ''):
        total_pages = max(1, (total + per_page - 1) // per_page)
        return render_template(
            'course/course_list.html',
            courses=courses,
            enrolled_courses_ids=enrolled_courses_ids,
            query=query,
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages
        )

    payload = [
        {
            'id': c.id,
            'title': getattr(c, 'title', None)
        }
        for c in courses
    ]

    return jsonify({
        'page': page,
        'per_page': per_page,
        'total': total,
        'courses': payload,
    }), 200

@course_bp.route('/<int:course_id>/view', methods=['GET'])
def course_detail(course_id):
    try:
        course = get_course_service(course_id)
        print(course.to_dict())

        return render_template(
            'course/course_detail.html',
            course=course,
            user=getattr(g, 'current_user', None)
        )

    except ValueError:
        return "Course not found", 404


@course_bp.route('/<int:course_id>', methods=['GET'])
def get_course(course_id):
    try:
        c = get_course_service(course_id)
        return jsonify({'id': c.id, 'title': getattr(c, 'title', None)}), 200
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 404

@course_bp.route('/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    try:
        _ensure_instructor_or_admin()
        c = update_course_service(course_id, request.get_json())
        return jsonify({'id': c.id, 'title': getattr(c, 'title', None)}), 200
    except (PermissionError, ValueError) as exc:
        return jsonify({'error': str(exc)}), 400

@course_bp.route('/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    try:
        _ensure_instructor_or_admin()
        delete_course_service(course_id)
        return jsonify({'message': 'Course deleted'}), 200
    except PermissionError as exc:
        return jsonify({'error': str(exc)}), 403
