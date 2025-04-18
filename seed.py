from app import app, db
from models import Teacher, Grade, Stream, Student, Subject, Term, AssessmentType

with app.app_context():
    # Clear existing data
    db.drop_all()
    db.create_all()

    # Add Teachers
    teachers = [
        Teacher(username="teacher1", password="pass123", role="teacher"),
        Teacher(username="headteacher", password="admin123", role="headteacher"),
        Teacher(username="classteacher1", password="class123", role="classteacher")
    ]
    db.session.add_all(teachers)

    # Add Grades (1 to 8, excluding Grade 9 to align with primary and junior secondary levels)
    grades = [Grade(level=str(i)) for i in range(1, 9)]
    db.session.add_all(grades)
    db.session.commit()

    # Add Streams
    streams_data = {}
    stream_names = ["B", "G", "Y"]
    for grade in grades:
        streams = []
        for stream_name in stream_names:
            stream = Stream(name=stream_name, grade_id=grade.id)
            streams.append(stream)
        streams_data[grade.level] = streams
        db.session.add_all(streams)
    db.session.commit()

    # Add Students (Grades 1 to 8, excluding Grade 9)
    students_data = {
        "1": {
            "B": [f"Student {i} Grade 1B" for i in range(1, 16)],
            "G": [f"Student {i} Grade 1G" for i in range(1, 16)],
            "Y": [f"Student {i} Grade 1Y" for i in range(1, 16)]
        },
        "2": {
            "B": [f"Student {i} Grade 2B" for i in range(1, 16)],
            "G": [f"Student {i} Grade 2G" for i in range(1, 16)],
            "Y": [f"Student {i} Grade 2Y" for i in range(1, 16)]
        },
        "3": {
            "B": [f"Student {i} Grade 3B" for i in range(1, 16)],
            "G": [f"Student {i} Grade 3G" for i in range(1, 16)],
            "Y": [f"Student {i} Grade 3Y" for i in range(1, 16)]
        },
        "4": {
            "B": [f"Student {i} Grade 4B" for i in range(1, 16)],
            "G": [f"Student {i} Grade 4G" for i in range(1, 16)],
            "Y": [f"Student {i} Grade 4Y" for i in range(1, 16)]
        },
        "5": {
            "B": [f"Student {i} Grade 5B" for i in range(1, 16)],
            "G": [f"Student {i} Grade 5G" for i in range(1, 16)],
            "Y": [f"Student {i} Grade 5Y" for i in range(1, 16)]
        },
        "6": {
            "B": [f"Student {i} Grade 6B" for i in range(1, 16)],
            "G": [f"Student {i} Grade 6G" for i in range(1, 16)],
            "Y": [f"Student {i} Grade 6Y" for i in range(1, 16)]
        },
        "7": {
            "B": [f"Student {i} Grade 7B" for i in range(1, 16)],
            "G": [f"Student {i} Grade 7G" for i in range(1, 16)],
            "Y": [f"Student {i} Grade 7Y" for i in range(1, 16)]
        },
        "8": {
            "B": [
                "ALVIN BLESSED .", "ALVIN NGANGA WANJIKU", "AMARA SAU MGHANGA",
                "CASEY RAPHAELA OWUOR", "CECILINE MBOO KANURI",
                "CELLINE MUTHONI GITHIEYA", "CLAIRE NJERI GIKONYO",
                "DIDUMO OJUAK OKELLO", "ETHAN MWANGI KINYUA",
                "FAITH WANGECHI KAGIRI", "GIBSON NGARI MUNENE",
                "GOY PETER MAJOK", "HARVEY MUGO MACHARIA",
                "JAMILA KANIRI NTOITI", "JAYDEN NJAGI MUNGA"
            ],
            "G": [
                "BRIDGETTE WAIRIMU MUTONGA", "BRYTON KOSGEI KISANG",
                "CALEB MUTIE MUTEMI", "CASTROL CHERUIYOT KORIR",
                "DELANE MAKORI MOREMA", "FAITH WANGARI WAMBUGU",
                "FAITH WANJIKU KINYUA", "FRANKLIN MURIUKI MWANGI",
                "HABIB MUMO MWENDWA", "IVY WAMBUI GICHOBI",
                "JAMES MATHINA GITHUA", "JAYDEN KIMATHI KOOME",
                "JOY GILGER KENDI NYAGA", "KRISTA KENDI MURIITHI",
                "LUCY WANJIRU NDUNGU"
            ],
            "Y": [
                "ABBY TATYANA MUKABI", "ADRIAN MBAU MWANGI",
                "ALISHA WANJIKU NJUBI", "ALVIN NDORO WAIRAGU",
                "ALVIN OWEIN MBUGUA", "ANGELA NYAKIO MUNENE",
                "ASHLYN WAYUA JULIA", "BAKHITA WANGECHI GACHOKA",
                "BIANCA WAMBUI NJERI", "BIANKA ANON MULUAL",
                "CARL KINYUA IKE", "CHERISE NJOKI WAIRAGU",
                "CHRISTINE WANGECHI MAINA", "CHRISTINE WANJA NJERU",
                "DANIELLA NYAMBURA MWANGI"
            ]
        }
    }

    for grade_level, streams in students_data.items():
        grade = Grade.query.filter_by(level=grade_level).first()
        if not grade:
            continue  # Skip if grade doesn't exist
        for stream_name, student_names in streams.items():
            stream = Stream.query.filter_by(name=stream_name, grade_id=grade.id).first()
            if not stream:
                continue  # Skip if stream doesn't exist
            students = [Student(name=name, stream_id=stream.id) for name in student_names]
            db.session.add_all(students)

    # Add Subjects for all education levels
    education_levels = ["lower_primary", "upper_primary", "junior_secondary"]
    subject_names = [
        "Mathematics", "English", "Kiswahili", "Integrated Science and Health Education",
        "Agriculture", "Pre-Technical Studies", "Visual Arts", "Religious Education",
        "Social Studies"
    ]
    subjects = []
    for edu_level in education_levels:
        for subject_name in subject_names:
            subjects.append(Subject(name=subject_name, education_level=edu_level))
    db.session.add_all(subjects)

    # Add Terms
    terms = [
        Term(name="term_1"),
        Term(name="term_2"),
        Term(name="term_3")
    ]
    db.session.add_all(terms)

    # Add Assessment Types
    assessment_types = [
        AssessmentType(name="opener"),
        AssessmentType(name="midterm"),
        AssessmentType(name="endterm")
    ]
    db.session.add_all(assessment_types)

    db.session.commit()
    print("Database seeded successfully!")