# Smart College Portal SQL Queries

This file contains SQL statements for the main tables used in the Smart College Portal application. It includes table creation, sample inserts, and CRUD operations for each entity.

---

## 1. Create Tables

```sql
CREATE TABLE student (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    semester INTEGER NOT NULL
);

CREATE TABLE faculty (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    subject VARCHAR(100) NOT NULL
);

CREATE TABLE admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject VARCHAR(100) NOT NULL,
    percentage INTEGER NOT NULL,
    FOREIGN KEY(student_id) REFERENCES student(id)
);

CREATE TABLE result (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    subject VARCHAR(100) NOT NULL,
    marks INTEGER NOT NULL,
    FOREIGN KEY(student_id) REFERENCES student(id)
);

CREATE TABLE notice (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    date VARCHAR(20) NOT NULL
);

CREATE TABLE assignment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    due_date VARCHAR(20) NOT NULL,
    faculty_id INTEGER NOT NULL,
    subject VARCHAR(100) NOT NULL,
    filename VARCHAR(200),
    FOREIGN KEY(faculty_id) REFERENCES faculty(id)
);
```

---

## 2. Sample Insert Statements

```sql
INSERT INTO admin (email, password) VALUES ('admin@example.com', 'admin');

INSERT INTO student (name, email, password, department, semester)
VALUES
('John Doe', 'john@example.com', 'password', 'Computer Science', 5),
('Jane Smith', 'jane@example.com', 'password', 'Information Technology', 4);

INSERT INTO faculty (name, email, password, subject)
VALUES ('Dr. Alice Johnson', 'alice@example.com', 'password', 'Data Structures');

INSERT INTO attendance (student_id, subject, percentage)
VALUES (1, 'Data Structures', 85);

INSERT INTO result (student_id, subject, marks)
VALUES (1, 'Data Structures', 85);

INSERT INTO notice (title, description, date)
VALUES ('Exam Schedule', 'Mid-term exams start next week.', '2023-10-01');

INSERT INTO assignment (title, description, due_date, faculty_id, subject, filename)
VALUES ('Data Structures Assignment 1', 'Implement a linked list.', '2023-10-15', 1, 'Data Structures', NULL);
```

---

## 3. Student CRUD Queries

### Create student
```sql
INSERT INTO student (name, email, password, department, semester)
VALUES (:name, :email, :password, :department, :semester);
```

### Read all students
```sql
SELECT * FROM student;
```

### Read student by ID
```sql
SELECT * FROM student WHERE id = :id;
```

### Search students
```sql
SELECT * FROM student
WHERE name LIKE '%' || :query || '%'
   OR email LIKE '%' || :query || '%'
   OR department LIKE '%' || :query || '%';
```

### Update student
```sql
UPDATE student
SET name = :name,
    email = :email,
    password = :password,
    department = :department,
    semester = :semester
WHERE id = :id;
```

### Delete student
```sql
DELETE FROM student WHERE id = :id;
```

---

## 4. Faculty CRUD Queries

### Create faculty
```sql
INSERT INTO faculty (name, email, password, subject)
VALUES (:name, :email, :password, :subject);
```

### Read all faculty
```sql
SELECT * FROM faculty;
```

### Read faculty by ID
```sql
SELECT * FROM faculty WHERE id = :id;
```

### Search faculty
```sql
SELECT * FROM faculty
WHERE name LIKE '%' || :query || '%'
   OR email LIKE '%' || :query || '%'
   OR subject LIKE '%' || :query || '%';
```

### Update faculty
```sql
UPDATE faculty
SET name = :name,
    email = :email,
    password = :password,
    subject = :subject
WHERE id = :id;
```

### Delete faculty
```sql
DELETE FROM faculty WHERE id = :id;
```

---

## 5. Admin Queries

### Create admin
```sql
INSERT INTO admin (email, password)
VALUES (:email, :password);
```

### Read admin by email/password
```sql
SELECT * FROM admin
WHERE email = :email
  AND password = :password;
```

### Read all admins
```sql
SELECT * FROM admin;
```

