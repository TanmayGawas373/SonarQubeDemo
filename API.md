## Root-Level Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Student/Instructor/Admin dashboard home |
| GET | `/health` | Health check |

---

## Auth Blueprint (`auth_bp`)

| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/register` | Register a new user |
| GET/POST | `/auth/register` | Register (alias) |
| GET/POST | `/login` | Login (sets cookie + returns JWT) |
| GET/POST | `/auth/login` | Login (alias) |
| GET/POST | `/login_jwt` | Login returning JWT token |
| GET/POST | `/auth/login_jwt` | Login JWT (alias) |
| POST | `/logout` | Logout (deletes cookie) |
| POST | `/auth/logout` | Logout (alias) |

---

## Course Blueprint (`course_bp`, prefix `/courses`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/courses` | Create course (instructor/admin) |
| GET | `/courses` | List courses (paginated, searchable) |
| GET | `/courses/<int:course_id>/view` | Course detail page |
| GET | `/courses/<int:course_id>` | Get course JSON |
| PUT | `/courses/<int:course_id>` | Update course (instructor/admin) |
| DELETE | `/courses/<int:course_id>` | Delete course (instructor/admin) |

---

## Module Blueprint (`module_bp`, prefix `/courses/<int:course_id>/modules`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/courses/<course_id>/modules` | Create module (instructor/admin) |
| GET | `/courses/<course_id>/modules/create-module` | Module creation form |
| GET | `/courses/<course_id>/modules/<module_id>/edit-module` | Module edit form |
| GET | `/courses/<course_id>/modules` | List modules |
| GET | `/courses/<course_id>/modules/<module_id>` | Get module |
| PUT | `/courses/<course_id>/modules/<module_id>` | Update module |
| DELETE | `/courses/<course_id>/modules/<module_id>` | Delete module |

---

## Lesson Blueprint (`lesson_bp`, prefix `/modules/<int:module_id>/lessons`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/modules/<module_id>/lessons` | Create lesson (instructor/admin) |
| GET | `/modules/<module_id>/lessons/create-lesson` | Lesson creation form |
| GET | `/modules/<module_id>/lessons/<lesson_id>/edit-lesson` | Lesson edit form |
| GET | `/modules/<module_id>/lessons` | List lessons |
| GET | `/modules/<module_id>/lessons/<lesson_id>/page` | Lesson page (HTML) |
| GET | `/modules/<module_id>/lessons/<lesson_id>` | Get lesson |
| POST | `/modules/<module_id>/lessons/<lesson_id>/complete` | Mark lesson complete (student) |
| PUT | `/modules/<module_id>/lessons/<lesson_id>` | Update lesson |
| DELETE | `/modules/<module_id>/lessons/<lesson_id>` | Delete lesson |

---

## Material Blueprint (`material_bp`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/modules/<module_id>/materials` | Upload material (instructor/admin) |
| GET | `/modules/<module_id>/materials` | List materials |
| GET | `/modules/<module_id>/upload_material` | Upload form |
| DELETE | `/modules/<module_id>/materials/<material_id>` | Delete material |
| GET | `/courses/<course_id>/modules/<module_id>/materials/<path:filename>` | Download material (enrolled users) |

---

## Enrollment Blueprint (`enroll_bp` — **commented out in registration**, but `enroll_ui_bp` is active)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/courses/<course_id>/enroll` | Student enrolls |
| DELETE | `/courses/<course_id>/enroll` | Student unenrolls |
| GET | `/my/enrollments` | List my enrollments (student) |
| GET | `/courses/<course_id>/enrollments` | List course enrollments (instructor/admin) |

### Enrollment UI Blueprint (`enroll_ui_bp` — active)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/my/enrollments` | My enrollments page |
| POST | `/courses/<course_id>/enroll` | Enroll (student, form) |
| POST | `/courses/<course_id>/unenroll` | Unenroll (student, form) |

---

