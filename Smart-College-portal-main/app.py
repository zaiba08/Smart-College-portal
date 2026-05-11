import csv
import os
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db = SQLAlchemy(app)

# Database Models
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.Integer, nullable=False)

class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    percentage = db.Column(db.Integer, nullable=False)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    marks = db.Column(db.Integer, nullable=False)

class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(20), nullable=False)

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.String(20), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(200), nullable=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        if role == 'admin':
            admin = Admin.query.filter_by(email=email, password=password).first()
            if admin:
                session['user'] = admin.id
                session['role'] = 'admin'
                return redirect(url_for('dashboard'))
        elif role == 'student':
            student = Student.query.filter_by(email=email, password=password).first()
            if student:
                session['user'] = student.id
                session['role'] = 'student'
                return redirect(url_for('dashboard'))
        elif role == 'faculty':
            faculty = Faculty.query.filter_by(email=email, password=password).first()
            if faculty:
                session['user'] = faculty.id
                session['role'] = 'faculty'
                return redirect(url_for('dashboard'))
        
        return 'Invalid credentials'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'role' not in session:
        return redirect(url_for('login'))
    role = session['role']
    if role == 'admin':
        student_count = Student.query.count()
        faculty_count = Faculty.query.count()
        notice_count = Notice.query.count()
        assignment_count = Assignment.query.count()
        return render_template('admin_dashboard.html', student_count=student_count, faculty_count=faculty_count, notice_count=notice_count, assignment_count=assignment_count)
    elif role == 'student':
        user_id = session['user']
        attendance = Attendance.query.filter_by(student_id=user_id).all()
        results = Result.query.filter_by(student_id=user_id).all()
        assignments = Assignment.query.all()
        avg_attendance = round(sum([a.percentage for a in attendance]) / len(attendance), 2) if attendance else 0
        avg_marks = round(sum([r.marks for r in results]) / len(results), 2) if results else 0
        pass_count = sum(1 for r in results if r.marks >= 50)
        fail_count = sum(1 for r in results if r.marks < 50)
        gpa = round((avg_marks / 20), 2) if results else 0
        return render_template('student_dashboard.html', attendance_count=len(attendance), result_count=len(results), assignment_count=len(assignments), avg_attendance=avg_attendance, avg_marks=avg_marks, gpa=gpa, pass_count=pass_count, fail_count=fail_count)
    elif role == 'faculty':
        faculty_id = session['user']
        assignments = Assignment.query.filter_by(faculty_id=faculty_id).count()
        total_students = Student.query.count()
        avg_attendance = round(db.session.query(db.func.avg(Attendance.percentage)).scalar() or 0, 2)
        avg_marks = round(db.session.query(db.func.avg(Result.marks)).scalar() or 0, 2)
        return render_template('faculty_dashboard.html', assignment_count=assignments, total_students=total_students, avg_attendance=avg_attendance, avg_marks=avg_marks)
    return redirect(url_for('login'))
# Admin routes
@app.route('/admin/students')
def admin_students():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    query = request.args.get('q', '').strip()
    if query:
        students = Student.query.filter(
            db.or_(
                Student.name.ilike(f'%{query}%'),
                Student.email.ilike(f'%{query}%'),
                Student.department.ilike(f'%{query}%')
            )
        ).all()
    else:
        students = Student.query.all()
    return render_template('admin_students.html', students=students, query=query)

@app.route('/admin/add_student', methods=['GET', 'POST'])
def add_student():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        department = request.form['department']
        semester = int(request.form['semester'])
        student = Student(name=name, email=email, password=password, department=department, semester=semester)
        db.session.add(student)
        db.session.commit()
        return redirect(url_for('admin_students'))
    return render_template('add_student.html')

