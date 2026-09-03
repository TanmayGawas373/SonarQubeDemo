# controller/quiz_controller.py
"""Blueprint exposing quiz management and attempt endpoints.
Routes (all under ``/courses/<course_id>/quizzes``):
* POST   ``/``                – instructor creates a quiz
* GET    ``/``                – list quizzes for a course
* GET    ``/<quiz_id>``       – retrieve quiz metadata (no questions)
* DELETE ``/<quiz_id>``       – instructor deletes a quiz
* POST   ``/<quiz_id>/questions`` – instructor adds a question
* GET    ``/<quiz_id>/questions`` – list questions for a quiz
* DELETE ``/questions/<question_id>`` – instructor deletes a question
* POST   ``/<quiz_id>/attempt`` – student submits answers
* GET    ``/my/results``       – student lists own attempts
* GET    ``/<quiz_id>/results`` – instructor lists attempts for a quiz
"""

from flask import Blueprint, g, request, jsonify, redirect, url_for, flash, render_template
from utils.role_check import _ensure_instructor_or_admin
from utils.jwt_util import jwt_required
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
from utils.role_check import get_current_user_id
from flask import render_template


quiz_bp = Blueprint("quiz", __name__, url_prefix="/courses/<int:course_id>/quizzes")

@quiz_bp.route("/<int:quiz_id>/take", methods=["GET"])
def take_quiz(course_id, quiz_id):
    try:
        quiz = get_quiz_service(quiz_id)
        questions = list_questions_service(quiz_id)
        return render_template("quiz.html", quiz=quiz, questions=questions, course_id=course_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404



@quiz_bp.route("/view", methods=["GET"])
def view_quizzes(course_id):
    user = getattr(g, 'current_user', None)
    quizzes = list_quizzes_service(course_id)
    return render_template("quiz_list.html", quizzes=quizzes, course_id=course_id, user=user)

@quiz_bp.route("/create", methods=["GET", "POST"])
@jwt_required
def create_quiz(course_id):
    _ensure_instructor_or_admin()
    if request.method == "GET":
        return render_template(
            "quiz/create_quiz.html",
            course_id=course_id
        )

    try:
        quiz = create_quiz_service(
            course_id,
            request.form
        )
        flash('Quiz created. Add questions next.', 'success')
        return redirect(url_for('quiz.manage_quiz', course_id=course_id, quiz_id=quiz.id))

    except (PermissionError, ValueError) as exc:
        return jsonify({
            "error": str(exc)
        }), 400

@quiz_bp.route("", methods=["GET"])
def list_quizzes(course_id):
    quizzes = list_quizzes_service(course_id)
    payload = [{"id": q.id, "title": q.title} for q in quizzes]
    return jsonify(payload), 200

@quiz_bp.route("/<int:quiz_id>", methods=["GET"])
def get_quiz(course_id, quiz_id):
    try:
        q = get_quiz_service(quiz_id)
        return jsonify({"id": q.id, "title": q.title, "course_id": q.course_id}), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404

@quiz_bp.route("/<int:quiz_id>", methods=["DELETE"])
@jwt_required
def delete_quiz(course_id, quiz_id):
    try:
        _ensure_instructor_or_admin()

        delete_quiz_service(quiz_id)

        return jsonify({
            "message": "Quiz deleted successfully"
        }), 200

    except (PermissionError, ValueError) as exc:
        return jsonify({
            "error": str(exc)
        }), 400

@quiz_bp.route("/<int:quiz_id>/questions", methods=["POST"])
@jwt_required
def add_question(quiz_id, course_id):
    try:
        _ensure_instructor_or_admin()
        if request.form:
            options = []
            correct = request.form.get('correct_option')
            for index in range(1, 5):
                text = request.form.get(f'option_{index}')
                if text:
                    options.append({'option': text, 'is_correct': str(index) == correct})
            data = {'prompt': request.form.get('prompt'), 'options': options}
        else:
            data = request.get_json()
        q = add_question_service(quiz_id, data)
        if request.form:
            flash('Question added.', 'success')
            return redirect(url_for('quiz.manage_quiz', course_id=course_id, quiz_id=quiz_id))
        return jsonify({"id": q.id, "prompt": q.prompt}), 201
    except (PermissionError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400

@quiz_bp.route("/<int:quiz_id>/questions", methods=["GET"])
def list_questions(quiz_id, course_id):
    qs = list_questions_service(quiz_id)
    payload = [{"id": q.id, "prompt": q.prompt, "options": q.get_options()} for q in qs]
    return jsonify(payload), 200

@quiz_bp.route("/questions/<int:question_id>", methods=["DELETE", "POST"])
@jwt_required
def delete_question(course_id, question_id):
    _ensure_instructor_or_admin()
    try:
        delete_question_service(question_id)
        if request.form or request.method == "POST":
            quiz_id = request.form.get("quiz_id") or request.args.get("quiz_id")
            flash("Question deleted.", "success")
            if quiz_id:
                return redirect(url_for('quiz.manage_quiz', course_id=course_id, quiz_id=quiz_id))
        return jsonify({"message": "Question deleted"}), 200
    except (PermissionError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400

@quiz_bp.route("/<int:quiz_id>/edit", methods=["POST"])
@jwt_required
def edit_quiz(course_id, quiz_id):
    _ensure_instructor_or_admin()
    try:
        title = request.form.get("title")
        update_quiz_service(quiz_id, title)
        flash("Quiz title updated successfully.", "success")
        return redirect(url_for('quiz.manage_quiz', course_id=course_id, quiz_id=quiz_id))
    except (PermissionError, ValueError) as exc:
        flash(str(exc), "danger")
        return redirect(url_for('quiz.manage_quiz', course_id=course_id, quiz_id=quiz_id))

@quiz_bp.route("/<int:quiz_id>/questions/<int:question_id>/edit", methods=["POST"])
@jwt_required
def edit_question(course_id, quiz_id, question_id):
    _ensure_instructor_or_admin()
    try:
        options = []
        correct = request.form.get('correct_option')
        for index in range(1, 5):
            text = request.form.get(f'option_{index}')
            if text:
                options.append({'option': text, 'is_correct': str(index) == correct})
        data = {'prompt': request.form.get('prompt'), 'options': options}
        update_question_service(question_id, data)
        flash("Question updated successfully.", "success")
        return redirect(url_for('quiz.manage_quiz', course_id=course_id, quiz_id=quiz_id))
    except (PermissionError, ValueError) as exc:
        flash(str(exc), "danger")
        return redirect(url_for('quiz.manage_quiz', course_id=course_id, quiz_id=quiz_id))


@quiz_bp.route("/<int:quiz_id>/attempt", methods=["POST"])
@jwt_required
def attempt_quiz(quiz_id, course_id):
    try:
        answers = {}
        if request.form:
            for key, value in request.form.items():
                if key.startswith('q'):
                    answers[key[1:]] = value
        else:
            answers = request.get_json() if request.is_json else request.form
        result = submit_attempt_service(quiz_id, answers)
        if request.form:
            flash(f'Quiz submitted. Score: {result.score:.1f}%', 'success')
            return redirect(url_for('progress.my_progress', course_id=course_id))
        return jsonify({"id": result.id, "score": result.score}), 201
    except (PermissionError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400

@quiz_bp.route("/my/results", methods=["GET"])
@quiz_bp.route("/my/results/view", methods=["GET"])
@jwt_required
def view_my_results(course_id):
    PAGE_SIZE = 10
    page = int(request.args.get('page', 1))
    search = request.args.get('search', '').strip()
    
    try:
        data = get_student_results_paginated_service(page=page, per_page=PAGE_SIZE, search=search)
        
        results_data = []
        for r, q, crs in data['results']:
            results_data.append({
                "result_id": r.id,
                "quiz_id": q.id,
                "course_id": crs.id,
                "quiz_title": q.title,
                "course_title": crs.title,
                "score": int(r.score),
                "submitted_at": r.submitted_at.strftime('%Y-%m-%d %H:%M')
            })

        return render_template(
            "quiz_results.html",
            course_id=course_id,
            results_data=results_data,
            page=data['page'],
            total_pages=data['total_pages'],
            search=search
        )
    except PermissionError as exc:
        return jsonify({"error": str(exc)}), 401

@quiz_bp.route("/<int:quiz_id>/manage", methods=["GET"])
@jwt_required
def manage_quiz(course_id, quiz_id):
    quiz = get_quiz_service(quiz_id)
    questions = list_questions_service(quiz_id)
    return render_template("quiz/create_quiz.html", course_id=course_id, quiz=quiz, questions=questions)

@quiz_bp.route("/<int:quiz_id>/results", methods=["GET"])
def quiz_results(quiz_id, course_id):
    try:
        res = get_quiz_results_service(quiz_id)
        payload = [
            {
                "student_id": r.student_id,
                "score": r.score,
                "submitted_at": r.submitted_at.isoformat(),
            }
            for r in res
        ]
        return jsonify(payload), 200
    except PermissionError as exc:
        return jsonify({"error": str(exc)}), 403


@quiz_bp.route("/<int:quiz_id>/results/<int:result_id>", methods=["GET"])
@jwt_required
def review_quiz_result(course_id, quiz_id, result_id):
    try:
        result = get_quiz_result_detail_service(result_id)
        quiz = get_quiz_service(quiz_id)
        questions = list_questions_service(quiz_id)
        user = g.current_user
        
        answers = result.get_answers()  # dict of string(question_id) -> option_idx
        
        return render_template(
            "quiz/quiz_attempt_detail.html",
            course_id=course_id,
            quiz=quiz,
            questions=questions,
            answers=answers,
            result=result,
            user=user
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404