### Delete admin
```sql
DELETE FROM admin WHERE id = :id;
```

---

## 6. Attendance CRUD Queries

### Create attendance record
```sql
INSERT INTO attendance (student_id, subject, percentage)
VALUES (:student_id, :subject, :percentage);
```

### Read attendance for one student
```sql
SELECT * FROM attendance WHERE student_id = :student_id;
```

### Read all attendance records
```sql
SELECT * FROM attendance;
```

### Read attendance for a specific subject
```sql
SELECT * FROM attendance WHERE subject = :subject;
```

### Update attendance record
```sql
UPDATE attendance
SET subject = :subject,
    percentage = :percentage
WHERE id = :id;
```

### Delete attendance record
```sql
DELETE FROM attendance WHERE id = :id;
```

### Aggregate attendance
```sql
SELECT AVG(percentage) AS avg_percentage
FROM attendance
WHERE student_id = :student_id;
```

---

## 7. Result CRUD Queries

### Create result record
```sql
INSERT INTO result (student_id, subject, marks)
VALUES (:student_id, :subject, :marks);
```

### Read results for one student
```sql
SELECT * FROM result WHERE student_id = :student_id;
```

### Read all results
```sql
SELECT * FROM result;
```

### Update result record
```sql
UPDATE result
SET subject = :subject,
    marks = :marks
WHERE id = :id;
```

### Delete result record
```sql
DELETE FROM result WHERE id = :id;
```

### Result summary
```sql
SELECT COUNT(*) AS count,
       AVG(marks) AS average_marks,
       SUM(CASE WHEN marks >= 50 THEN 1 ELSE 0 END) AS pass_count,
       SUM(CASE WHEN marks < 50 THEN 1 ELSE 0 END) AS fail_count
FROM result
WHERE student_id = :student_id;
```

---

## 8. Notice CRUD Queries

### Create notice
```sql
INSERT INTO notice (title, description, date)
VALUES (:title, :description, :date);
```

### Read all notices
```sql
SELECT * FROM notice ORDER BY date DESC;
```

### Read notice by ID
```sql
SELECT * FROM notice WHERE id = :id;
```

### Update notice
```sql
UPDATE notice
SET title = :title,
    description = :description,
    date = :date
WHERE id = :id;
```

### Delete notice
```sql
DELETE FROM notice WHERE id = :id;
```
```

---

## 9. Assignment CRUD Queries

### Create assignment
```sql
INSERT INTO assignment (title, description, due_date, faculty_id, subject, filename)
VALUES (:title, :description, :due_date, :faculty_id, :subject, :filename);
```

### Read all assignments
```sql
SELECT * FROM assignment;
```

### Read assignment by ID
```sql
SELECT * FROM assignment WHERE id = :id;
```

### Read assignments by faculty
```sql
SELECT * FROM assignment WHERE faculty_id = :faculty_id;
```

### Update assignment
```sql
UPDATE assignment
SET title = :title,
    description = :description,
    due_date = :due_date,
    faculty_id = :faculty_id,
    subject = :subject,
    filename = :filename
WHERE id = :id;
```

### Delete assignment
```sql
DELETE FROM assignment WHERE id = :id;
```

---

## 10. Dashboard and Summary Queries

### Count students
```sql
SELECT COUNT(*) AS student_count FROM student;
```

### Count faculty
```sql
SELECT COUNT(*) AS faculty_count FROM faculty;
```

### Count assignments
```sql
SELECT COUNT(*) AS assignment_count FROM assignment;
```

### Count notices
```sql
SELECT COUNT(*) AS notice_count FROM notice;
```

### Average attendance across students
```sql
SELECT AVG(percentage) AS avg_attendance FROM attendance;
```

### Average marks across results
```sql
SELECT AVG(marks) AS avg_marks FROM result;
```

---

## Notes
- Replace `:param` values with actual values or parameter names depending on the SQL library you use.
- Use parameterized queries to prevent SQL injection.
- In SQLite, `AUTOINCREMENT` is optional when using `INTEGER PRIMARY KEY`.