## Progress Blueprint (`progress_bp`, prefix `/courses`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/courses/<course_id>/progress` | Get my progress (JSON or HTML) |

---

## Quiz Blueprint (`quiz_bp`, prefix `/courses/<course_id>/quizzes`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/courses/<course_id>/quizzes/<quiz_id>/take` | Take quiz (HTML) |
| GET | `/courses/<course_id>/quizzes/view` | Quiz list page |
| GET/POST | `/courses/<course_id>/quizzes/create` | Create quiz (instructor/admin) |
| GET | `/courses/<course_id>/quizzes` | List quizzes |
| GET | `/courses/<course_id>/quizzes/<quiz_id>` | Get quiz |
| DELETE | `/courses/<course_id>/quizzes/<quiz_id>` | Delete quiz |
| POST | `/courses/<course_id>/quizzes/<quiz_id>/questions` | Add question |
| GET | `/courses/<course_id>/quizzes/<quiz_id>/questions` | List questions |
| DELETE | `/courses/<course_id>/quizzes/questions/<question_id>` | Delete question |
| POST | `/courses/<course_id>/quizzes/<quiz_id>/edit` | Edit quiz title |
| POST | `/courses/<course_id>/quizzes/<quiz_id>/questions/<question_id>/edit` | Edit question |
| POST | `/courses/<course_id>/quizzes/<quiz_id>/attempt` | Submit quiz attempt |
| GET | `/courses/<course_id>/quizzes/my/results` | My quiz results (HTML) |
| GET | `/courses/<course_id>/quizzes/my/results/view` | My quiz results (HTML alias) |
| GET | `/courses/<course_id>/quizzes/<quiz_id>/manage` | Manage quiz page |
| GET | `/courses/<course_id>/quizzes/<quiz_id>/results` | Quiz results (instructor) |
| GET | `/courses/<course_id>/quizzes/<quiz_id>/results/<result_id>` | Review quiz result |

---

## Protected Blueprint (`protected_bp`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/protected` | Protected route (any logged-in user) |
| GET | `/admin-only` | Admin-only route |

---

## Admin Course Blueprint (`admin_course_bp`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/courses` | List all courses (admin) |
| GET/POST | `/admin/courses/create` | Create course (admin) |
| GET/POST | `/admin/courses/<course_id>/edit` | Edit course (admin/instructor) |
| POST | `/admin/courses/<course_id>/delete` | Delete course (admin/instructor) |

---

## Admin UI Blueprint (`admin_ui_bp`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/dashboard` | Admin dashboard |
| GET | `/admin/users` | List users (admin) |
| GET/POST | `/admin/users/<user_id>/edit` | Edit user (admin) |
| DELETE | `/admin/users/<user_id>` | Delete user (admin) |

---

## Instructor UI Blueprint (`instructor_ui_bp`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/instructor` | Instructor dashboard |
| GET | `/instructor/courses` | Instructor's courses |
| GET | `/instructor/create-course` | Create course form |
| GET | `/instructor/students` | Students list |
| GET | `/instructor/quiz-results` | Quiz results |

---

## V2 API Endpoints (JSON-only, prefix `/api/v2`)

### Auth V2 (`/api/v2/auth`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v2/auth/register` | Register |
| POST | `/api/v2/auth/login` | Login |
| POST | `/api/v2/auth/logout` | Logout |
| GET | `/api/v2/auth/me` | Current user |

### Courses V2 (`/api/v2/courses`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v2/courses` | Create course |
| GET | `/api/v2/courses` | List courses |
| GET | `/api/v2/courses/<course_id>` | Get course |
| PUT | `/api/v2/courses/<course_id>` | Update course |
| DELETE | `/api/v2/courses/<course_id>` | Delete course |

