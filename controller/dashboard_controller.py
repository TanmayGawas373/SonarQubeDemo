import time
from flask import Blueprint, render_template, redirect, url_for, g
from flask_login import current_user, login_required
from service.user_service import get_user_by_id_service
from utils.jwt_util import jwt_required
from service.enrollment_service import list_my_enrollments
from service.progress_service import get_my_progress
from service.quiz_service import get_student_results_service

class SimpleCache:
    def __init__(self):
        self._cache = {}
        
    def get(self, key):
        if key in self._cache:
            val, expiry = self._cache[key]
            if expiry > time.time():
                return val
            else:
                del self._cache[key]
        return None
        
    def set(self, key, value, timeout=10):
        self._cache[key] = (value, time.time() + timeout)

student_cache = SimpleCache()
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@jwt_required
def home():
    user = g.current_user
    role = user['role']
    email = user['email']
    user_id = int(user['sub'])
    full_name = get_user_by_id_service(user_id).to_dict()["full_name"]

    if role == 'student':
        cache_key = f"student_dash_{user_id}"
        cached_data = student_cache.get(cache_key)
        if cached_data:
            return render_template('dashboard/student_dashboard.html', **cached_data)

        

        enrollments = list_my_enrollments()
        enrolled_count = len(enrollments)
        
        completed_count = 0
        course_progresses = []
        for enrollment in enrollments:
            try:
                prog_data = get_my_progress(enrollment.course_id)
                pct = prog_data.get("completion_percent", 0.0)
            except Exception:
                pct = 0.0
            if pct >= 100.0:
                completed_count += 1
            course_progresses.append({
                "id": enrollment.course_id,
                "title": enrollment.course.title,
                "percent": int(pct)
            })

        quiz_results = get_student_results_service()
        avg_score = 0.0
        quiz_performances = []
        if quiz_results:
            avg_score = sum(r.score for r in quiz_results) / len(quiz_results)
            for r in quiz_results:
                status = "Passed" if r.score >= 70.0 else "Failed"
                quiz_performances.append({
                    "id": r.id,
                    "quiz_id": r.quiz_id,
                    "course_id": r.quiz.course_id,
                    "title": r.quiz.title,
                    "score": int(r.score),
                    "status": status
                })

        data_to_render = {
            "user": user,
            "enrolled_count": enrolled_count,
            "completed_count": completed_count,
            "avg_quiz_score": round(avg_score, 1),
            "course_progresses": course_progresses,
            "quiz_performances": quiz_performances,
            "full_name": full_name
        }

        student_cache.set(cache_key, data_to_render, timeout=10)
        return render_template('dashboard/student_dashboard.html', **data_to_render)

    elif role == 'instructor':
        return redirect(url_for('instructor_ui.dashboard'))
    elif role == 'admin':
        return redirect(url_for('admin_ui.dashboard'))
    else:
        return redirect(url_for('auth.login'))