# controller/v2/register_blueprints_v2.py
"""
Register all v2 API blueprints.
"""

def register_v2_blueprints(app):
    from .auth_controller_v2 import auth_v2_bp
    from .course_controller_v2 import course_v2_bp
    from .module_controller_v2 import module_v2_bp
    from .lesson_controller_v2 import lesson_v2_bp
    from .material_controller_v2 import material_v2_bp
    from .quiz_controller_v2 import quiz_v2_bp
    from .progress_controller_v2 import progress_v2_bp
    from .enrollment_controller_v2 import enrollment_v2_bp
    from .admin_controller_v2 import admin_v2_bp

    app.register_blueprint(auth_v2_bp)
    app.register_blueprint(course_v2_bp)
    app.register_blueprint(module_v2_bp)
    app.register_blueprint(lesson_v2_bp)
    app.register_blueprint(material_v2_bp)
    app.register_blueprint(quiz_v2_bp)
    app.register_blueprint(progress_v2_bp)
    app.register_blueprint(enrollment_v2_bp)
    app.register_blueprint(admin_v2_bp)