from flask import Flask
from models import db, Teacher, Grade, Stream, Subject, Term, AssessmentType

# Create a Flask app instance for database initialization
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///E:/DKANTE/hillview_mvp/hillview.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create the database and tables
with app.app_context():
    print("Starting database creation...")
    db.create_all()
    print("Database creation completed!")

    # Add sample data if the database is empty
    if not Grade.query.first():
        print("Adding sample data...")
        # Sample Grades
        grade1 = Grade(level="Grade 1")
        grade2 = Grade(level="Grade 2")
        db.session.add_all([grade1, grade2])

        # Sample Streams
        stream1 = Stream(name="A", grade=grade1)
        stream2 = Stream(name="B", grade=grade1)
        stream3 = Stream(name="A", grade=grade2)
        db.session.add_all([stream1, stream2, stream3])

        # Sample Subjects
        subject1 = Subject(name="Mathematics", education_level="Lower Primary")
        subject2 = Subject(name="English", education_level="Lower Primary")
        subject3 = Subject(name="Kiswahili", education_level="Lower Primary")
        subject4 = Subject(name="Integrated Science and Health Education", education_level="Lower Primary")
        subject5 = Subject(name="Agriculture", education_level="Lower Primary")
        subject6 = Subject(name="Pre-Technical Studies", education_level="Lower Primary")
        subject7 = Subject(name="Visual Arts", education_level="Lower Primary")
        subject8 = Subject(name="Religious Education", education_level="Lower Primary")
        subject9 = Subject(name="Social Studies", education_level="Lower Primary")
        db.session.add_all([subject1, subject2, subject3, subject4, subject5, subject6, subject7, subject8, subject9])

        # Sample Terms
        term1 = Term(name="Term 1")
        term2 = Term(name="Term 2")
        db.session.add_all([term1, term2])

        # Sample Assessment Types
        assessment1 = AssessmentType(name="Exam")
        assessment2 = AssessmentType(name="Quiz")
        db.session.add_all([assessment1, assessment2])

        # Add a default Class Teacher for login
        classteacher = Teacher.query.filter_by(role="classteacher").first()
        if not classteacher:
            new_teacher = Teacher(username="admin", password="admin123", role="classteacher")
            db.session.add(new_teacher)
            print("Class Teacher 'admin' created successfully! Username: admin, Password: admin123")

        # Add a default Head Teacher for login
        headteacher = Teacher.query.filter_by(role="headteacher").first()
        if not headteacher:
            new_headteacher = Teacher(username="headteacher", password="head123", role="headteacher")
            db.session.add(new_headteacher)
            print("Head Teacher 'headteacher' created successfully! Username: headteacher, Password: head123")

        # Add a default Teacher for login
        teacher = Teacher.query.filter_by(role="teacher").first()
        if not teacher:
            new_teacher = Teacher(username="teacher", password="teach123", role="teacher")
            db.session.add(new_teacher)
            print("Teacher 'teacher' created successfully! Username: teacher, Password: teach123")

        db.session.commit()
        print("Sample data and users added successfully!")
    else:
        print("Database already contains data. Skipping sample data insertion.")

print("Database initialization completed. You can now run 'python app.py' to start the server.")