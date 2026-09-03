from flask import Blueprint, render_template, redirect, url_for, flash, request
from utils.jwt_util import jwt_required
from utils.role_check import _ensure_student
from service.enrollment_service import enroll_student, unenroll_student, list_my_enrollments, list_my_enrollments_paginated

enroll_ui_bp = Blueprint('enroll_ui', __name__)

@enroll_ui_bp.route('/my/enrollments', methods=['GET'])
@jwt_required
def my_enrollments():
    _ensure_student()

    PAGE_SIZE = 10
    page = max(1, int(request.args.get('page', 1)))
    search = request.args.get('search', '').strip()

    data = list_my_enrollments_paginated(page=page, per_page=PAGE_SIZE, search=search or None)
    page = min(page, data['total_pages'])

    return render_template(
        'enrollment/my_enrollments.html',
        enrollments=data['results'],
        page=data['page'],
        total_pages=data['total_pages'],
        total=data['total'],
        search=search
    )

@enroll_ui_bp.route('/courses/<int:course_id>/enroll', methods=['POST'])
@jwt_required
def enroll(course_id):
    _ensure_student()
    enroll_student(course_id)
    flash('Enrolled successfully', 'success')
    return redirect(url_for('course.course_detail', course_id=course_id))

@enroll_ui_bp.route('/courses/<int:course_id>/unenroll', methods=['POST'])
@jwt_required
def unenroll(course_id):
    _ensure_student()
    unenroll_student(course_id)
    flash('Unenrolled successfully', 'info')
    return redirect(url_for('enroll_ui.my_enrollments', course_id=course_id))
