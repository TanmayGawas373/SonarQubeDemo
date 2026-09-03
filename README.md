# README.md

## Learning Management System (P1) – How to Run

### Prerequisites
- **Python 3.10+**
- **MySQL** (or any SQLAlchemy‑compatible database). Create a database for the app and note the connection URL.
- **Virtual environment** – the project ships with a `myvenv` folder but you can create your own:
  ```bash
  python -m venv venv
  source venv/bin/activate   # Unix/macOS
  venv\Scripts\activate    # Windows
  ```

### Install dependencies
```bash
pip install -r requirements.txt
```
(This file is generated in `requirements.txt` during Phase 0; if missing, run `pip freeze > requirements.txt` after installing Flask, Flask‑Login, Flask‑Migrate, etc.)

### Configure the app
1. Copy the example config:
   ```bash
   cp config/.env.example .env
   ```
2. Edit `.env` and set your database URL, e.g.:
   ```
   SQLALCHEMY_DATABASE_URI=mysql+pymysql://user:password@localhost/lms_db
   ```
3. Optionally set `FLASK_ENV=development`.

### Initialise the database
```bash
flask db init      # creates migrations folder
flask db migrate   # generates the initial migration (creates tables)
flask db upgrade   # applies migrations to the DB
```

### Run the development server
```bash
flask run
```
The app will be available at `http://127.0.0.1:5000`.

## Current Implementation Status

- **Authentication & Authorization**: Session‑based login and role checks are implemented. JWT support pending.
- **Course Management**: Full CRUD API with pagination and search available.
- **Enrollment**: API endpoints for enroll/unenroll and views for student and instructor/admin.
- **Learning Content**: Material upload endpoint with validation; download endpoint still missing.
- **Assessments**: Quiz CRUD, attempt, scoring and UI pages are present.
- **Progress Tracking**: Placeholder progress endpoint returning a static percentage; real aggregation pending.
- **Admin Dashboard**: Placeholder admin blueprint with `/admin/users`; UI dashboard page added.
- **UI Templates**: Added `admin/dashboard.html` and `lesson/lesson.html`. Many other templates (login, dashboards, course list/detail, material list/download, enrollment flow, progress page) are still to be created.
- **Testing**: Core tests for auth, course/module/lesson flow exist. Additional tests for enrollment, material handling, quizzes, progress, admin actions are needed.

See `PRD.md` for the full list of required features.

| Area | Method | URL | Description |
|------|--------|-----|-------------|
| **Auth** | `POST /auth/register` | Register a new user (instructor, student, admin) |
| | `POST /auth/login` | Login and set session |
| **Courses** | `GET /courses` | List courses (supports `?q=` search and `?page=` pagination) |
| | `POST /courses` | Create a course (instructor only) |
| **Modules** | `GET /courses/<cid>/modules` | List modules for a course |
| **Lessons** | `GET /modules/<mid>/lessons` | List lessons for a module |
| **Materials** | `POST /modules/<mid>/materials` | Upload a material file (validated) |
| **Enrollments** | `POST /courses/<cid>/enroll` | Student enrolls |
| **Quizzes** | `GET /courses/<cid>/quizzes/view` | View quiz list |
| | `GET /courses/<cid>/quizzes/<qid>/take` | Take a quiz |
| | `POST /courses/<cid>/quizzes/<qid>/attempt` | Submit answers |
| **Progress** | `GET /courses/<cid>/progress` | Student progress view |
| **Admin** | `GET /admin/users` | List users (admin only) |

### Testing
```bash
pytest
```
All tests under `tests/` should pass.

### Phase 8 – Hardening (already integrated)
- Input validation is performed in service layers (e.g., file extensions, size limits, required fields).
- All routes enforce role‑based access via `PermissionError` checks.
- Errors are returned as JSON with appropriate HTTP status codes.

### Phase 9 – Polish (optional enhancements)
- Search and pagination added to course listing (see `list_courses` implementation).
- You can extend other list endpoints similarly.
- Basic admin dashboard placeholder is in `controller/admin_controller.py`.

---
**Enjoy building and extending the LMS!**
