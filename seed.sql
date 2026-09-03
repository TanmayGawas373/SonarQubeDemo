-- Seed script for LMS database (MySQL compatible)
-- Resolves IDs dynamically to prevent key conflict errors with existing data

-- 1. Insert Users (using INSERT IGNORE to prevent duplicate email issues)
INSERT IGNORE INTO users (full_name, email, education, password_hash, role, created_at, is_verified) VALUES
('System Admin', 'admin@example.com', 'Doctorate', 'scrypt:32768:8:1$JNqEQnuplFmZBUjh$45153cd3d792dce731f2a4e11d7e106a395c4219201a41728e4d4ffaa9b2819e54ee601245ed4427bca0ebc5d99f5a6d0b29451e24c8fa548afeeb6fccaa457e', 'admin', NOW(), 1),
('Jane Doe', 'jane.doe@example.com', 'Master of Science', 'scrypt:32768:8:1$JNqEQnuplFmZBUjh$45153cd3d792dce731f2a4e11d7e106a395c4219201a41728e4d4ffaa9b2819e54ee601245ed4427bca0ebc5d99f5a6d0b29451e24c8fa548afeeb6fccaa457e', 'instructor', NOW(), 1),
('Robert Johnson', 'robert.j@example.com', 'Ph.D. in Computer Science', 'scrypt:32768:8:1$JNqEQnuplFmZBUjh$45153cd3d792dce731f2a4e11d7e106a395c4219201a41728e4d4ffaa9b2819e54ee601245ed4427bca0ebc5d99f5a6d0b29451e24c8fa548afeeb6fccaa457e', 'instructor', NOW(), 1),
('John Smith', 'john.smith@example.com', 'Bachelor of Science', 'scrypt:32768:8:1$JNqEQnuplFmZBUjh$45153cd3d792dce731f2a4e11d7e106a395c4219201a41728e4d4ffaa9b2819e54ee601245ed4427bca0ebc5d99f5a6d0b29451e24c8fa548afeeb6fccaa457e', 'student', NOW(), 1),
('Alice Williams', 'alice.w@example.com', 'Undergraduate', 'scrypt:32768:8:1$JNqEQnuplFmZBUjh$45153cd3d792dce731f2a4e11d7e106a395c4219201a41728e4d4ffaa9b2819e54ee601245ed4427bca0ebc5d99f5a6d0b29451e24c8fa548afeeb6fccaa457e', 'student', NOW(), 1),
('Bob Miller', 'bob.m@example.com', 'High School Graduate', 'scrypt:32768:8:1$JNqEQnuplFmZBUjh$45153cd3d792dce731f2a4e11d7e106a395c4219201a41728e4d4ffaa9b2819e54ee601245ed4427bca0ebc5d99f5a6d0b29451e24c8fa548afeeb6fccaa457e', 'student', NOW(), 1),
('Charlie Davis', 'charlie.d@example.com', 'Bachelor of Arts', 'scrypt:32768:8:1$JNqEQnuplFmZBUjh$45153cd3d792dce731f2a4e11d7e106a395c4219201a41728e4d4ffaa9b2819e54ee601245ed4427bca0ebc5d99f5a6d0b29451e24c8fa548afeeb6fccaa457e', 'student', NOW(), 1),
('Diana Prince', 'diana.p@example.com', 'Associate Degree', 'scrypt:32768:8:1$JNqEQnuplFmZBUjh$45153cd3d792dce731f2a4e11d7e106a395c4219201a41728e4d4ffaa9b2819e54ee601245ed4427bca0ebc5d99f5a6d0b29451e24c8fa548afeeb6fccaa457e', 'student', NOW(), 1);

-- Get user IDs dynamically
SET @instructor_id_jane = (SELECT id FROM users WHERE email = 'jane.doe@example.com');
SET @instructor_id_robert = (SELECT id FROM users WHERE email = 'robert.j@example.com');
SET @student_id_john = (SELECT id FROM users WHERE email = 'john.smith@example.com');
SET @student_id_alice = (SELECT id FROM users WHERE email = 'alice.w@example.com');
SET @student_id_bob = (SELECT id FROM users WHERE email = 'bob.m@example.com');
SET @student_id_charlie = (SELECT id FROM users WHERE email = 'charlie.d@example.com');
SET @student_id_diana = (SELECT id FROM users WHERE email = 'diana.p@example.com');

