from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from utils.role_check import _ensure_student, get_current_user_id, _ensure_instructor_or_admin
from service.module_service import get_module_service
from utils.jwt_util import jwt_required
from service.lesson_service import (
    create_lesson_service,
    get_lesson_service,
    list_lessons_service,
    update_lesson_service,
    delete_lesson_service,
    complete_lesson_service,
)

lesson_bp = Blueprint('lesson', __name__, url_prefix='/modules/<int:module_id>/lessons')

@lesson_bp.route('', methods=['POST'])
@jwt_required
def create_lesson(module_id):
    try:
        data = request.form if request.form else request.get_json()
        l = create_lesson_service(module_id, data)
        if request.form:
            flash('Lesson created.', 'success')
            return redirect(request.referrer or url_for('dashboard.home'))
        return jsonify({'id': l.id, 'title': getattr(l, 'title', None)}), 201
    except (PermissionError, ValueError) as exc:
        return jsonify({'error': str(exc)}), 400

@lesson_bp.route('/create-lesson', methods=['GET'])
@jwt_required
def lesson_form(module_id):
    _ensure_instructor_or_admin()
    module = get_module_service(module_id)
    return render_template(
        'lesson/create_lesson.html',
        module = module,
        module_id=module_id
    )

@lesson_bp.route('/<int:lesson_id>/edit-lesson', methods=['GET'])
@jwt_required
def lesson_edit_form(module_id, lesson_id):
    _ensure_instructor_or_admin()
    module = get_module_service(module_id)
    lesson = get_lesson_service(lesson_id)
    return render_template(
        'lesson/edit_lesson.html',
        module = module,
        module_id=module_id,
        lesson = lesson,
        lesson_id = lesson_id
    )

@lesson_bp.route('', methods=['GET'])
def list_lessons(module_id):
    lessons = list_lessons_service(module_id)
    payload = [{'id': l.id, 'title': getattr(l, 'title', None)} for l in lessons]
    return jsonify(payload), 200

@lesson_bp.route('/<int:lesson_id>/page', methods=['GET'])
def lesson_page(module_id, lesson_id):
    try:
        l = get_lesson_service(lesson_id)
        return render_template('lesson/lesson.html', lesson=l)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 404
@lesson_bp.route('/<int:lesson_id>', methods=['GET'])
def get_lesson(module_id, lesson_id):
    try:
        l = get_lesson_service(lesson_id)
        return jsonify({'id': l.id, 'title': getattr(l, 'title', None)}), 200
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 404

@lesson_bp.route('/<int:lesson_id>/complete', methods=['POST'])
@jwt_required
def complete_lesson(module_id, lesson_id):
    try:
        lesson = get_lesson_service(lesson_id)
        complete_lesson_service(lesson_id)
        flash('Lesson marked complete.', 'success')
        return redirect(url_for('progress.my_progress', course_id=lesson.module.course_id))
    except (PermissionError, ValueError) as exc:
        return jsonify({'error': str(exc)}), 400

@lesson_bp.route('/<int:lesson_id>', methods=['PUT'])
def update_lesson(module_id, lesson_id):
    try:
        _ensure_instructor_or_admin()
        l = update_lesson_service(lesson_id, request.form if request.form else request.get_json())
        return jsonify({'id': l.id, 'title': getattr(l, 'title', None)}), 200
    except (PermissionError, ValueError) as exc:
        return jsonify({'error': str(exc)}), 400

@lesson_bp.route('/<int:lesson_id>', methods=['DELETE'])
def delete_lesson(module_id, lesson_id):
    try:
        _ensure_instructor_or_admin()

        delete_lesson_service(lesson_id)

        return jsonify({
            'message': 'Lesson deleted'
        }), 200

    except PermissionError as exc:
        return jsonify({
            'error': str(exc)
        }), 403

    except ValueError as exc:
        return jsonify({
            'error': str(exc)
        }), 404
