from flask import Flask
from models import db, Teacher, Grade, Stream, Subject, Term, AssessmentType, Student

# Create a Flask app instance for database initialization
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///E:/DKANTE/hillview_mvp/kirima_primary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create the database and tables
with app.app_context():
    print("Starting database creation...")
    db.drop_all()  # Drop existing tables to ensure a fresh database
    db.create_all()  # Create new tables based on models.py
    print("Database creation completed!")

    # Add data for Grade 9 with Streams B, G, and Y, and the 102 students
    print("Adding Grade 9 with Streams B, G, Y and student data...")

    # Add Grade 9
    grade9 = Grade(level="Grade 9")
    db.session.add(grade9)

    # Add Streams B, G, and Y for Grade 9
    stream_b = Stream(name="B", grade=grade9)
    stream_g = Stream(name="G", grade=grade9)
    stream_y = Stream(name="Y", grade=grade9)
    db.session.add_all([stream_b, stream_g, stream_y])

    # Add Subjects (same as before)
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

    # Add Terms
    term1 = Term(name="Term 1")
    term2 = Term(name="Term 2")
    db.session.add_all([term1, term2])

    # Add Assessment Types
    assessment1 = AssessmentType(name="Exam")
    assessment2 = AssessmentType(name="Quiz")
    db.session.add_all([assessment1, assessment2])

    # Add the 32 students from Grade 9 Stream B with gender (19 boys, 13 girls)
    students_stream_b = [
        {"name": "ABIGAEL GAKENIA RWAMBA", "admission_number": "HS9B001", "gender": "Female"},
        {"name": "ALLAN CHEGE NJOROGE", "admission_number": "HS9B002", "gender": "Male"},
        {"name": "BRIAN KIPKEMOI", "admission_number": "HS9B003", "gender": "Male"},
        {"name": "CATHYLINE WANJIKU KIMANI", "admission_number": "HS9B004", "gender": "Female"},
        {"name": "COLLINS KIPCHIRCHIR", "admission_number": "HS9B005", "gender": "Male"},
        {"name": "CYNTHIA MUTHONI MWANGI", "admission_number": "HS9B006", "gender": "Female"},
        {"name": "DANIEL WANYOIKE KIMANI", "admission_number": "HS9B007", "gender": "Male"},
        {"name": "DERRICK KIPKORIR", "admission_number": "HS9B008", "gender": "Male"},
        {"name": "EDWIN KIPKORIR", "admission_number": "HS9B009", "gender": "Male"},
        {"name": "ELIJAH MWANGI NJOROGE", "admission_number": "HS9B010", "gender": "Male"},
        {"name": "EMMANUEL KIPKORIR", "admission_number": "HS9B011", "gender": "Male"},
        {"name": "EVANS KIPKORIR", "admission_number": "HS9B012", "gender": "Male"},
        {"name": "FAITH NJERI MWANGI", "admission_number": "HS9B013", "gender": "Female"},
        {"name": "FRANCIS KIMANI MWANGI", "admission_number": "HS9B014", "gender": "Male"},
        {"name": "GEORGE KIMANI MWANGI", "admission_number": "HS9B015", "gender": "Male"},
        {"name": "GLADYS WANJIKU KIMANI", "admission_number": "HS9B016", "gender": "Female"},
        {"name": "GRACE NJERI MWANGI", "admission_number": "HS9B017", "gender": "Female"},
        {"name": "IAN KIPKORIR", "admission_number": "HS9B018", "gender": "Male"},
        {"name": "ISAAC KIPKORIR", "admission_number": "HS9B019", "gender": "Male"},
        {"name": "JAMES KIMANI MWANGI", "admission_number": "HS9B020", "gender": "Male"},
        {"name": "JANE WANJIKU KIMANI", "admission_number": "HS9B021", "gender": "Female"},
        {"name": "JOHN KIPKORIR", "admission_number": "HS9B022", "gender": "Male"},
        {"name": "JOSEPH KIMANI MWANGI", "admission_number": "HS9B023", "gender": "Male"},
        {"name": "JOYCE NJERI MWANGI", "admission_number": "HS9B024", "gender": "Female"},
        {"name": "JUDITH WANJIKU KIMANI", "admission_number": "HS9B025", "gender": "Female"},
        {"name": "KEVIN KIPKORIR", "admission_number": "HS9B026", "gender": "Male"},
        {"name": "LILIAN NJERI MWANGI", "admission_number": "HS9B027", "gender": "Female"},
        {"name": "MARY WANJIKU KIMANI", "admission_number": "HS9B028", "gender": "Female"},
        {"name": "MERCY NJERI MWANGI", "admission_number": "HS9B029", "gender": "Female"},
        {"name": "PETER KIMANI MWANGI", "admission_number": "HS9B030", "gender": "Male"},
        {"name": "SAMUEL KIPKORIR", "admission_number": "HS9B031", "gender": "Male"},
        {"name": "SARAH WANJIKU KIMANI", "admission_number": "HS9B032", "gender": "Female"},
    ]

    for student_data in students_stream_b:
        student = Student(
            name=student_data["name"],
            admission_number=student_data["admission_number"],
            stream=stream_b,
            gender=student_data["gender"].lower()  # Store as lowercase for consistency
        )
        db.session.add(student)

    # Add 35 students to Grade 9 Stream G (21 boys, 14 girls)
    students_stream_g = [
        {"name": "ALICE NJERI MWANGI", "admission_number": "HS9G001", "gender": "Female"},
        {"name": "BENJAMIN KIPKORIR", "admission_number": "HS9G002", "gender": "Male"},
        {"name": "CHARLES KIMANI MWANGI", "admission_number": "HS9G003", "gender": "Male"},
        {"name": "DIANA WANJIKU KIMANI", "admission_number": "HS9G004", "gender": "Female"},
        {"name": "EDWARD KIPKORIR", "admission_number": "HS9G005", "gender": "Male"},
        {"name": "ESTHER NJERI MWANGI", "admission_number": "HS9G006", "gender": "Female"},
        {"name": "FRED KIMANI MWANGI", "admission_number": "HS9G007", "gender": "Male"},
        {"name": "GLORIA WANJIKU KIMANI", "admission_number": "HS9G008", "gender": "Female"},
        {"name": "HENRY KIPKORIR", "admission_number": "HS9G009", "gender": "Male"},
        {"name": "IRENE NJERI MWANGI", "admission_number": "HS9G010", "gender": "Female"},
        {"name": "JACKSON KIMANI MWANGI", "admission_number": "HS9G011", "gender": "Male"},
        {"name": "KAREN WANJIKU KIMANI", "admission_number": "HS9G012", "gender": "Female"},
        {"name": "LEWIS KIPKORIR", "admission_number": "HS9G013", "gender": "Male"},
        {"name": "MARTHA NJERI MWANGI", "admission_number": "HS9G014", "gender": "Female"},
        {"name": "NICHOLAS KIMANI MWANGI", "admission_number": "HS9G015", "gender": "Male"},
        {"name": "PAULINE WANJIKU KIMANI", "admission_number": "HS9G016", "gender": "Female"},
        {"name": "RICHARD KIPKORIR", "admission_number": "HS9G017", "gender": "Male"},
        {"name": "RUTH NJERI MWANGI", "admission_number": "HS9G018", "gender": "Female"},
        {"name": "SIMON KIMANI MWANGI", "admission_number": "HS9G019", "gender": "Male"},
        {"name": "SUSAN WANJIKU KIMANI", "admission_number": "HS9G020", "gender": "Female"},
        {"name": "THOMAS KIPKORIR", "admission_number": "HS9G021", "gender": "Male"},
        {"name": "VICTOR KIMANI MWANGI", "admission_number": "HS9G022", "gender": "Male"},
        {"name": "WINNIE NJERI MWANGI", "admission_number": "HS9G023", "gender": "Female"},
        {"name": "ALBERT KIPKORIR", "admission_number": "HS9G024", "gender": "Male"},
        {"name": "BETH WANJIKU KIMANI", "admission_number": "HS9G025", "gender": "Female"},
        {"name": "CALVIN KIMANI MWANGI", "admission_number": "HS9G026", "gender": "Male"},
        {"name": "DORIS NJERI MWANGI", "admission_number": "HS9G027", "gender": "Female"},
        {"name": "ERIC KIPKORIR", "admission_number": "HS9G028", "gender": "Male"},
        {"name": "FIONA WANJIKU KIMANI", "admission_number": "HS9G029", "gender": "Female"},
        {"name": "GILBERT KIMANI MWANGI", "admission_number": "HS9G030", "gender": "Male"},
        {"name": "HILDA NJERI MWANGI", "admission_number": "HS9G031", "gender": "Female"},
        {"name": "IVAN KIPKORIR", "admission_number": "HS9G032", "gender": "Male"},
        {"name": "JANET WANJIKU KIMANI", "admission_number": "HS9G033", "gender": "Female"},
        {"name": "KELVIN KIMANI MWANGI", "admission_number": "HS9G034", "gender": "Male"},
        {"name": "LAURA NJERI MWANGI", "admission_number": "HS9G035", "gender": "Female"},
    ]

    for student_data in students_stream_g:
        student = Student(
            name=student_data["name"],
            admission_number=student_data["admission_number"],
            stream=stream_g,
            gender=student_data["gender"].lower()
        )
        db.session.add(student)

    # Add 35 students to Grade 9 Stream Y (21 boys, 14 girls)
    students_stream_y = [
        {"name": "ANDREW KIPKORIR", "admission_number": "HS9Y001", "gender": "Male"},
        {"name": "BEATRICE WANJIKU KIMANI", "admission_number": "HS9Y002", "gender": "Female"},
        {"name": "CHRISTOPHER KIMANI MWANGI", "admission_number": "HS9Y003", "gender": "Male"},
        {"name": "DOROTHY NJERI MWANGI", "admission_number": "HS9Y004", "gender": "Female"},
        {"name": "ELVIS KIPKORIR", "admission_number": "HS9Y005", "gender": "Male"},
        {"name": "FAITH WANJIKU KIMANI", "admission_number": "HS9Y006", "gender": "Female"},
        {"name": "GIDEON KIMANI MWANGI", "admission_number": "HS9Y007", "gender": "Male"},
        {"name": "HANNAH NJERI MWANGI", "admission_number": "HS9Y008", "gender": "Female"},
        {"name": "ISAIAH KIPKORIR", "admission_number": "HS9Y009", "gender": "Male"},
        {"name": "JACQUELINE WANJIKU KIMANI", "admission_number": "HS9Y010", "gender": "Female"},
        {"name": "KENNETH KIMANI MWANGI", "admission_number": "HS9Y011", "gender": "Male"},
        {"name": "LINDA NJERI MWANGI", "admission_number": "HS9Y012", "gender": "Female"},
        {"name": "MARTIN KIPKORIR", "admission_number": "HS9Y013", "gender": "Male"},
        {"name": "NAOMI WANJIKU KIMANI", "admission_number": "HS9Y014", "gender": "Female"},
        {"name": "OSCAR KIMANI MWANGI", "admission_number": "HS9Y015", "gender": "Male"},
        {"name": "PRISCILLA NJERI MWANGI", "admission_number": "HS9Y016", "gender": "Female"},
        {"name": "RAYMOND KIPKORIR", "admission_number": "HS9Y017", "gender": "Male"},
        {"name": "SHARON WANJIKU KIMANI", "admission_number": "HS9Y018", "gender": "Female"},
        {"name": "TIMOTHY KIMANI MWANGI", "admission_number": "HS9Y019", "gender": "Male"},
        {"name": "VERONICA NJERI MWANGI", "admission_number": "HS9Y020", "gender": "Female"},
        {"name": "WALTER KIPKORIR", "admission_number": "HS9Y021", "gender": "Male"},
        {"name": "ZACHARY KIMANI MWANGI", "admission_number": "HS9Y022", "gender": "Male"},
        {"name": "AGNES WANJIKU KIMANI", "admission_number": "HS9Y023", "gender": "Female"},
        {"name": "BARRY KIPKORIR", "admission_number": "HS9Y024", "gender": "Male"},
        {"name": "CLARA NJERI MWANGI", "admission_number": "HS9Y025", "gender": "Female"},
        {"name": "DAVIS KIMANI MWANGI", "admission_number": "HS9Y026", "gender": "Male"},
        {"name": "ELIZABETH WANJIKU KIMANI", "admission_number": "HS9Y027", "gender": "Female"},
        {"name": "FRANK KIPKORIR", "admission_number": "HS9Y028", "gender": "Male"},
        {"name": "GRACE NJERI MWANGI", "admission_number": "HS9Y029", "gender": "Female"},
        {"name": "HAROLD KIMANI MWANGI", "admission_number": "HS9Y030", "gender": "Male"},
        {"name": "IVY WANJIKU KIMANI", "admission_number": "HS9Y031", "gender": "Female"},
        {"name": "JONAH KIPKORIR", "admission_number": "HS9Y032", "gender": "Male"},
        {"name": "KELLY NJERI MWANGI", "admission_number": "HS9Y033", "gender": "Female"},
        {"name": "LEONARD KIMANI MWANGI", "admission_number": "HS9Y034", "gender": "Male"},
        {"name": "MONICA WANJIKU KIMANI", "admission_number": "HS9Y035", "gender": "Female"},
    ]

    for student_data in students_stream_y:
        student = Student(
            name=student_data["name"],
            admission_number=student_data["admission_number"],
            stream=stream_y,
            gender=student_data["gender"].lower()
        )
        db.session.add(student)

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
    print("Grade 9 with Streams B, G, Y and student data added successfully!")

print("Database initialization completed. You can now run 'python app.py' to start the server.")