-- 2. Insert Courses (using INSERT IGNORE to prevent duplicate title issues)
INSERT IGNORE INTO courses (title, description, instructor_id, created_at) VALUES
('Python Web Development with Flask', 'A comprehensive course covering backend web application development using Python, Flask, Jinja templates, and SQL databases.', @instructor_id_jane, NOW() - INTERVAL 10 DAY),
('Mastering Relational Databases and SQL', 'Learn table design, normalization, relations, queries, joins, indexes, and transactions in MySQL.', @instructor_id_jane, NOW() - INTERVAL 9 DAY),
('Frontend Development with React', 'Master components, state, hooks, routing, and context APIs to build premium single-page applications.', @instructor_id_robert, NOW() - INTERVAL 8 DAY),
('Data Structures and Algorithms', 'Dive deep into stacks, queues, linked lists, trees, sorting algorithms, and complexity analysis.', @instructor_id_robert, NOW() - INTERVAL 7 DAY);

-- Get course IDs dynamically
SET @course_id_flask = (SELECT id FROM courses WHERE title = 'Python Web Development with Flask');
SET @course_id_sql = (SELECT id FROM courses WHERE title = 'Mastering Relational Databases and SQL');
SET @course_id_react = (SELECT id FROM courses WHERE title = 'Frontend Development with React');
SET @course_id_dsa = (SELECT id FROM courses WHERE title = 'Data Structures and Algorithms');

-- 3. Insert Modules
INSERT IGNORE INTO modules (course_id, title, `order`, created_at) VALUES
-- Modules for Course 1 (Flask)
(@course_id_flask, 'Introduction to Flask', 1, NOW() - INTERVAL 10 DAY),
(@course_id_flask, 'Working with Databases (SQLAlchemy)', 2, NOW() - INTERVAL 9 DAY),
-- Modules for Course 2 (SQL)
(@course_id_sql, 'SQL Basics & Simple Queries', 1, NOW() - INTERVAL 9 DAY),
(@course_id_sql, 'Joins & Relations', 2, NOW() - INTERVAL 8 DAY),
-- Modules for Course 3 (React)
(@course_id_react, 'React Core Concepts', 1, NOW() - INTERVAL 8 DAY),
(@course_id_react, 'Hooks and State Management', 2, NOW() - INTERVAL 7 DAY),
-- Modules for Course 4 (DSA)
(@course_id_dsa, 'Basic Data Structures', 1, NOW() - INTERVAL 7 DAY),
(@course_id_dsa, 'Trees and Graphs', 2, NOW() - INTERVAL 6 DAY);

-- Get module IDs dynamically
SET @module_id_flask_intro = (SELECT id FROM modules WHERE course_id = @course_id_flask AND title = 'Introduction to Flask');
SET @module_id_flask_db = (SELECT id FROM modules WHERE course_id = @course_id_flask AND title = 'Working with Databases (SQLAlchemy)');
SET @module_id_sql_basics = (SELECT id FROM modules WHERE course_id = @course_id_sql AND title = 'SQL Basics & Simple Queries');
SET @module_id_sql_joins = (SELECT id FROM modules WHERE course_id = @course_id_sql AND title = 'Joins & Relations');
SET @module_id_react_core = (SELECT id FROM modules WHERE course_id = @course_id_react AND title = 'React Core Concepts');
SET @module_id_react_hooks = (SELECT id FROM modules WHERE course_id = @course_id_react AND title = 'Hooks and State Management');
SET @module_id_dsa_basics = (SELECT id FROM modules WHERE course_id = @course_id_dsa AND title = 'Basic Data Structures');
SET @module_id_dsa_trees = (SELECT id FROM modules WHERE course_id = @course_id_dsa AND title = 'Trees and Graphs');

