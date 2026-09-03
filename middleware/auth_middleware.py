from flask import g, request, abort
from utils.jwt_util import decode_token

PUBLIC_ENDPOINTS = ['auth.login_jwt','login_jwt','register','auth.register', 'logout', 'auth.logout','static']

def jwt_middleware(app):

    @app.before_request
    def verify_jwt():

        # Always initialize for this request
        if request.endpoint in PUBLIC_ENDPOINTS:
            return None
        g.current_user = None

        token = None

        # --------------------------------------------------
        # 1. Try JWT from cookie
        # --------------------------------------------------
        token = request.cookies.get('access_token')

        if token:
            print("JWT found in cookie")

        # --------------------------------------------------
        # 2. If no cookie, try Authorization header
        # --------------------------------------------------
        if not token:

            auth_header = request.headers.get('Authorization')

            if auth_header:

                if not auth_header.startswith('Bearer '):
                    abort(
                        401,
                        description='Invalid Authorization header format'
                    )

                token = auth_header.split(' ', 1)[1]

                print("JWT found in Authorization header")

        # --------------------------------------------------
        # 3. No JWT anywhere
        # --------------------------------------------------
        if not token:
            print("No JWT found")
            return

        # --------------------------------------------------
        # 4. Decode JWT
        # --------------------------------------------------
        try:

            payload = decode_token(token)

            print("JWT PAYLOAD:", payload)

            # Store decoded JWT for this request
            g.current_user = payload

        except Exception as e:

            print("JWT ERROR:", e)

            abort(
                401,
                description='Invalid or expired token'
            )

    return app