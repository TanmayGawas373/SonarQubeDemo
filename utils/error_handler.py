# utils/error_handler.py
"""Flask error handling utilities.
Registers error handlers to return JSON for API requests or beautiful HTML pages for web pages.
"""

from flask import jsonify, request, render_template

def wants_json_response():
    return request.path.startswith('/api/') or \
           request.accept_mimetypes.best_match(['application/json', 'text/html']) == 'application/json'

def make_error_response(message, code):
    if wants_json_response():
        return jsonify({"error": message}), code
    return render_template('error/error_page.html', message=message, code=code), code

def register_error_handlers(app):
    @app.errorhandler(ValueError)
    def handle_value_error(error):
        return make_error_response(str(error), 400)

    @app.errorhandler(PermissionError)
    def handle_permission_error(error):
        return make_error_response(str(error), 403)

    @app.errorhandler(404)
    def handle_not_found(error):
        return make_error_response("The page or resource you are looking for could not be found.", 404)

    @app.errorhandler(500)
    def handle_internal_error(error):
        # Do not leak internal details in production/general environments
        return make_error_response("An unexpected internal server error occurred. Please try again later.", 500)