-- 4. Insert Lessons
INSERT IGNORE INTO lessons (module_id, title, content, `order`, created_at) VALUES
-- Module 1 (Intro to Flask)
(@module_id_flask_intro, 'Flask Hello World App', 'In this lesson, you will build your first Flask application using a minimal script and learn how the routing system works.', 1, NOW() - INTERVAL 10 DAY),
(@module_id_flask_intro, 'Routing & Dynamic URLs', 'Learn how to define endpoints, handle path parameters, and use HTTP request methods.', 2, NOW() - INTERVAL 9 DAY),
-- Module 2 (SQLAlchemy)
(@module_id_flask_db, 'Setting up Flask-SQLAlchemy', 'Configure connections, define database models, and run migrations using Flask-Migrate.', 1, NOW() - INTERVAL 9 DAY),
(@module_id_flask_db, 'Relationships & Cascading Deletes', 'Implement database-level foreign key cascades and ORM session deletes.', 2, NOW() - INTERVAL 8 DAY),
-- Module 3 (SQL Basics)
(@module_id_sql_basics, 'Understanding SELECT and WHERE', 'Learn how to retrieve specific rows, filter columns, and sort results in a relational table.', 1, NOW() - INTERVAL 9 DAY),
-- Module 4 (Joins)
(@module_id_sql_joins, 'INNER, LEFT, and RIGHT Joins', 'Query multiple related tables and combine their output using JOIN operations.', 1, NOW() - INTERVAL 8 DAY),
-- Module 5 (React Core)
(@module_id_react_core, 'JSX and Virtual DOM', 'Learn why React uses JSX and how the virtual DOM works to perform efficient updates.', 1, NOW() - INTERVAL 8 DAY),
-- Module 6 (Hooks)
(@module_id_react_hooks, 'Understanding useState and useEffect', 'Learn the React component lifecycle hooks and state updates.', 1, NOW() - INTERVAL 7 DAY),
-- Module 7 (DSA Basics)
(@module_id_dsa_basics, 'Stacks & Queues Implementation', 'Implement Stacks and Queues using dynamic arrays and linked lists.', 1, NOW() - INTERVAL 7 DAY),
-- Module 8 (Trees/Graphs)
(@module_id_dsa_trees, 'Binary Trees & Traversals', 'Understand root nodes, leaf nodes, binary search trees (BST), and DFS/BFS traversals.', 1, NOW() - INTERVAL 6 DAY);

-- Get lesson IDs dynamically
SET @lesson_id_flask_hello = (SELECT id FROM lessons WHERE module_id = @module_id_flask_intro AND title = 'Flask Hello World App');
SET @lesson_id_flask_routes = (SELECT id FROM lessons WHERE module_id = @module_id_flask_intro AND title = 'Routing & Dynamic URLs');
SET @lesson_id_flask_sqla = (SELECT id FROM lessons WHERE module_id = @module_id_flask_db AND title = 'Setting up Flask-SQLAlchemy');
SET @lesson_id_flask_cascade = (SELECT id FROM lessons WHERE module_id = @module_id_flask_db AND title = 'Relationships & Cascading Deletes');
SET @lesson_id_sql_select = (SELECT id FROM lessons WHERE module_id = @module_id_sql_basics AND title = 'Understanding SELECT and WHERE');
SET @lesson_id_sql_join_types = (SELECT id FROM lessons WHERE module_id = @module_id_sql_joins AND title = 'INNER, LEFT, and RIGHT Joins');
SET @lesson_id_react_jsx = (SELECT id FROM lessons WHERE module_id = @module_id_react_core AND title = 'JSX and Virtual DOM');
SET @lesson_id_react_hooks_core = (SELECT id FROM lessons WHERE module_id = @module_id_react_hooks AND title = 'Understanding useState and useEffect');
SET @lesson_id_dsa_stacks = (SELECT id FROM lessons WHERE module_id = @module_id_dsa_basics AND title = 'Stacks & Queues Implementation');
SET @lesson_id_dsa_binary = (SELECT id FROM lessons WHERE module_id = @module_id_dsa_trees AND title = 'Binary Trees & Traversals');

