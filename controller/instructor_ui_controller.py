from flask import Blueprint, render_template, g, redirect, url_for, request
from service.course_service import list_courses_service
from service.dashboard_service import get_instructor_dashboard_service
from service.quiz_service import get_instructor_students_service, get_instructor_quiz_results_paginated_service, get_instructor_students_paginated_service
from service.user_service import get_user_by_id_service
from utils.jwt_util import jwt_required
from utils.role_check import _ensure_instructor

instructor_ui_bp = Blueprint('instructor_ui', __name__)

@instructor_ui_bp.route('/instructor', methods=['GET'])
@jwt_required
def dashboard():
    _ensure_instructor()

    user = g.current_user
    instructor_id = int(user['sub'])
    full_name = get_user_by_id_service(instructor_id).to_dict()["full_name"]
    courses, course_count = list_courses_service()

    taught_courses = [c for c in courses if c.instructor_id == instructor_id]
    stats = get_instructor_dashboard_service(instructor_id)

    return render_template(
        'dashboard/instructor_dashboard.html',
        taught_courses=taught_courses,
        full_name=full_name,
        user=user,
        stats=stats
    )

@instructor_ui_bp.route('/instructor/courses', methods=['GET'])
@jwt_required
def courses():
    _ensure_instructor()
    user = g.current_user
    instructor_id = int(user['sub'])

    PAGE_SIZE = 10
    page = max(1, int(request.args.get('page', 1)))
    search = request.args.get('search', '').strip()

    all_courses, total_all = list_courses_service(search=search or None)
    taught_courses = [c for c in all_courses if c.instructor_id == instructor_id]

    total = len(taught_courses)
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = min(page, total_pages)
    start = (page - 1) * PAGE_SIZE
    paginated_courses = taught_courses[start:start + PAGE_SIZE]

    return render_template(
        'dashboard/instructor_courses.html',
        taught_courses=paginated_courses,
        user=user,
        page=page,
        total_pages=total_pages,
        total=total,
        search=search
    )

@instructor_ui_bp.route('/instructor/create-course', methods=['GET'])
@jwt_required
def create_course():
    _ensure_instructor()
    return render_template('dashboard/instructor_create_course.html', user=g.current_user)

@instructor_ui_bp.route('/instructor/students', methods=['GET'])
@jwt_required
def students():
    _ensure_instructor()
    user = g.current_user
    instructor_id = int(user['sub'])
    
    # Pagination and search parameters
    PAGE_SIZE = 10
    page = int(request.args.get('page', 1))
    search = request.args.get('search', '').strip()

    data = get_instructor_students_paginated_service(instructor_id, page, PAGE_SIZE, search)
    
    students_data = []
    for enroll, stu, crs in data['results']:
        students_data.append({
            "email": stu.email,
            "course_title": crs.title,
            "enrolled_at": enroll.enrolled_at.strftime('%Y-%m-%d %H:%M')
        })

    return render_template(
        'dashboard/instructor_students.html',
        students_data=students_data,
        user=user,
        page=data['page'],
        total_pages=data['total_pages'],
        search=search
    )

@instructor_ui_bp.route('/instructor/quiz-results', methods=['GET'])
@jwt_required
def quiz_results():
    _ensure_instructor()
    user = g.current_user
    instructor_id = int(user['sub'])

    # Pagination and search parameters
    PAGE_SIZE = 10
    page = int(request.args.get('page', 1))
    search = request.args.get('search', '').strip()

    data = get_instructor_quiz_results_paginated_service(instructor_id, page, PAGE_SIZE, search)

    results_data = []
    for r, stu, q, crs in data['results']:
        results_data.append({
            "result_id": r.id,
            "quiz_id": q.id,
            "course_id": crs.id,
            "student_email": stu.email,
            "quiz_title": q.title,
            "course_title": crs.title,
            "score": int(r.score),
            "submitted_at": r.submitted_at.strftime('%Y-%m-%d %H:%M')
        })

    return render_template(
        'dashboard/instructor_quizzes.html',
        results_data=results_data,
        user=user,
        page=data['page'],
        total_pages=data['total_pages'],
        search=search
    )