# controller/v2/quiz_controller_v2.py
"""
v2 Quiz API - JSON only endpoints.
"""

from flask import Blueprint, request, jsonify, g
from utils.jwt_util import jwt_required
from utils.role_check import get_current_user_id, _ensure_instructor_or_admin
from service.quiz_service import (
    create_quiz_service,
    list_quizzes_service,
    get_quiz_service,
    delete_quiz_service,
    add_question_service,
    list_questions_service,
    delete_question_service,
    submit_attempt_service,
    get_student_results_service,
    get_quiz_results_service,
    update_quiz_service,
    update_question_service,
    get_quiz_result_detail_service,
    get_student_results_paginated_service,
)

quiz_v2_bp = Blueprint('quiz_v2', __name__, url_prefix='/api/v2/courses/<int:course_id>/quizzes')


@quiz_v2_bp.route('', methods=['POST'])
@jwt_required
def create_quiz(course_id):
    try:
        _ensure_instructor_or_admin()
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON body required'}), 400
        
        quiz = create_quiz_service(course_id, data)
        return jsonify({
            'id': quiz.id,
            'title': quiz.title,
            'course_id': quiz.course_id
        }), 201
    except (PermissionError, ValueError) as exc:
        return jsonify({'error': str(exc)}), 400


@quiz_v2_bp.route('', methods=['GET'])
def list_quizzes(course_id):
    quizzes = list_quizzes_service(course_id)
    payload = [
        {
            'id': q.id,
            'title': q.title,
            'course_id': q.course_id
        }
        for q in quizzes
    ]
    return jsonify(payload), 200


@quiz_v2_bp.route('/<int:quiz_id>', methods=['GET'])
def get_quiz(course_id, quiz_id):
    try:
        q = get_quiz_service(quiz_id)
        return jsonify({
            'id': q.id,
            'title': q.title,
            'course_id': q.course_id
        }), 200
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 404


@quiz_v2_bp.route('/<int:quiz_id>', methods=['PUT'])
@jwt_required
def update_quiz(course_id, quiz_id):
    try:
        _ensure_instructor_or_admin()
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON body required'}), 400
        
        update_quiz_service(quiz_id, data.get('title'))
        return jsonify({'message': 'Quiz updated successfully'}), 200
    except (PermissionError, ValueError) as exc:
        return jsonify({'error': str(exc)}), 400


@quiz_v2_bp.route('/<int:quiz_id>', methods=['DELETE'])
@jwt_required
def delete_quiz(course_id, quiz_id):
    try:
        _ensure_instructor_or_admin()
        delete_quiz_service(quiz_id)
        return jsonify({'message': 'Quiz deleted successfully'}), 200
    except (PermissionError, ValueError) as exc:
        return jsonify({'error': str(exc)}), 400


@quiz_v2_bp.route('/<int:quiz_id>/questions', methods=['POST'])
@jwt_required
def add_question(course_id, quiz_id):
    try:
        _ensure_instructor_or_admin()
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON body required'}), 400
        
        q = add_question_service(quiz_id, data)
        return jsonify({
            'id': q.id,
            'prompt': q.prompt,
            'options': q.get_options()
        }), 201
    except (PermissionError, ValueError) as exc:
        return jsonify({'error': str(exc)}), 400


@quiz_v2_bp.route('/<int:quiz_id>/questions', methods=['GET'])
def list_questions(quiz_id, course_id):
    qs = list_questions_service(quiz_id)
    payload = [
        {
            'id': q.id,
            'prompt': q.prompt,
            'options': q.get_options()
        }
        for q in qs
    ]
    return jsonify(payload), 200


@quiz_v2_bp.route('/questions/<int:question_id>', methods=['DELETE'])
@jwt_required
def delete_question(course_id, question_id):
    try:
        _ensure_instructor_or_admin()
        delete_question_service(question_id)
        return jsonify({'message': 'Question deleted'}), 200
    except (PermissionError, ValueError) as exc:
        return jsonify({'error': str(exc)}), 400


@quiz_v2_bp.route('/questions/<int:question_id>', methods=['PUT'])
@jwt_required
def update_question(course_id, question_id):
    try:
        _ensure_instructor_or_admin()
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON body required'}), 400
        
        update_question_service(question_id, data)
        return jsonify({'message': 'Question updated successfully'}), 200
    except (PermissionError, ValueError) as exc:
        return jsonify({'error': str(exc)}), 400


@quiz_v2_bp.route('/<int:quiz_id>/attempt', methods=['POST'])
@jwt_required
def attempt_quiz(course_id, quiz_id):
    try:
        answers = request.get_json()
        if not answers:
            return jsonify({'error': 'JSON body required with answers'}), 400
        
        result = submit_attempt_service(quiz_id, answers)
        return jsonify({
            'id': result.id,
            'score': result.score,
            'quiz_id': quiz_id
        }), 201
    except (PermissionError, ValueError) as exc:
        return jsonify({'error': str(exc)}), 400


@quiz_v2_bp.route('/my/results', methods=['GET'])
@jwt_required
def view_my_results(course_id):
    try:
        PAGE_SIZE = int(request.args.get('per_page', 10))
        page = int(request.args.get('page', 1))
        search = request.args.get('search', '').strip()
        
        data = get_student_results_paginated_service(page=page, per_page=PAGE_SIZE, search=search)
        
        results_data = [
            {
                'result_id': r.id,
                'quiz_id': q.id,
                'course_id': crs.id,
                'quiz_title': q.title,
                'course_title': crs.title,
                'score': int(r.score),
                'submitted_at': r.submitted_at.isoformat() if r.submitted_at else None
            }
            for r, q, crs in data['results']
        ]
        
        return jsonify({
            'page': data['page'],
            'per_page': data['per_page'],
            'total': data['total_count'],
            'total_pages': data['total_pages'],
            'results': results_data
        }), 200
    except PermissionError as exc:
        return jsonify({'error': str(exc)}), 401


@quiz_v2_bp.route('/<int:quiz_id>/results', methods=['GET'])
@jwt_required
def quiz_results(course_id, quiz_id):
    try:
        res = get_quiz_results_service(quiz_id)
        payload = [
            {
                'student_id': r.student_id,
                'score': r.score,
                'submitted_at': r.submitted_at.isoformat() if r.submitted_at else None
            }
            for r in res
        ]
        return jsonify(payload), 200
    except PermissionError as exc:
        return jsonify({'error': str(exc)}), 403


@quiz_v2_bp.route('/<int:quiz_id>/results/<int:result_id>', methods=['GET'])
@jwt_required
def review_quiz_result(course_id, quiz_id, result_id):
    try:
        result = get_quiz_result_detail_service(result_id)
        quiz = get_quiz_service(quiz_id)
        questions = list_questions_service(quiz_id)
        
        answers = result.get_answers()  # dict of string(question_id) -> option_idx
        
        questions_with_answers = []
        for q in questions:
            q_dict = {
                'id': q.id,
                'prompt': q.prompt,
                'options': q.get_options(),
                'selected_answer': answers.get(str(q.id)),
                'correct_option': q.get_correct_option()
            }
            questions_with_answers.append(q_dict)
        
        return jsonify({
            'result_id': result.id,
            'quiz': {
                'id': quiz.id,
                'title': quiz.title
            },
            'questions': questions_with_answers,
            'score': result.score,
            'submitted_at': result.submitted_at.isoformat() if result.submitted_at else None
        }), 200
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 404