-- 5. Insert Materials
INSERT IGNORE INTO materials (module_id, file_path, file_type, uploaded_by, uploaded_at) VALUES
(@module_id_flask_intro, 'flask_basics_cheatsheet.pdf', 'pdf', @instructor_id_jane, NOW() - INTERVAL 10 DAY),
(@module_id_sql_basics, 'sql_quick_reference.pdf', 'pdf', @instructor_id_jane, NOW() - INTERVAL 9 DAY),
(@module_id_react_core, 'react_architecture.png', 'image', @instructor_id_robert, NOW() - INTERVAL 8 DAY),
(@module_id_dsa_basics, 'dsa_cheatsheet.pdf', 'pdf', @instructor_id_robert, NOW() - INTERVAL 7 DAY);

-- 6. Insert Enrollments
INSERT IGNORE INTO enrollments (user_id, course_id, enrolled_at) VALUES
-- Student John Smith
(@student_id_john, @course_id_flask, NOW() - INTERVAL 5 DAY),
(@student_id_john, @course_id_sql, NOW() - INTERVAL 4 DAY),
(@student_id_john, @course_id_react, NOW() - INTERVAL 3 DAY),
-- Student Alice Williams
(@student_id_alice, @course_id_flask, NOW() - INTERVAL 4 DAY),
(@student_id_alice, @course_id_sql, NOW() - INTERVAL 4 DAY),
(@student_id_alice, @course_id_dsa, NOW() - INTERVAL 2 DAY),
-- Student Bob Miller
(@student_id_bob, @course_id_flask, NOW() - INTERVAL 3 DAY),
(@student_id_bob, @course_id_react, NOW() - INTERVAL 3 DAY),
-- Student Charlie Davis
(@student_id_charlie, @course_id_sql, NOW() - INTERVAL 2 DAY),
(@student_id_charlie, @course_id_dsa, NOW() - INTERVAL 2 DAY),
-- Student Diana Prince
(@student_id_diana, @course_id_flask, NOW() - INTERVAL 1 DAY),
(@student_id_diana, @course_id_dsa, NOW() - INTERVAL 1 DAY);

-- 7. Insert Lesson Completions
INSERT IGNORE INTO lesson_completions (student_id, lesson_id, completed_at) VALUES
-- Student John Smith
(@student_id_john, @lesson_id_flask_hello, NOW() - INTERVAL 4 DAY),
(@student_id_john, @lesson_id_flask_routes, NOW() - INTERVAL 4 DAY),
(@student_id_john, @lesson_id_flask_sqla, NOW() - INTERVAL 3 DAY),
-- Student Alice Williams
(@student_id_alice, @lesson_id_flask_hello, NOW() - INTERVAL 3 DAY),
(@student_id_alice, @lesson_id_sql_select, NOW() - INTERVAL 3 DAY),
-- Student Bob Miller
(@student_id_bob, @lesson_id_flask_hello, NOW() - INTERVAL 2 DAY),
(@student_id_bob, @lesson_id_react_jsx, NOW() - INTERVAL 2 DAY);

-- 8. Insert Course Progress (using ON DUPLICATE KEY UPDATE to handle existing user_id/course_id uniquely if applicable)
INSERT INTO progress (student_id, course_id, completion_percent, updated_at) VALUES
(@student_id_john, @course_id_flask, 75.0, NOW()),
(@student_id_john, @course_id_sql, 0.0, NOW()),
(@student_id_john, @course_id_react, 0.0, NOW()),
(@student_id_alice, @course_id_flask, 25.0, NOW()),
(@student_id_alice, @course_id_sql, 50.0, NOW()),
(@student_id_alice, @course_id_dsa, 0.0, NOW()),
(@student_id_bob, @course_id_flask, 25.0, NOW()),
(@student_id_bob, @course_id_react, 0.0, NOW()),
(@student_id_charlie, @course_id_sql, 0.0, NOW()),
(@student_id_charlie, @course_id_dsa, 0.0, NOW()),
(@student_id_diana, @course_id_flask, 0.0, NOW()),
(@student_id_diana, @course_id_dsa, 0.0, NOW())
ON DUPLICATE KEY UPDATE completion_percent = VALUES(completion_percent), updated_at = NOW();

