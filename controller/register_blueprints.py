from flask import Blueprint

def register_blueprints(app):
    # Register protected blueprint for role tests
    from .protected_controller import protected_bp
    from .auth_controller import auth_bp
    from .course_controller import course_bp
    from .module_controller import module_bp
    from .lesson_controller import lesson_bp
    from .material_controller import material_bp
    from .quiz_controller import quiz_bp
    from .progress_controller import progress_bp
    from .enrollment_controller import enroll_bp
    from .enrollment_ui_controller import enroll_ui_bp
    from .admin_course_controller import admin_course_bp
    from .admin_ui_controller import admin_ui_bp
    from .dashboard_controller import dashboard_bp
    from .instructor_ui_controller import instructor_ui_bp

    app.register_blueprint(protected_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(module_bp)
    app.register_blueprint(lesson_bp)
    app.register_blueprint(material_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(progress_bp)
    # app.register_blueprint(enroll_bp)
    app.register_blueprint(enroll_ui_bp)
    app.register_blueprint(dashboard_bp)
    # app.register_blueprint(admin_bp)
    app.register_blueprint(admin_course_bp)
    app.register_blueprint(admin_ui_bp)
    app.register_blueprint(instructor_ui_bp)