### Modules V2 (`/api/v2/courses/<course_id>/modules`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v2/courses/<course_id>/modules` | Create module |
| GET | `/api/v2/courses/<course_id>/modules` | List modules |
| GET | `/api/v2/courses/<course_id>/modules/<module_id>` | Get module |
| PUT | `/api/v2/courses/<course_id>/modules/<module_id>` | Update module |
| DELETE | `/api/v2/courses/<course_id>/modules/<module_id>` | Delete module |

### Lessons V2 (`/api/v2/modules/<module_id>/lessons`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v2/modules/<module_id>/lessons` | Create lesson |
| GET | `/api/v2/modules/<module_id>/lessons` | List lessons |
| GET | `/api/v2/modules/<module_id>/lessons/<lesson_id>` | Get lesson |
| POST | `/api/v2/modules/<module_id>/lessons/<lesson_id>/complete` | Mark complete |
| PUT | `/api/v2/modules/<module_id>/lessons/<lesson_id>` | Update lesson |
| DELETE | `/api/v2/modules/<module_id>/lessons/<lesson_id>` | Delete lesson |

### Materials V2 (`/api/v2`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v2/modules/<module_id>/materials` | Upload material |
| GET | `/api/v2/modules/<module_id>/materials` | List materials |
| DELETE | `/api/v2/modules/<module_id>/materials/<material_id>` | Delete material |
| GET | `/api/v2/courses/<course_id>/modules/<module_id>/materials/<path:filename>` | Download material |

### Enrollment V2 (`/api/v2`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v2/courses/<course_id>/enroll` | Enroll |
| DELETE | `/api/v2/courses/<course_id>/enroll` | Unenroll |
| GET | `/api/v2/my/enrollments` | My enrollments |
| GET | `/api/v2/courses/<course_id>/enrollments` | Course enrollments |

### Progress V2 (`/api/v2/courses`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v2/courses/<course_id>/progress` | My progress |
| GET | `/api/v2/my/progress` | All my progress |

### Quizzes V2 (`/api/v2/courses/<course_id>/quizzes`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v2/courses/<course_id>/quizzes` | Create quiz |
| GET | `/api/v2/courses/<course_id>/quizzes` | List quizzes |
| GET | `/api/v2/courses/<course_id>/quizzes/<quiz_id>` | Get quiz |
| PUT | `/api/v2/courses/<course_id>/quizzes/<quiz_id>` | Update quiz |
| DELETE | `/api/v2/courses/<course_id>/quizzes/<quiz_id>` | Delete quiz |
| POST | `/api/v2/courses/<course_id>/quizzes/<quiz_id>/questions` | Add question |
| GET | `/api/v2/courses/<course_id>/quizzes/<quiz_id>/questions` | List questions |
| DELETE | `/api/v2/courses/<course_id>/quizzes/questions/<question_id>` | Delete question |
| PUT | `/api/v2/courses/<course_id>/quizzes/questions/<question_id>` | Update question |
| POST | `/api/v2/courses/<course_id>/quizzes/<quiz_id>/attempt` | Submit attempt |
| GET | `/api/v2/courses/<course_id>/quizzes/my/results` | My results |
| GET | `/api/v2/courses/<course_id>/quizzes/<quiz_id>/results` | Quiz results |
| GET | `/api/v2/courses/<course_id>/quizzes/<quiz_id>/results/<result_id>` | Review result |

### Admin V2 (`/api/v2/admin`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v2/admin/dashboard` | Admin dashboard stats |
| GET | `/api/v2/admin/users` | List users |
| GET | `/api/v2/admin/users/<user_id>` | Get user |
| PUT | `/api/v2/admin/users/<user_id>` | Update user |
| DELETE | `/api/v2/admin/users/<user_id>` | Delete user |
| GET | `/api/v2/admin/courses` | List courses |
| GET | `/api/v2/admin/courses/<course_id>` | Get course |
| PUT | `/api/v2/admin/courses/<course_id>` | Update course |
| DELETE | `/api/v2/admin/courses/<course_id>` | Delete course |

