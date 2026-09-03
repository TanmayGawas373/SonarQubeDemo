from flask import (
    Blueprint,
    abort,
    jsonify,
    render_template,
    request,
    redirect,
    url_for
)

from service.course_service import list_courses_service
from service.user_service import (
    get_all_users_service,
    get_user_by_id_service,
    update_user_service,
    delete_user_service
)
from service.dashboard_service import get_admin_dashboard_service

from utils.jwt_util import jwt_required
from utils.role_check import _ensure_admin


admin_ui_bp = Blueprint('admin_ui', __name__)


@admin_ui_bp.route('/admin/dashboard', methods=['GET'])
@jwt_required
def dashboard():
    _ensure_admin()
    
    stats = get_admin_dashboard_service()

    return render_template(
        'admin/admin_dashboard.html',
        total_users=stats['total_users'],
        course_count=stats['course_count'],
        enrollment_count=stats['enrollment_count'],
        quiz_attempts_count=stats['quiz_attempts_count'],
        student_count=stats['student_count'],
        instructor_count=stats['instructor_count'],
        admin_count=stats['admin_count'],
        popular_courses=stats['popular_courses'],
        avg_quiz_score=stats['avg_quiz_score'],
        quiz_pass_rate=stats['quiz_pass_rate']
    )


@admin_ui_bp.route('/admin/users', methods=['GET'])
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

    # Guard against a page number beyond the last available page
    if page > total_pages:
        page = total_pages

    return render_template(
        'admin/users.html',
        users=users,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        search_query=search_query,
        role_filter=role_filter
    )


@admin_ui_bp.route(
    '/admin/users/<int:user_id>/edit',
    methods=['GET', 'POST']
)
@jwt_required
def edit_user(user_id):

    _ensure_admin()

    user = get_user_by_id_service(user_id)

    if not user:
        abort(404, description='User not found')

    # Display edit form
    if request.method == 'GET':
        return render_template(
            'admin/edit_user.html',
            user=user
        )

    # Handle form submission
    email = request.form.get('email')
    role = request.form.get('role')

    if not email or not role:
        return render_template(
            'admin/edit_user.html',
            user=user,
            error='Email and role are required'
        ), 400

    updated_user = update_user_service(
        user_id=user_id,
        email=email,
        role=role
    )

    if not updated_user:
        abort(404, description='User not found')

    return redirect(
        url_for('admin_ui.list_users')
    )


@admin_ui_bp.route(
    '/admin/users/<int:user_id>',
    methods=['DELETE']
)
@jwt_required
def delete_user(user_id):

    _ensure_admin()

    success = delete_user_service(user_id)

    if not success:
        abort(404, description='User not found')

    return jsonify({
        'message': 'User deleted successfully'
    }), 200