-- 9. Insert Quizzes
INSERT IGNORE INTO quizzes (title, course_id, instructor_id, created_at) VALUES
('Flask Routing & Basics Quiz', @course_id_flask, @instructor_id_jane, NOW() - INTERVAL 10 DAY),
('SQL Joins & Queries Quiz', @course_id_sql, @instructor_id_jane, NOW() - INTERVAL 9 DAY),
('React Concepts & Hooks Quiz', @course_id_react, @instructor_id_robert, NOW() - INTERVAL 8 DAY),
('DSA Stacks and Trees Quiz', @course_id_dsa, @instructor_id_robert, NOW() - INTERVAL 7 DAY);

-- Get quiz IDs dynamically
SET @quiz_id_flask = (SELECT id FROM quizzes WHERE course_id = @course_id_flask AND title = 'Flask Routing & Basics Quiz');
SET @quiz_id_sql = (SELECT id FROM quizzes WHERE course_id = @course_id_sql AND title = 'SQL Joins & Queries Quiz');
SET @quiz_id_react = (SELECT id FROM quizzes WHERE course_id = @course_id_react AND title = 'React Concepts & Hooks Quiz');
SET @quiz_id_dsa = (SELECT id FROM quizzes WHERE course_id = @course_id_dsa AND title = 'DSA Stacks and Trees Quiz');

-- 10. Insert Questions
INSERT IGNORE INTO questions (quiz_id, prompt, options_json) VALUES
-- Quiz 1 Questions (Flask)
(@quiz_id_flask, 'Which decorator is used to bind a function to a URL endpoint in Flask?', '[{"option": "@app.route()", "is_correct": true}, {"option": "@app.endpoint()", "is_correct": false}, {"option": "@app.link()", "is_correct": false}]'),
(@quiz_id_flask, 'By default, flask run starts the server on which port?', '[{"option": "8080", "is_correct": false}, {"option": "5000", "is_correct": true}, {"option": "3000", "is_correct": false}]'),
-- Quiz 2 Questions (SQL)
(@quiz_id_sql, 'Which SQL clause is used to filter query results based on aggregate functions?', '[{"option": "WHERE", "is_correct": false}, {"option": "HAVING", "is_correct": true}, {"option": "GROUP BY", "is_correct": false}]'),
(@quiz_id_sql, 'Which JOIN returns all records when there is a match in either left or right table?', '[{"option": "LEFT JOIN", "is_correct": false}, {"option": "FULL OUTER JOIN", "is_correct": true}, {"option": "INNER JOIN", "is_correct": false}]'),
-- Quiz 3 Questions (React)
(@quiz_id_react, 'What is the purpose of key prop in React lists?', '[{"option": "To uniquely identify element changes, additions, or removals", "is_correct": true}, {"option": "To bind CSS styles", "is_correct": false}]'),
-- Quiz 4 Questions (DSA)
(@quiz_id_dsa, 'What is the time complexity of searching a value in a balanced Binary Search Tree?', '[{"option": "O(N)", "is_correct": false}, {"option": "O(log N)", "is_correct": true}, {"option": "O(1)", "is_correct": false}]');

-- 11. Insert Quiz Results (Student Attempts)
INSERT IGNORE INTO quiz_results (quiz_id, student_id, score, submitted_at, answers_json) VALUES
-- Student John Smith
(@quiz_id_flask, @student_id_john, 100.0, NOW() - INTERVAL 3 DAY, '{"1": 0, "2": 1}'),
(@quiz_id_sql, @student_id_john, 50.0, NOW() - INTERVAL 2 DAY, '{"3": 1, "4": 0}'),
-- Student Alice Williams
(@quiz_id_flask, @student_id_alice, 50.0, NOW() - INTERVAL 2 DAY, '{"1": 1, "2": 1}'),
(@quiz_id_sql, @student_id_alice, 100.0, NOW() - INTERVAL 1 DAY, '{"3": 1, "4": 1}'),
-- Student Bob Miller
(@quiz_id_flask, @student_id_bob, 100.0, NOW() - INTERVAL 1 DAY, '{"1": 0, "2": 1}'),
(@quiz_id_react, @student_id_bob, 100.0, NOW() - INTERVAL 1 DAY, '{"5": 0}');
