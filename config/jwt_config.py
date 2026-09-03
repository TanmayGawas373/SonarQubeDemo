import os

JWT_SECRET = os.getenv(
    "JWT_SECRET",
    "replace-this-with-a-random-secret-of-at-least-32-bytes"
)

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES = 3600