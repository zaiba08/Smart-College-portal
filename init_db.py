from app import app, db

with app.app_context():
    db.create_all()
    print('Database tables created')
    
    # Add sample data
    from app import Student, Faculty, Admin, Attendance, Result, Notice, Assignment
    
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
    
    if not Admin.query.first():
        admin = Admin(email='admin@example.com', password='admin')
        db.session.add(admin)
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
    
    print('Sample data added')