@app.route('/admin/delete_student/<int:id>')
def delete_student(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    student = Student.query.get(id)
    if student:
        db.session.delete(student)
        db.session.commit()
    return redirect(url_for('admin_students'))

@app.route('/admin/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    student = Student.query.get(id)
    if not student:
        return redirect(url_for('admin_students'))
    if request.method == 'POST':
        student.name = request.form['name']
        student.email = request.form['email']
        student.password = request.form['password']
        student.department = request.form['department']
        student.semester = int(request.form['semester'])
        db.session.commit()
        return redirect(url_for('admin_students'))
    return render_template('edit_student.html', student=student)

# Similar for faculty
@app.route('/admin/faculty')
def admin_faculty():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    query = request.args.get('q', '').strip()
    if query:
        faculty = Faculty.query.filter(
            db.or_(
                Faculty.name.ilike(f'%{query}%'),
                Faculty.email.ilike(f'%{query}%'),
                Faculty.subject.ilike(f'%{query}%')
            )
        ).all()
    else:
        faculty = Faculty.query.all()
    return render_template('admin_faculty.html', faculty=faculty, query=query)

@app.route('/admin/add_faculty', methods=['GET', 'POST'])
def add_faculty():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        subject = request.form['subject']
        fac = Faculty(name=name, email=email, password=password, subject=subject)
        db.session.add(fac)
        db.session.commit()
        return redirect(url_for('admin_faculty'))
    return render_template('add_faculty.html')

@app.route('/admin/edit_faculty/<int:id>', methods=['GET', 'POST'])
def edit_faculty(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    faculty = Faculty.query.get(id)
    if not faculty:
        return redirect(url_for('admin_faculty'))
    if request.method == 'POST':
        faculty.name = request.form['name']
        faculty.email = request.form['email']
        faculty.password = request.form['password']
        faculty.subject = request.form['subject']
        db.session.commit()
        return redirect(url_for('admin_faculty'))
    return render_template('edit_faculty.html', faculty=faculty)

@app.route('/admin/delete_faculty/<int:id>')
def delete_faculty(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    faculty = Faculty.query.get(id)
    if faculty:
        db.session.delete(faculty)
        db.session.commit()
    return redirect(url_for('admin_faculty'))

# Notices
@app.route('/admin/notices')
def admin_notices():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    query = request.args.get('q', '').strip()
    if query:
        notices = Notice.query.filter(
            db.or_(
                Notice.title.ilike(f'%{query}%'),
                Notice.description.ilike(f'%{query}%'),
                Notice.date.ilike(f'%{query}%')
            )
        ).all()
    else:
        notices = Notice.query.all()
    alert_sent = request.args.get('alert_sent')
    return render_template('admin_notices.html', notices=notices, query=query, alert_sent=alert_sent)

@app.route('/admin/send_notice_alert/<int:id>')
def send_notice_alert(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    notice = Notice.query.get(id)
    if notice:
        print(f"[NOTICE ALERT] Sending notice '{notice.title}' to all users")
    return redirect(url_for('admin_notices', alert_sent=1))

@app.route('/profile')
def profile():
    if 'role' not in session:
        return redirect(url_for('login'))
    role = session['role']
    if role == 'student':
        user = Student.query.get(session['user'])
    elif role == 'faculty':
        user = Faculty.query.get(session['user'])
    else:
        return redirect(url_for('dashboard'))
    return render_template('profile.html', user=user, role=role)

@app.route('/admin/add_notice', methods=['GET', 'POST'])
def add_notice():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date = request.form['date']
        notice = Notice(title=title, description=description, date=date)
        db.session.add(notice)
        db.session.commit()
        return redirect(url_for('admin_notices'))
    return render_template('add_notice.html')

@app.route('/admin/edit_notice/<int:id>', methods=['GET', 'POST'])
def edit_notice(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    notice = Notice.query.get(id)
    if not notice:
        return redirect(url_for('admin_notices'))
    if request.method == 'POST':
        notice.title = request.form['title']
        notice.description = request.form['description']
        notice.date = request.form['date']
        db.session.commit()
        return redirect(url_for('admin_notices'))
    return render_template('edit_notice.html', notice=notice)

@app.route('/admin/view_notice/<int:id>')
def admin_view_notice(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    notice = Notice.query.get(id)
    if not notice:
        return redirect(url_for('admin_notices'))
    return render_template('view_notice.html', notice=notice, admin=True)

@app.route('/notice/<int:id>')
def view_notice(id):
    notice = Notice.query.get(id)
    if not notice:
        return redirect(url_for('notices'))
    return render_template('view_notice.html', notice=notice, admin=False)

@app.route('/admin/delete_notice/<int:id>')
def delete_notice(id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    notice = Notice.query.get(id)
    if notice:
        db.session.delete(notice)
        db.session.commit()
    return redirect(url_for('admin_notices'))

# Public notices
@app.route('/notices')
def notices():
    notices = Notice.query.all()
    return render_template('notices.html', notices=notices)

# Student routes
@app.route('/student/attendance')
def student_attendance():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    user_id = session['user']
    attendance = Attendance.query.filter_by(student_id=user_id).all()
    return render_template('attendance.html', attendance=attendance)

@app.route('/student/results')
def student_results():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    user_id = session['user']
    results = Result.query.filter_by(student_id=user_id).all()
    return render_template('results.html', results=results)

@app.route('/student/assignments')
def student_assignments():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    query = request.args.get('q', '').strip()
    if query:
        assignments = Assignment.query.filter(
            db.or_(
                Assignment.title.ilike(f'%{query}%'),
                Assignment.description.ilike(f'%{query}%'),
                Assignment.subject.ilike(f'%{query}%')
            )
        ).all()
    else:
        assignments = Assignment.query.all()
    return render_template('assignments.html', assignments=assignments, query=query)

@app.route('/assignments/download/<int:id>')
def download_assignment(id):
    assignment = Assignment.query.get(id)
    if assignment and assignment.filename:
        return send_from_directory(app.config['UPLOAD_FOLDER'], assignment.filename, as_attachment=True)
    return redirect(url_for('student_assignments'))

# Faculty routes
@app.route('/faculty/attendance', methods=['GET', 'POST'])
def faculty_attendance():
    if session.get('role') != 'faculty':
        return redirect(url_for('login'))
    if request.method == 'POST':
        subject = request.form['subject']
        student_ids = request.form.getlist('student_ids')
        csv_file = request.files.get('attendance_csv')
        if csv_file and csv_file.filename:
            csv_reader = csv.DictReader(csv_file.stream.read().decode('utf-8').splitlines())
            for row in csv_reader:
                try:
                    student_id = int(row.get('student_id', '').strip())
                    percentage = int(row.get('percentage', '').strip())
                    if student_id and 0 <= percentage <= 100:
                        att = Attendance(student_id=student_id, subject=row.get('subject', subject).strip() or subject, percentage=percentage)
                        db.session.add(att)
                except ValueError:
                    continue
        else:
            for student_id in student_ids:
                percentage = request.form.get(f'percentage_{student_id}')
                if percentage:
                    att = Attendance(student_id=int(student_id), subject=subject, percentage=int(percentage))
                    db.session.add(att)
        db.session.commit()
        return redirect(url_for('faculty_attendance'))
    students = Student.query.all()
    return render_template('faculty_attendance.html', students=students)

@app.route('/faculty/results', methods=['GET', 'POST'])
def faculty_results():
    if session.get('role') != 'faculty':
        return redirect(url_for('login'))
    if request.method == 'POST':
        student_id = int(request.form['student_id'])
        subject = request.form['subject']
        marks = int(request.form['marks'])
        res = Result(student_id=student_id, subject=subject, marks=marks)
        db.session.add(res)
        db.session.commit()
        return redirect(url_for('faculty_results'))
    students = Student.query.all()
    return render_template('faculty_results.html', students=students)

@app.route('/faculty/assignments', methods=['GET', 'POST'])
def faculty_assignments():
    if session.get('role') != 'faculty':
        return redirect(url_for('login'))
    faculty_id = session['user']
    query = request.args.get('q', '').strip()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        due_date = request.form['due_date']
        subject = request.form['subject']
        filename = None
        file = request.files.get('assignment_file')
        if file and file.filename:
            filename = f"{faculty_id}_{file.filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
        assignment = Assignment(title=title, description=description, due_date=due_date, faculty_id=faculty_id, subject=subject, filename=filename)
        db.session.add(assignment)
        db.session.commit()
        return redirect(url_for('faculty_assignments'))
    if query:
        assignments = Assignment.query.filter(Assignment.faculty_id == faculty_id).filter(
            db.or_(
                Assignment.title.ilike(f'%{query}%'),
                Assignment.description.ilike(f'%{query}%'),
                Assignment.subject.ilike(f'%{query}%')
            )
        ).all()
    else:
        assignments = Assignment.query.filter_by(faculty_id=faculty_id).all()
    return render_template('faculty_assignments.html', assignments=assignments, query=query)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Sample data
        if not Student.query.first():
            student1 = Student(name='John Doe', email='john@example.com', password='password', department='Computer Science', semester=5)
            student2 = Student(name='Jane Smith', email='jane@example.com', password='password', department='Information Technology', semester=4)
            db.session.add(student1)
            db.session.add(student2)
            db.session.commit()
        
        if not Faculty.query.first():
            faculty1 = Faculty(name='Dr. Alice Johnson', email='alice@example.com', password='password', subject='Data Structures')
            db.session.add(faculty1)
            db.session.commit()
        
        if not Attendance.query.first():
            att1 = Attendance(student_id=1, subject='Data Structures', percentage=85)
            db.session.add(att1)
            db.session.commit()
        
        if not Result.query.first():
            res1 = Result(student_id=1, subject='Data Structures', marks=85)
            db.session.add(res1)
            db.session.commit()
        
        if not Notice.query.first():
            notice1 = Notice(title='Exam Schedule', description='Mid-term exams start next week.', date='2023-10-01')
            db.session.add(notice1)
            db.session.commit()
        
        if not Assignment.query.first():
            assignment1 = Assignment(title='Data Structures Assignment 1', description='Implement a linked list.', due_date='2023-10-15', faculty_id=1, subject='Data Structures')
            db.session.add(assignment1)
            db.session.commit()
    
    app.run(debug=True)