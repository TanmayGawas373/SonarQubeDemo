from flask import Blueprint, abort, g, render_template, request, redirect, url_for, flash
from service.enrollment_service import _ensure_instructor_or_admin
from utils.jwt_util import jwt_required
from utils.role_check import _ensure_admin
from service.course_service import admin_update_course_service, create_course_service, get_course_service, update_course, delete_course, get_course, list_courses, update_course_service

admin_course_bp = Blueprint('admin_course', __name__)

@admin_course_bp.route('/admin/courses', methods=['GET'])
@jwt_required
def list_admin_courses():
    _ensure_admin()

    search_query = request.args.get('q', '', type=str).strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 10

    courses, total = list_courses(
        search=search_query or None,
        page=page,
        per_page=per_page
    )

    total_pages = max(1, (total + per_page - 1) // per_page)

    if page > total_pages:
        page = total_pages

    return render_template(
        'admin/course_list.html',
        courses=courses,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        search_query=search_query
    )

@admin_course_bp.route('/admin/courses/create', methods=['GET', 'POST'])
@jwt_required
def create_admin_course():
    _ensure_admin()
    if request.method == 'GET':
        instructors = get_all_instructors_service()
        return render_template('admin/create_course.html', instructors=instructors)
    if request.method == 'POST':
            title = request.form['title']
            description = request.form.get('description', '')
            instructor_id = request.form.get('instructor_id')
            create_course_service({"title": title, "description": description, "instructor_id": instructor_id})
            flash('Course created', 'success')
            return redirect(url_for('admin_course.list_admin_courses'))

from service.user_service import get_all_instructors_service


@admin_course_bp.route(
    '/admin/courses/<int:course_id>/edit',
    methods=['GET', 'POST']
)
@jwt_required
def edit_admin_course(course_id):

    _ensure_instructor_or_admin()

    course = get_course_service(course_id)

    instructors = get_all_instructors_service()

    

    if request.method == 'GET':
        return render_template(
            'admin/edit_course.html',
            course=course,
            instructors=instructors
        )

    title = request.form.get('title')
    description = request.form.get('description', '')
    instructor_id = request.form.get('instructor_id')

    if not title:
        return render_template(
            'admin/edit_course.html',
            course=course,
            instructors=instructors,
            error='Course title is required'
        ), 400

    if not instructor_id:
        return render_template(
            'admin/edit_course.html',
            course=course,
            instructors=instructors,
            error='Instructor is required'
        ), 400

    admin_update_course_service(
        course.id,
        {
            'title': title,
            'description': description,
            'instructor_id': int(instructor_id)
        }
    )


    jwt_user = getattr(g, 'current_user', None)
    if jwt_user:
        if jwt_user.get('role') != 'admin':
            return redirect(url_for('instructor_ui.courses'))
        else:
            return redirect(url_for('admin_course.list_admin_courses'))

@admin_course_bp.route('/admin/courses/<int:course_id>/delete', methods=['POST'])
@jwt_required
def delete_admin_course(course_id):
    _ensure_instructor_or_admin()
    delete_course(course_id)
    flash('Course deleted', 'info')
    return redirect(url_for('admin_course.list_admin_courses'))
