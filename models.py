# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Many-to-many relationship table between Teacher and Subject
teacher_subjects = db.Table('teacher_subjects',
    db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    education_level = db.Column(db.String(50), nullable=False)
    marks = db.relationship('Mark', backref='subject', lazy=True)
    teachers = db.relationship('Teacher', secondary=teacher_subjects, backref=db.backref('subjects', lazy=True))

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    stream_id = db.Column(db.Integer, db.ForeignKey('stream.id'), nullable=True)
    stream = db.relationship('Stream', backref=db.backref('teachers', lazy=True))

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(50), unique=True, nullable=False)  # Increased length to match previous version
    streams = db.relationship('Stream', backref='grade', lazy=True)

class Stream(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # Increased length to match previous version
    grade_id = db.Column(db.Integer, db.ForeignKey('grade.id'), nullable=False)
    students = db.relationship('Student', backref='stream', lazy=True)

class Term(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    marks = db.relationship('Mark', backref='term', lazy=True)

class AssessmentType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    marks = db.relationship('Mark', backref='assessment_type', lazy=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    admission_number = db.Column(db.String(50), unique=True, nullable=False)  # Added field
    stream_id = db.Column(db.Integer, db.ForeignKey('stream.id'), nullable=True)  # Changed to nullable=True
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    marks = db.relationship('Mark', backref='student', lazy=True)

class Mark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'), nullable=False)
    assessment_type_id = db.Column(db.Integer, db.ForeignKey('assessment_type.id'), nullable=False)
    mark = db.Column(db.Float, nullable=False)
    total_marks = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())