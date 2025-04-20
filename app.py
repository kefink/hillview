from flask import Flask, render_template, request, redirect, url_for, send_file, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from datetime import datetime
from collections import defaultdict
import os
import zipfile
from io import BytesIO, StringIO
import pandas as pd

# Import the models
from models import db, Subject, Teacher, Grade, Stream, Term, AssessmentType, Student, Mark

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Configure SQLite database for development
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///E:/DKANTE/hillview_mvp/hillview.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the Flask app
db.init_app(app)

# Education level names
education_level_names = {
    "lower_primary": "Lower Primary",
    "upper_primary": "Upper Primary",
    "junior_secondary": "Junior Secondary"
}

def get_performance_category(percentage):
    if percentage >= 75:
        return "E.E"
    elif percentage >= 50:
        return "M.E"
    elif percentage >= 30:
        return "A.E"
    else:
        return "B.E"

def get_grade_and_points(average):
    if average >= 80:
        return "A", 12
    elif average >= 75:
        return "A-", 11
    elif average >= 70:
        return "B+", 10
    elif average >= 65:
        return "B", 9
    elif average >= 60:
        return "B-", 8
    elif average >= 55:
        return "C+", 7
    elif average >= 50:
        return "C", 6
    elif average >= 45:
        return "C-", 5
    elif average >= 40:
        return "D+", 4
    elif average >= 35:
        return "D", 3
    elif average >= 30:
        return "D-", 2
    else:
        return "E", 1

def get_performance_summary(marks_data):
    summary = defaultdict(int)
    for student in marks_data:
        summary[student[3]] += 1
    return dict(summary)

def generate_individual_report_pdf(grade, stream, term, assessment_type, student_name, class_data, education_level, total_marks, subjects):
    stream_letter = stream[-1] if stream else ''
    student_data = next((data for data in class_data if data['student'].lower() == student_name.lower()), None)
    
    if not student_data:
        return None

    pdf_file = f"individual_report_{grade}_{stream}_{student_name.replace(' ', '_')}.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']
    heading3_style = styles['Heading3']

    elements.append(Paragraph("HILL VIEW SCHOOL", title_style))
    elements.append(Paragraph("P.O. Box 12345 - 00100, Nairobi, Kenya", subtitle_style))
    elements.append(Paragraph("Tel: 0712345678", subtitle_style))
    elements.append(Paragraph(f"ACADEMIC REPORT TERM {term.replace('_', ' ').upper()} 2025", subtitle_style))
    elements.append(Spacer(1, 12))

    student_name_upper = student_name.upper()
    admission_no = f"HS{grade}{stream_letter}{str(class_data.index(student_data) + 1).zfill(3)}"
    elements.append(Paragraph(f"{student_name_upper}  ADM NO.: {admission_no}", normal_style))
    elements.append(Paragraph(f"Grade {grade} {education_level} {stream}", normal_style))

    total = student_data['total_marks']
    avg_percentage = student_data['average_percentage']
    mean_grade, mean_points = get_grade_and_points(avg_percentage)
    total_possible_marks = len(subjects) * total_marks
    total_points = sum(get_grade_and_points(student_data['marks'].get(subject, 0))[1] for subject in subjects)

    elements.append(Paragraph(f"MEAN GRADE: {mean_grade}", normal_style))
    elements.append(Paragraph(f"Mean Points: {mean_points}  Total Marks: {int(total)} out of: {total_possible_marks}", normal_style))
    elements.append(Paragraph(f"Mean Mark: {avg_percentage:.2f}%", normal_style))
    elements.append(Paragraph(f"Total Points: {total_points}", normal_style))
    elements.append(Spacer(1, 12))

    headers = ["Subjects", "Entrance", "Mid Term", "End Term", "Avg.", "Subject Remarks"]
    data = [headers]
    for subject in subjects:
        mark = student_data['marks'].get(subject, 0)
        avg = mark
        percentage = (mark / total_marks) * 100 if total_marks > 0 else 0
        performance = get_performance_category(percentage)
        data.append([
            subject.upper(),
            "",
            "",
            str(int(mark)),
            str(int(avg)),
            f"{performance}"
        ])

    data.append([
        "Totals",
        "",
        "",
        str(int(total)),
        str(int(total)),
        ""
    ])

    table = Table(data)
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]

    table.setStyle(TableStyle(table_style))
    elements.append(table)

    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Class Teacher's Remarks:", heading3_style))
    elements.append(Paragraph("Well done! With continued focus and consistency, you have the potential to achieve even more.", normal_style))
    elements.append(Paragraph("Class Teacher: Moses Barasa", normal_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Head Teacher's Remarks:", heading3_style))
    elements.append(Paragraph("Great progress! Your growing confidence is evident - keep practicing, and you'll excel even further.", normal_style))
    elements.append(Paragraph("Head Teacher Name: Mr. Paul Mwangi", normal_style))
    elements.append(Paragraph("Head Teacher Signature: ____________________", normal_style))
    elements.append(Paragraph("Next Term Begins on: TBD", normal_style))

    elements.append(Spacer(1, 12))
    footer_style = styles['Normal']
    footer_style.alignment = 1
    current_date = datetime.now().strftime("%Y-%m-%d")
    elements.append(Paragraph(f"Generated on: {current_date}", footer_style))
    elements.append(Paragraph("Hillview School powered by CbcTeachkit", footer_style))

    doc.build(elements)
    return pdf_file

@app.route("/")
def index():
    app.logger.warning("Index route accessed!")  # Will appear in terminal
    try:
        return render_template("login.html")
    except Exception as e:
        app.logger.error(f"Error rendering login.html: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        teacher = Teacher.query.filter_by(username=username, password=password, role="headteacher").first()
        if teacher:
            session['teacher_id'] = teacher.id
            session['role'] = 'headteacher'
            session.permanent = True
            return redirect(url_for("headteacher"))
        return render_template("admin_login.html", error="Invalid credentials")
    return render_template("admin_login.html")

@app.route("/teacher_login", methods=["GET", "POST"])
def teacher_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        teacher = Teacher.query.filter_by(username=username, password=password, role="teacher").first()
        if teacher:
            session['teacher_id'] = teacher.id
            session['role'] = 'teacher'
            session.permanent = True
            return redirect(url_for("teacher"))
        return render_template("teacher_login.html", error="Invalid credentials")
    return render_template("teacher_login.html")

@app.route("/classteacher_login", methods=["GET", "POST"])
def classteacher_login():
    print("Request method:", request.method)
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        print("Username:", username)
        print("Password:", password)
        teacher = Teacher.query.filter_by(username=username, password=password, role="classteacher").first()
        if teacher:
            print("Teacher found:", teacher.username)
            session['teacher_id'] = teacher.id
            session['role'] = 'classteacher'
            session.permanent = True
            print("Session:", session)
            return redirect(url_for("classteacher"))
        print("No teacher found")
        return render_template("classteacher_login.html", error="Invalid credentials")
    return render_template("classteacher_login.html")

@app.route("/teacher", methods=["GET", "POST"])
def teacher():
    if 'teacher_id' not in session or session['role'] != 'teacher':
        return redirect(url_for('teacher_login'))

    grades = [grade.level for grade in Grade.query.all()]
    grades_dict = {grade.level: grade.id for grade in Grade.query.all()}  # Mapping of grade levels to IDs
    subjects = [subject.name for subject in Subject.query.all()]
    terms = [term.name for term in Term.query.all()]
    assessment_types = [assessment_type.name for assessment_type in AssessmentType.query.all()]
    error_message = None
    show_students = False
    students = []
    subject = ""
    grade = ""
    stream = ""
    term = ""
    assessment_type = ""
    total_marks = 0
    show_download_button = False

    # Fetch recent reports (last 5 unique grade/stream/term/assessment combinations)
    recent_reports = []
    marks = Mark.query.join(Student).join(Stream).join(Grade).join(Term).join(AssessmentType).all()
    seen_combinations = set()
    for mark in marks:
        combination = (mark.student.stream.grade.level, mark.student.stream.name, mark.term.name, mark.assessment_type.name)
        if combination not in seen_combinations:
            seen_combinations.add(combination)
            recent_reports.append({
                'grade': mark.student.stream.grade.level,
                'stream': f"Stream {mark.student.stream.name}",
                'term': mark.term.name,
                'assessment_type': mark.assessment_type.name,
                'date': mark.created_at.strftime('%Y-%m-%d') if mark.created_at else 'N/A'
            })
            if len(recent_reports) >= 5:  # Limit to 5 recent reports
                break

    if request.method == "POST":
        subject = request.form.get("subject", "")
        grade = request.form.get("grade", "")
        stream = request.form.get("stream", "")
        term = request.form.get("term", "")
        assessment_type = request.form.get("assessment_type", "")
        try:
            total_marks = int(request.form.get("total_marks", 0))
        except ValueError:
            total_marks = 0

        if "upload_marks" in request.form:
            if not all([subject, grade, stream, term, assessment_type, total_marks > 0]):
                error_message = "Please fill in all fields before uploading marks"
            else:
                stream_obj = Stream.query.join(Grade).filter(Grade.level == grade, Stream.name == stream[-1]).first()
                if stream_obj:
                    students = [student.name for student in Student.query.filter_by(stream_id=stream_obj.id).all()]
                    show_students = True
                else:
                    error_message = f"No students found for grade {grade} stream {stream[-1]}"

        elif "submit_marks" in request.form:
            if not all([subject, grade, stream, term, assessment_type, total_marks > 0]):
                error_message = "Please fill in all fields before submitting marks"
            else:
                stream_obj = Stream.query.join(Grade).filter(Grade.level == grade, Stream.name == stream[-1]).first()
                subject_obj = Subject.query.filter_by(name=subject).first()
                term_obj = Term.query.filter_by(name=term).first()
                assessment_type_obj = AssessmentType.query.filter_by(name=assessment_type).first()

                if not (stream_obj and subject_obj and term_obj and assessment_type_obj):
                    error_message = "Invalid selection for grade, stream, subject, term, or assessment type"
                else:
                    students = Student.query.filter_by(stream_id=stream_obj.id).all()
                    marks_data = []
                    any_marks_submitted = False

                    for student in students:
                        mark_key = f"mark_{student.name.replace(' ', '_')}"
                        mark_value = request.form.get(mark_key, '')
                        if mark_value and mark_value.isdigit():
                            mark = int(mark_value)
                            if 0 <= mark <= total_marks:
                                percentage = (mark / total_marks) * 100
                                performance = get_performance_category(percentage)
                                marks_data.append([student.name, mark, round(percentage, 1), performance])
                                # Save the mark to the database
                                new_mark = Mark(
                                    student_id=student.id,
                                    subject_id=subject_obj.id,
                                    term_id=term_obj.id,
                                    assessment_type_id=assessment_type_obj.id,
                                    mark=mark,
                                    total_marks=total_marks
                                )
                                db.session.add(new_mark)
                                any_marks_submitted = True
                            else:
                                error_message = f"Invalid mark for {student.name}. Must be between 0 and {total_marks}."
                                break
                        else:
                            error_message = f"Missing or invalid mark for {student.name}"
                            break

                    if any_marks_submitted and not error_message:
                        db.session.commit()
                        mean_score = sum(mark[1] for mark in marks_data) / len(marks_data) if marks_data else 0
                        mean_percentage = (mean_score / total_marks) * 100 if total_marks > 0 else 0
                        mean_performance = get_performance_category(mean_percentage)
                        performance_summary = get_performance_summary(marks_data)

                        return render_template(
                            "report.html",
                            data=marks_data,
                            mean_score=mean_score,
                            mean_percentage=mean_percentage,
                            mean_performance=mean_performance,
                            performance_summary=performance_summary,
                            education_level="",
                            subject=subject,
                            grade=grade,
                            stream=stream,
                            term=term,
                            assessment_type=assessment_type,
                            total_marks=total_marks
                        )

    return render_template(
        "teacher.html",
        grades=grades,
        grades_dict=grades_dict,
        subjects=subjects,
        terms=terms,
        assessment_types=assessment_types,
        students=students,
        subject=subject,
        grade=grade,
        stream=stream,
        term=term,
        assessment_type=assessment_type,
        total_marks=total_marks,
        show_students=show_students,
        error_message=error_message,
        show_download_button=show_download_button,
        recent_reports=recent_reports
    )

@app.route("/classteacher", methods=["GET", "POST"])
def classteacher():
    if 'teacher_id' not in session or session['role'] != 'classteacher':
        return redirect(url_for('classteacher_login'))

    grades = [grade.level for grade in Grade.query.all()]
    grades_dict = {grade.level: grade.id for grade in Grade.query.all()}  # Mapping of grade levels to IDs
    terms = [term.name for term in Term.query.all()]
    assessment_types = [assessment_type.name for assessment_type in AssessmentType.query.all()]
    streams = Stream.query.all()  # Fetch all streams for the dropdown
    error_message = None
    show_students = False
    students = []
    education_level = ""
    grade = ""
    stream = ""
    term = ""
    assessment_type = ""
    total_marks = 0
    show_download_button = False
    show_individual_report_button = False
    subjects = []
    stats = None
    class_data = None

    # Fetch recent reports (last 5 unique grade/stream/term/assessment combinations)
    recent_reports = []
    marks = Mark.query.join(Student).join(Stream).join(Grade).join(Term).join(AssessmentType).all()
    seen_combinations = set()
    for mark in marks:
        combination = (mark.student.stream.grade.level, mark.student.stream.name, mark.term.name, mark.assessment_type.name)
        if combination not in seen_combinations:
            seen_combinations.add(combination)
            recent_reports.append({
                'grade': mark.student.stream.grade.level,
                'stream': f"Stream {mark.student.stream.name}",
                'term': mark.term.name,
                'assessment_type': mark.assessment_type.name,
                'date': mark.created_at.strftime('%Y-%m-%d') if mark.created_at else 'N/A'
            })
            if len(recent_reports) >= 5:  # Limit to 5 recent reports
                break

    subject_mapping = {
        "lower_primary": [
            "Mathematics", "English", "Kiswahili", "Integrated Science and Health Education",
            "Agriculture", "Pre-Technical Studies", "Visual Arts", "Religious Education",
            "Social Studies"
        ],
        "upper_primary": [
            "Mathematics", "English", "Kiswahili", "Integrated Science and Health Education",
            "Agriculture", "Pre-Technical Studies", "Visual Arts", "Religious Education",
            "Social Studies"
        ],
        "junior_secondary": [
            "Mathematics", "English", "Kiswahili", "Integrated Science and Health Education",
            "Agriculture", "Pre-Technical Studies", "Visual Arts", "Religious Education",
            "Social Studies"
        ]
    }

    if request.method == "POST":
        education_level = request.form.get("education_level", "")
        grade = request.form.get("grade", "")
        stream = request.form.get("stream", "")
        term = request.form.get("term", "")
        assessment_type = request.form.get("assessment_type", "")
        try:
            total_marks = int(request.form.get("total_marks", 0))
        except ValueError:
            total_marks = 0

        subjects = subject_mapping.get(education_level, [])

        if "upload_marks" in request.form:
            if not all([education_level, grade, stream, term, assessment_type, total_marks > 0]):
                error_message = "Please fill in all fields before uploading marks"
            else:
                stream_letter = stream.replace("Stream ", "") if stream.startswith("Stream ") else stream[-1]
                stream_obj = Stream.query.join(Grade).filter(Grade.level == grade, Stream.name == stream_letter).first()
                if stream_obj:
                    students = [student.name for student in Student.query.filter_by(stream_id=stream_obj.id).all()]
                    show_students = True
                else:
                    error_message = f"No students found for grade {grade} stream {stream_letter}"

        elif "submit_marks" in request.form:
            if not all([education_level, grade, stream, term, assessment_type, total_marks > 0]):
                error_message = "Please fill in all fields before submitting marks"
            else:
                stream_letter = stream.replace("Stream ", "") if stream.startswith("Stream ") else stream[-1]
                stream_obj = Stream.query.join(Grade).filter(Grade.level == grade, Stream.name == stream_letter).first()
                term_obj = Term.query.filter_by(name=term).first()
                assessment_type_obj = AssessmentType.query.filter_by(name=assessment_type).first()

                if not (stream_obj and term_obj and assessment_type_obj):
                    error_message = "Invalid selection for grade, stream, term, or assessment type"
                else:
                    students = Student.query.filter_by(stream_id=stream_obj.id).all()
                    marks_data = []
                    any_marks_submitted = False
                    subject_marks = {subject: {} for subject in subjects}

                    subject_objs = {subject: Subject.query.filter_by(name=subject).first() for subject in subjects}
                    for student in students:
                        student_marks = {}
                        valid_student = True
                        for subject in subjects:
                            mark_key = f"mark_{student.name.replace(' ', '_')}_{subject.replace(' ', '_')}"
                            mark_value = request.form.get(mark_key, '')
                            if mark_value and mark_value.replace('.', '').isdigit():
                                mark = float(mark_value)
                                if 0 <= mark <= total_marks:
                                    subject_marks[subject][student.name] = mark
                                    student_marks[subject] = mark
                                    # Save the mark to the database
                                    subject_obj = subject_objs[subject]
                                    if subject_obj:
                                        new_mark = Mark(
                                            student_id=student.id,
                                            subject_id=subject_obj.id,
                                            term_id=term_obj.id,
                                            assessment_type_id=assessment_type_obj.id,
                                            mark=mark,
                                            total_marks=total_marks
                                        )
                                        db.session.add(new_mark)
                                    any_marks_submitted = True
                                else:
                                    error_message = f"Invalid mark for {student.name} in {subject}. Must be between 0 and {total_marks}."
                                    valid_student = False
                                    break
                            else:
                                error_message = f"Missing or invalid mark for {student.name} in {subject}"
                                valid_student = False
                                break
                        if valid_student:
                            marks_data.append([student.name, student_marks])

                    if any_marks_submitted and not error_message:
                        db.session.commit()
                        class_data = []
                        for student, student_marks in marks_data:
                            total = sum(student_marks.values())
                            avg_percentage = (total / (len(subjects) * total_marks)) * 100
                            class_data.append({
                                'student': student,
                                'marks': student_marks,
                                'total_marks': total,
                                'average_percentage': avg_percentage
                            })

                        class_data.sort(key=lambda x: x['total_marks'], reverse=True)
                        for i, student_data in enumerate(class_data, 1):
                            student_data['rank'] = i

                        stats = {'exceeding': 0, 'meeting': 0, 'approaching': 0, 'below': 0}
                        for student_data in class_data:
                            avg = student_data['average_percentage']
                            if avg >= 75:
                                stats['exceeding'] += 1
                            elif 50 <= avg < 75:
                                stats['meeting'] += 1
                            elif 30 <= avg < 50:
                                stats['approaching'] += 1
                            else:
                                stats['below'] += 1

                        show_download_button = True
                        show_individual_report_button = True

    return render_template(
        "classteacher.html",
        grades=grades,
        grades_dict=grades_dict,
        terms=terms,
        assessment_types=assessment_types,
        streams=streams,
        students=students,
        education_level=education_level,
        grade=grade,
        stream=stream,
        term=term,
        assessment_type=assessment_type,
        total_marks=total_marks,
        show_students=show_students,
        error_message=error_message,
        show_download_button=show_download_button,
        show_individual_report_button=show_individual_report_button,
        subjects=subjects,
        stats=stats,
        class_data=class_data,
        recent_reports=recent_reports
    )

@app.route("/headteacher")
def headteacher():
    if 'teacher_id' not in session or session['role'] != 'headteacher':
        return redirect(url_for('admin_login'))

    dashboard_data = []
    # Compute mean scores for each class
    for grade in Grade.query.all():
        for stream in grade.streams:
            students = Student.query.filter_by(stream_id=stream.id).all()
            if not students:
                continue
            total_avg = 0
            student_count = 0
            for student in students:
                marks = Mark.query.filter_by(student_id=student.id).all()
                if marks:
                    avg = sum(mark.mark for mark in marks) / len(marks)
                    total_avg += (avg / marks[0].total_marks) * 100 if marks[0].total_marks else 0
                    student_count += 1
            if student_count > 0:
                mean_score = total_avg / student_count
                dashboard_data.append({"grade": f"{grade.level}{stream.name}", "mean": round(mean_score, 1)})

    dashboard_data.sort(key=lambda x: x["grade"])
    return render_template("headteacher.html", data=dashboard_data)

@app.route("/get_streams/<grade_id>", methods=["GET"])
def get_streams(grade_id):
    try:
        grade_id = int(grade_id)
        streams = Stream.query.filter_by(grade_id=grade_id).all()
        return jsonify({"streams": [{"id": stream.id, "name": stream.name} for stream in streams]})
    except ValueError:
        return jsonify({"streams": [], "error": "Invalid grade ID"}), 400

@app.route("/manage_students", methods=["GET", "POST"])
def manage_students():
    if 'teacher_id' not in session or session['role'] != 'classteacher':
        return redirect(url_for('classteacher_login'))

    error_message = None
    success_message = None
    selected_level = None

    # Define educational levels
    educational_levels = [
        "Lower Primary",
        "Upper Primary",
        "Junior School",
        "Senior School",
        "High School"
    ]

    # Map educational levels to grade levels (for filtering)
    educational_level_mapping = {
        "Lower Primary": ["Grade 1", "Grade 2", "Grade 3"],
        "Upper Primary": ["Grade 4", "Grade 5", "Grade 6"],
        "Junior School": ["Grade 7", "Grade 8", "Grade 9"],
        "Senior School": ["Grade 10", "Grade 11", "Grade 12"],
        "High School": ["Form 2", "Form 3", "Form 4"]
    }

    # Get the selected educational level (from form, query params, or none)
    selected_level = request.args.get('level') or request.form.get('educational_level') or request.form.get('redirect_level')

    if request.method == "POST":
        action = request.form.get('action')
        redirect_level = request.form.get('redirect_level') or selected_level  # Fallback to selected_level if redirect_level is not provided

        # Add a Grade
        if action == 'add_grade':
            grade_name = request.form.get('grade_name')
            educational_level = request.form.get('educational_level')
            if not educational_level:
                error_message = "Please select an educational level before adding a grade."
            elif grade_name:
                # Validate that the grade name matches the selected educational level
                allowed_grades = educational_level_mapping.get(educational_level, [])
                if grade_name not in allowed_grades:
                    error_message = f"Grade '{grade_name}' is not valid for {educational_level}. Valid grades are: {', '.join(allowed_grades)}."
                else:
                    existing_grade = Grade.query.filter_by(level=grade_name).first()
                    if existing_grade:
                        error_message = f"Grade '{grade_name}' already exists."
                    else:
                        new_grade = Grade(level=grade_name)
                        db.session.add(new_grade)
                        db.session.commit()
                        success_message = f"Grade '{grade_name}' added successfully."
            else:
                error_message = "Grade name is required."

        # Add a Stream
        elif action == 'add_stream':
            stream_name = request.form.get('stream_name')
            grade_id = request.form.get('grade_id')
            educational_level = request.form.get('educational_level')
            if not educational_level:
                error_message = "Please select an educational level before adding a stream."
            elif stream_name and grade_id:
                existing_stream = Stream.query.filter_by(name=stream_name, grade_id=grade_id).first()
                if existing_stream:
                    error_message = f"Stream '{stream_name}' already exists for this grade."
                else:
                    new_stream = Stream(name=stream_name, grade_id=grade_id)
                    db.session.add(new_stream)
                    db.session.commit()
                    success_message = f"Stream '{stream_name}' added successfully."
            else:
                error_message = "Stream name and grade are required."

        # Add a Student (Single Entry)
        elif action == 'add_student':
            name = request.form.get('name')
            admission_number = request.form.get('admission_number')
            stream_id = request.form.get('stream') or None  # Stream is optional
            educational_level = request.form.get('educational_level')
            if not educational_level:
                error_message = "Please select an educational level before adding a student."
            elif not name:
                error_message = "Student name is required."
            elif not admission_number:
                error_message = "Admission number is required."
            else:
                # Check if admission number is unique
                existing_student = Student.query.filter_by(admission_number=admission_number).first()
                if existing_student:
                    error_message = f"Admission number '{admission_number}' is already in use."
                else:
                    # Check if student already exists in the stream (if stream is selected)
                    if stream_id:
                        existing_student = Student.query.filter_by(name=name, stream_id=stream_id).first()
                        if existing_student:
                            error_message = f"Student '{name}' already exists in this stream."
                        else:
                            new_student = Student(name=name, admission_number=admission_number, stream_id=stream_id)
                            db.session.add(new_student)
                            db.session.commit()
                            success_message = f"Student '{name}' added successfully."
                    else:
                        # If no stream, just check for duplicate student name globally
                        existing_student = Student.query.filter_by(name=name, stream_id=None).first()
                        if existing_student:
                            error_message = f"Student '{name}' already exists with no stream."
                        else:
                            new_student = Student(name=name, admission_number=admission_number, stream_id=None)
                            db.session.add(new_student)
                            db.session.commit()
                            success_message = f"Student '{name}' added successfully."

        # Bulk Upload Students
        elif action == 'bulk_upload_students':
            if 'student_file' not in request.files:
                error_message = "No file uploaded."
            else:
                file = request.files['student_file']
                if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
                    error_message = "Only CSV and Excel (.xlsx) files are supported."
                else:
                    try:
                        # Read the file based on its extension
                        if file.filename.endswith('.csv'):
                            # Read CSV file
                            stream = StringIO(file.stream.read().decode("utf-8"))
                            df = pd.read_csv(stream)
                        else:
                            # Read Excel file
                            df = pd.read_excel(file, engine='openpyxl')

                        # Validate required columns
                        required_columns = ['name', 'grade', 'admission_number']
                        if not all(col in df.columns for col in required_columns):
                            error_message = "File must contain 'name', 'grade', and 'admission_number' columns. Optional: 'stream'."
                        else:
                            # Track successful and failed uploads
                            success_count = 0
                            errors = []

                            for index, row in df.iterrows():
                                name = row['name']
                                grade_name = row['grade']
                                admission_number = row['admission_number']
                                stream_name = row.get('stream', None)  # Stream is optional

                                # Validate name
                                if pd.isna(name) or not isinstance(name, str) or not name.strip():
                                    errors.append(f"Row {index + 2}: Invalid or missing name.")
                                    continue

                                # Validate admission number
                                if pd.isna(admission_number) or not str(admission_number).strip():
                                    errors.append(f"Row {index + 2}: Invalid or missing admission number.")
                                    continue

                                # Convert admission number to string (in case it's a number)
                                admission_number = str(admission_number)

                                # Check if admission number is unique
                                existing_student = Student.query.filter_by(admission_number=admission_number).first()
                                if existing_student:
                                    errors.append(f"Row {index + 2}: Admission number '{admission_number}' is already in use.")
                                    continue

                                # Validate grade
                                grade = Grade.query.filter_by(level=grade_name).first()
                                if not grade:
                                    errors.append(f"Row {index + 2}: Grade '{grade_name}' does not exist.")
                                    continue

                                # Validate stream (if provided)
                                stream_id = None
                                if stream_name and not pd.isna(stream_name):
                                    stream = Stream.query.filter_by(name=stream_name, grade_id=grade.id).first()
                                    if not stream:
                                        errors.append(f"Row {index + 2}: Stream '{stream_name}' does not exist for grade '{grade_name}'.")
                                        continue
                                    stream_id = stream.id

                                # Check for duplicates (based on name and stream)
                                if stream_id:
                                    existing_student = Student.query.filter_by(name=name, stream_id=stream_id).first()
                                    if existing_student:
                                        errors.append(f"Row {index + 2}: Student '{name}' already exists in stream '{stream_name}'.")
                                        continue
                                else:
                                    existing_student = Student.query.filter_by(name=name, stream_id=None).first()
                                    if existing_student:
                                        errors.append(f"Row {index + 2}: Student '{name}' already exists with no stream.")
                                        continue

                                # Add the student
                                new_student = Student(name=name, admission_number=admission_number, stream_id=stream_id)
                                db.session.add(new_student)
                                success_count += 1

                            # Commit the transaction
                            db.session.commit()

                            # Prepare success/error messages
                            if success_count > 0:
                                success_message = f"Successfully added {success_count} student(s)."
                            if errors:
                                error_message = "Some students could not be added:\n" + "\n".join(errors)
                            if success_count == 0 and not errors:
                                error_message = "No students were added. Please check the file."

                    except Exception as e:
                        db.session.rollback()
                        error_message = f"Error processing file: {str(e)}"

        # Delete a Student
        elif action == 'delete_student':
            student_id = request.form.get('student_id')
            student = Student.query.get(student_id)
            if student:
                # Check if student has associated marks
                if student.marks:
                    error_message = "Cannot delete student with associated marks."
                else:
                    student_name = student.name
                    db.session.delete(student)
                    db.session.commit()
                    success_message = f"Student '{student_name}' deleted successfully."
            else:
                error_message = "Student not found."

        # Always redirect after POST to maintain Post/Redirect/Get pattern
        # Store messages in session to display after redirect
        if error_message or success_message:
            session['error_message'] = error_message
            session['success_message'] = success_message
        return redirect(url_for('manage_students', level=redirect_level))

    # On GET request, retrieve messages from session if they exist
    error_message = session.pop('error_message', None)
    success_message = session.pop('success_message', None)

    # Fetch grades and convert to JSON-serializable format
    grades = Grade.query.all()
    grades_list = [{"id": grade.id, "level": grade.level} for grade in grades]

    # Fetch streams and convert to JSON-serializable format
    streams = Stream.query.all()
    streams_list = [{"id": stream.id, "name": stream.name, "grade_id": stream.grade_id} for stream in streams]

    # Fetch students and convert to JSON-serializable format
    students = Student.query.all()
    students_list = [
        {
            "id": student.id,
            "name": student.name,
            "admission_number": student.admission_number,
            "stream": {
                "id": student.stream.id if student.stream else None,
                "name": student.stream.name if student.stream else None,
                "grade": {
                    "id": student.stream.grade.id if student.stream else None,
                    "level": student.stream.grade.level if student.stream else None
                }
            } if student.stream else None
        } for student in students
    ]

    return render_template('manage_students.html', 
                           grades=grades_list,
                           streams=streams_list,
                           students=students_list,
                           educational_levels=educational_levels,
                           educational_level_mapping=educational_level_mapping,
                           selected_level=selected_level,
                           error_message=error_message, 
                           success_message=success_message)

@app.route("/manage_subjects", methods=["GET", "POST"])
def manage_subjects():
    if 'teacher_id' not in session or session['role'] != 'classteacher':
        return redirect(url_for('classteacher_login'))

    error_message = None
    success_message = None

    if request.method == "POST":
        if "add_subject" in request.form:
            name = request.form.get("name")
            education_level = request.form.get("education_level")
            if name and education_level:
                # Check if subject already exists
                existing_subject = Subject.query.filter_by(name=name).first()
                if existing_subject:
                    error_message = f"Subject '{name}' already exists."
                else:
                    new_subject = Subject(name=name, education_level=education_level)
                    db.session.add(new_subject)
                    db.session.commit()
                    success_message = f"Subject '{name}' added successfully!"
            else:
                error_message = "Please fill in all fields."

        elif "delete_subject" in request.form:
            subject_id = request.form.get("subject_id")
            subject = Subject.query.get(subject_id)
            if subject:
                # Check if subject is used in marks
                if subject.marks:
                    error_message = "Cannot delete subject with associated marks."
                else:
                    db.session.delete(subject)
                    db.session.commit()
                    success_message = f"Subject '{subject.name}' deleted successfully!"
            else:
                error_message = "Subject not found."

    subjects = Subject.query.all()
    return render_template("manage_subjects.html", subjects=subjects, error_message=error_message, success_message=success_message)

@app.route("/manage_teachers", methods=["GET", "POST"])
def manage_teachers():
    if 'teacher_id' not in session or session['role'] != 'classteacher':
        return redirect(url_for('classteacher_login'))

    error_message = None
    success_message = None
    subjects = Subject.query.all()  # Fetch all subjects for the dropdown
    grades = Grade.query.all()  # Fetch all grades for the dropdown

    if request.method == "POST":
        if "add_teacher" in request.form:
            username = request.form.get("username")
            password = request.form.get("password")
            role = request.form.get("role")
            subject_ids = request.form.getlist("subjects")  # Get list of selected subject IDs
            stream_id = request.form.get("stream")

            if username and password and role and subject_ids and stream_id:
                # Check if teacher already exists
                existing_teacher = Teacher.query.filter_by(username=username).first()
                if existing_teacher:
                    error_message = f"Teacher with username '{username}' already exists."
                else:
                    # Create new teacher
                    new_teacher = Teacher(username=username, password=password, role=role, stream_id=stream_id)
                    # Assign subjects
                    selected_subjects = Subject.query.filter(Subject.id.in_(subject_ids)).all()
                    new_teacher.subjects = selected_subjects
                    db.session.add(new_teacher)
                    db.session.commit()
                    success_message = f"Teacher '{username}' added successfully!"
            else:
                error_message = "Please fill in all fields."

        elif "delete_teacher" in request.form:
            teacher_id = request.form.get("teacher_id")
            teacher = Teacher.query.get(teacher_id)
            if teacher:
                db.session.delete(teacher)
                db.session.commit()
                success_message = f"Teacher '{teacher.username}' deleted successfully!"
            else:
                error_message = "Teacher not found."

    teachers = Teacher.query.all()
    return render_template("manage_teachers.html", teachers=teachers, subjects=subjects, grades=grades, error_message=error_message, success_message=success_message)

@app.route("/manage_grades_streams", methods=["GET", "POST"])
def manage_grades_streams():
    if 'teacher_id' not in session or session['role'] != 'classteacher':
        return redirect(url_for('classteacher_login'))

    error_message = None
    success_message = None

    if request.method == "POST":
        if "add_grade" in request.form:
            grade_level = request.form.get("grade_level")
            if grade_level:
                existing_grade = Grade.query.filter_by(level=grade_level).first()
                if existing_grade:
                    error_message = f"Grade '{grade_level}' already exists."
                else:
                    new_grade = Grade(level=grade_level)
                    db.session.add(new_grade)
                    db.session.commit()
                    success_message = f"Grade '{grade_level}' added successfully!"
            else:
                error_message = "Please fill in the grade level."

        elif "add_stream" in request.form:
            stream_name = request.form.get("stream_name")
            grade_id = request.form.get("grade_id")
            if stream_name and grade_id:
                grade = Grade.query.get(grade_id)
                if not grade:
                    error_message = "Selected grade not found."
                else:
                    existing_stream = Stream.query.filter_by(name=stream_name, grade_id=grade_id).first()
                    if existing_stream:
                        error_message = f"Stream '{stream_name}' already exists for Grade {grade.level}."
                    else:
                        new_stream = Stream(name=stream_name, grade_id=grade_id)
                        db.session.add(new_stream)
                        db.session.commit()
                        success_message = f"Stream '{stream_name}' added to Grade {grade.level} successfully!"
            else:
                error_message = "Please fill in all fields."

        elif "delete_grade" in request.form:
            grade_id = request.form.get("grade_id")
            grade = Grade.query.get(grade_id)
            if grade:
                # Check if grade has streams with students
                for stream in grade.streams:
                    if stream.students:
                        error_message = f"Cannot delete Grade {grade.level} because it has students in its streams."
                        break
                else:
                    db.session.delete(grade)
                    db.session.commit()
                    success_message = f"Grade '{grade.level}' deleted successfully!"
            else:
                error_message = "Grade not found."

        elif "delete_stream" in request.form:
            stream_id = request.form.get("stream_id")
            stream = Stream.query.get(stream_id)
            if stream:
                # Check if stream has students
                if stream.students:
                    error_message = f"Cannot delete Stream {stream.name} because it has associated students."
                else:
                    db.session.delete(stream)
                    db.session.commit()
                    success_message = f"Stream '{stream.name}' deleted successfully!"
            else:
                error_message = "Stream not found."

    grades = Grade.query.all()
    return render_template("manage_grades_streams.html", grades=grades, error_message=error_message, success_message=success_message)

@app.route("/manage_terms_assessments", methods=["GET", "POST"])
def manage_terms_assessments():
    if 'teacher_id' not in session or session['role'] != 'classteacher':
        return redirect(url_for('classteacher_login'))

    error_message = None
    success_message = None

    if request.method == "POST":
        if "add_term" in request.form:
            term_name = request.form.get("term_name")
            if term_name:
                existing_term = Term.query.filter_by(name=term_name).first()
                if existing_term:
                    error_message = f"Term '{term_name}' already exists."
                else:
                    new_term = Term(name=term_name)
                    db.session.add(new_term)
                    db.session.commit()
                    success_message = f"Term '{term_name}' added successfully!"
            else:
                error_message = "Please fill in the term name."

        elif "add_assessment" in request.form:
            assessment_name = request.form.get("assessment_name")
            if assessment_name:
                existing_assessment = AssessmentType.query.filter_by(name=assessment_name).first()
                if existing_assessment:
                    error_message = f"Assessment Type '{assessment_name}' already exists."
                else:
                    new_assessment = AssessmentType(name=assessment_name)
                    db.session.add(new_assessment)
                    db.session.commit()
                    success_message = f"Assessment Type '{assessment_name}' added successfully!"
            else:
                error_message = "Please fill in the assessment type name."

        elif "delete_term" in request.form:
            term_id = request.form.get("term_id")
            term = Term.query.get(term_id)
            if term:
                # Check if term is used in marks
                if term.marks:
                    error_message = "Cannot delete term with associated marks."
                else:
                    db.session.delete(term)
                    db.session.commit()
                    success_message = f"Term '{term.name}' deleted successfully!"
            else:
                error_message = "Term not found."

        elif "delete_assessment" in request.form:
            assessment_id = request.form.get("assessment_id")
            assessment = AssessmentType.query.get(assessment_id)
            if assessment:
                # Check if assessment type is used in marks
                if assessment.marks:
                    error_message = "Cannot delete assessment type with associated marks."
                else:
                    db.session.delete(assessment)
                    db.session.commit()
                    success_message = f"Assessment Type '{assessment.name}' deleted successfully!"
            else:
                error_message = "Assessment Type not found."

    terms = Term.query.all()
    assessment_types = AssessmentType.query.all()
    return render_template("manage_terms_assessments.html", terms=terms, assessment_types=assessment_types, error_message=error_message, success_message=success_message)

@app.route("/generate_pdf/<grade>/<stream>/<subject>")
def generate_pdf(grade, stream, subject):
    stream_obj = Stream.query.join(Grade).filter(Grade.level == grade, Stream.name == stream[-1]).first()
    subject_obj = Subject.query.filter_by(name=subject).first()
    if not (stream_obj and subject_obj):
        return "Invalid grade, stream, or subject", 404

    students = Student.query.filter_by(stream_id=stream_obj.id).all()
    marks_data = []
    total_marks = 0
    for student in students:
        mark = Mark.query.filter_by(student_id=student.id, subject_id=subject_obj.id).first()
        if mark:
            percentage = (mark.mark / mark.total_marks) * 100 if mark.total_marks > 0 else 0
            performance = get_performance_category(percentage)
            marks_data.append([student.name, mark.mark, round(percentage, 1), performance])
            total_marks = mark.total_marks

    if not marks_data:
        return "No data available for this report.", 404

    mean_score = sum(mark[1] for mark in marks_data) / len(marks_data) if marks_data else 0
    mean_percentage = (mean_score / total_marks) * 100 if total_marks > 0 else 0
    mean_performance = get_performance_category(mean_percentage)
    performance_summary = get_performance_summary(marks_data)

    pdf_file = f"report_{grade}_{stream}_{subject.replace(' ', '_')}.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']
    heading3_style = styles['Heading3']

    elements.append(Paragraph("Hill View School", title_style))
    elements.append(Paragraph(f"Grade {grade} Stream {stream} - {subject} Report", subtitle_style))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"Mean Score: {mean_score:.2f} ({mean_percentage:.1f}%) - {mean_performance}", normal_style))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Performance Summary:", heading3_style))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(f"E.E: {performance_summary.get('E.E', 0)} students", normal_style))
    elements.append(Paragraph(f"M.E: {performance_summary.get('M.E', 0)} students", normal_style))
    elements.append(Paragraph(f"A.E: {performance_summary.get('A.E', 0)} students", normal_style))
    elements.append(Paragraph(f"B.E: {performance_summary.get('B.E', 0)} students", normal_style))
    elements.append(Spacer(1, 24))

    data = [["Student Name", "Marks", "Percentage (%)", "Performance Level"]]
    for student_record in marks_data:
        data.append([
            student_record[0],
            str(student_record[1]),
            f"{student_record[2]}%",
            student_record[3]
        ])
    
    table = Table(data)
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]

    for i, row in enumerate(data[1:], start=1):
        performance = row[3]
        if performance == "E.E":
            table_style.append(('BACKGROUND', (3, i), (3, i), colors.green))
        elif performance == "M.E":
            table_style.append(('BACKGROUND', (3, i), (3, i), colors.lightblue))
        elif performance == "A.E":
            table_style.append(('BACKGROUND', (3, i), (3, i), colors.yellow))
        else:
            table_style.append(('BACKGROUND', (3, i), (3, i), colors.pink))

    table.setStyle(TableStyle(table_style))
    elements.append(table)

    elements.append(Spacer(1, 20))
    footer_style = styles['Normal']
    footer_style.alignment = 1
    elements.append(Paragraph("Hillview School powered by CbcTeachkit", footer_style))

    doc.build(elements)
    return send_file(pdf_file, as_attachment=True)

@app.route("/generate_class_pdf/<grade>/<stream>/<term>/<assessment_type>")
def generate_class_pdf(grade, stream, term, assessment_type):
    stream_obj = Stream.query.join(Grade).filter(Grade.level == grade, Stream.name == stream[-1]).first()
    term_obj = Term.query.filter_by(name=term).first()
    assessment_type_obj = AssessmentType.query.filter_by(name=assessment_type).first()
    
    if not (stream_obj and term_obj and assessment_type_obj):
        return "Invalid grade, stream, term, or assessment type", 404

    students = Student.query.filter_by(stream_id=stream_obj.id).all()
    subjects = Subject.query.all()
    class_data = []
    total_marks = 0

    for student in students:
        student_marks = {}
        for subject in subjects:
            mark = Mark.query.filter_by(
                student_id=student.id,
                subject_id=subject.id,
                term_id=term_obj.id,
                assessment_type_id=assessment_type_obj.id
            ).first()
            student_marks[subject.name] = mark.mark if mark else 0
            if mark:
                total_marks = mark.total_marks
        total = sum(student_marks.values())
        avg_percentage = (total / (len(subjects) * total_marks)) * 100 if total_marks > 0 else 0
        class_data.append({
            'student': student.name,
            'marks': student_marks,
            'total_marks': total,
            'average_percentage': avg_percentage
        })

    if not class_data:
        return "No data available for this report.", 404

    class_data.sort(key=lambda x: x['total_marks'], reverse=True)
    for i, student_data in enumerate(class_data, 1):
        student_data['rank'] = i

    stats = {'exceeding': 0, 'meeting': 0, 'approaching': 0, 'below': 0}
    for student_data in class_data:
        avg = student_data['average_percentage']
        if avg >= 75:
            stats['exceeding'] += 1
        elif 50 <= avg < 75:
            stats['meeting'] += 1
        elif 30 <= avg < 50:
            stats['approaching'] += 1
        else:
            stats['below'] += 1

    pdf_file = f"class_report_{grade}_{stream}_{term}_{assessment_type}.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=landscape(letter))
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']
    heading3_style = styles['Heading3']

    subject_abbreviations = {
        "Mathematics": "MATH",
        "English": "ENG",
        "Kiswahili": "KISW",
        "Integrated Science and Health Education": "ISHE",
        "Agriculture": "AGR",
        "Pre-Technical Studies": "PTS",
        "Visual Arts": "VA",
        "Religious Education": "RE",
        "Social Studies": "SS"
    }

    abbreviated_subjects = [subject_abbreviations.get(subject.name, subject.name[:4].upper()) for subject in subjects]

    title_style.alignment = 1
    subtitle_style.alignment = 1
    elements.append(Paragraph("HILL VIEW SCHOOL", title_style))
    elements.append(Paragraph(f"GRADE {grade} - MARKSHEET: AVERAGE SCORE", subtitle_style))
    elements.append(Paragraph(f"STREAM: {stream}  TERM: {term.replace('_', ' ').upper()}  ASSESSMENT: {assessment_type.upper()}", subtitle_style))
    elements.append(Spacer(1, 12))

    headers = ["S/N", "STUDENT NAME"] + abbreviated_subjects + ["TOTAL", "AVG %", "GRD", "RANK"]
    data = [headers]
    for idx, student_data in enumerate(class_data, 1):
        row = [str(idx), student_data['student'].upper()]
        for subject in subjects:
            mark = student_data['marks'].get(subject.name, 0)
            row.append(str(int(mark)))
        total = student_data['total_marks']
        avg_percentage = student_data['average_percentage']
        grade = get_performance_category(avg_percentage)
        row.extend([str(int(total)), f"{avg_percentage:.0f}%", grade, str(student_data['rank'])])
        data.append(row)
    
    table = Table(data)
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]

    col_widths = [30, 150] + [40] * len(abbreviated_subjects) + [50, 50, 40, 40]
    table._argW = col_widths

    table.setStyle(TableStyle(table_style))
    elements.append(table)

    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Performance Summary:", heading3_style))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(f"E.E (Exceeding Expectation, ≥75%): {stats.get('exceeding', 0)} learners", normal_style))
    elements.append(Paragraph(f"M.E (Meeting Expectation, 50-74%): {stats.get('meeting', 0)} learners", normal_style))
    elements.append(Paragraph(f"A.E (Approaching Expectation, 30-49%): {stats.get('approaching', 0)} learners", normal_style))
    elements.append(Paragraph(f"B.E (Below Expectation, <30%): {stats.get('below', 0)} learners", normal_style))

    elements.append(Spacer(1, 20))
    footer_style = styles['Normal']
    footer_style.alignment = 1
    footer_style.fontSize = 8
    current_date = datetime.now().strftime("%Y-%m-%d")
    elements.append(Paragraph(f"Generated on: {current_date}", footer_style))
    elements.append(Paragraph("Hillview School powered by CbcTeachkit", footer_style))

    doc.build(elements)
    return send_file(pdf_file, as_attachment=True)

@app.route("/preview_class_report/<grade>/<stream>/<term>/<assessment_type>")
def preview_class_report(grade, stream, term, assessment_type):
    stream_obj = Stream.query.join(Grade).filter(Grade.level == grade, Stream.name == stream[-1]).first()
    term_obj = Term.query.filter_by(name=term).first()
    assessment_type_obj = AssessmentType.query.filter_by(name=assessment_type).first()
    
    if not (stream_obj and term_obj and assessment_type_obj):
        return "Invalid grade, stream, term, or assessment type", 404

    students = Student.query.filter_by(stream_id=stream_obj.id).all()
    subjects = Subject.query.all()
    class_data = []
    total_marks = 0

    for student in students:
        student_marks = {}
        for subject in subjects:
            mark = Mark.query.filter_by(
                student_id=student.id,
                subject_id=subject.id,
                term_id=term_obj.id,
                assessment_type_id=assessment_type_obj.id
            ).first()
            student_marks[subject.name] = mark.mark if mark else 0
            if mark:
                total_marks = mark.total_marks
        total = sum(student_marks.values())
        avg_percentage = (total / (len(subjects) * total_marks)) * 100 if total_marks > 0 else 0
        class_data.append({
            'student': student.name,
            'marks': student_marks,
            'total_marks': total,
            'average_percentage': avg_percentage
        })

    if not class_data:
        return "No data available for this report.", 404

    class_data.sort(key=lambda x: x['total_marks'], reverse=True)
    indexed_class_data = []
    for idx, student_data in enumerate(class_data, 1):
        student_data_copy = student_data.copy()
        student_data_copy['index'] = idx
        student_data_copy['performance_category'] = get_performance_category(student_data['average_percentage'])
        student_data_copy['rank'] = idx
        indexed_class_data.append(student_data_copy)

    stats = {'exceeding': 0, 'meeting': 0, 'approaching': 0, 'below': 0}
    for student_data in class_data:
        avg = student_data['average_percentage']
        if avg >= 75:
            stats['exceeding'] += 1
        elif 50 <= avg < 75:
            stats['meeting'] += 1
        elif 30 <= avg < 50:
            stats['approaching'] += 1
        else:
            stats['below'] += 1

    subject_abbreviations = {
        "Mathematics": "MATH",
        "English": "ENG",
        "Kiswahili": "KISW",
        "Integrated Science and Health Education": "ISHE",
        "Agriculture": "AGR",
        "Pre-Technical Studies": "PTS",
        "Visual Arts": "VA",
        "Religious Education": "RE",
        "Social Studies": "SS"
    }

    abbreviated_subjects = [subject_abbreviations.get(subject.name, subject.name[:4].upper()) for subject in subjects]

    return render_template(
        "preview_class_report.html",
        class_data=indexed_class_data,
        stats=stats,
        education_level="",
        grade=grade,
        stream=stream,
        term=term,
        assessment_type=assessment_type,
        total_marks=total_marks,
        subjects=[subject.name for subject in subjects],
        abbreviated_subjects=abbreviated_subjects,
        current_date=datetime.now().strftime("%Y-%m-%d")
    )

@app.route("/preview_individual_report/<grade>/<stream>/<term>/<assessment_type>/<student_name>")
def preview_individual_report(grade, stream, term, assessment_type, student_name):
    stream_obj = Stream.query.join(Grade).filter(Grade.level == grade, Stream.name == stream[-1]).first()
    term_obj = Term.query.filter_by(name=term).first()
    assessment_type_obj = AssessmentType.query.filter_by(name=assessment_type).first()
    
    if not (stream_obj and term_obj and assessment_type_obj):
        return "Invalid grade, stream, term, or assessment type", 404

    student = Student.query.filter_by(name=student_name, stream_id=stream_obj.id).first()
    if not student:
        return f"No data available for student {student_name}.", 404

    subjects = Subject.query.all()
    student_marks = {}
    total_marks = 0
    for subject in subjects:
        mark = Mark.query.filter_by(
            student_id=student.id,
            subject_id=subject.id,
            term_id=term_obj.id,
            assessment_type_id=assessment_type_obj.id
        ).first()
        student_marks[subject.name] = mark.mark if mark else 0
        if mark:
            total_marks = mark.total_marks

    total = sum(student_marks.values())
    avg_percentage = (total / (len(subjects) * total_marks)) * 100 if total_marks > 0 else 0
    mean_grade, mean_points = get_grade_and_points(avg_percentage)
    total_possible_marks = len(subjects) * total_marks
    total_points = sum(get_grade_and_points(student_marks.get(subject.name, 0))[1] for subject in subjects)

    table_data = []
    for subject in subjects:
        mark = student_marks.get(subject.name, 0)
        avg = mark
        percentage = (mark / total_marks) * 100 if total_marks > 0 else 0
        performance = get_performance_category(percentage)
        table_data.append({
            'subject': subject.name.upper(),
            'entrance': "",
            'mid_term': "",
            'end_term': int(mark),
            'avg': int(avg),
            'remarks': f"{performance}"
        })

    return render_template(
        "preview_individual_report.html",
        student_data={'student': student_name, 'marks': student_marks, 'total_marks': total, 'average_percentage': avg_percentage},
        education_level="",
        grade=grade,
        stream=stream,
        term=term,
        assessment_type=assessment_type,
        total_marks=total_marks,
        subjects=[subject.name for subject in subjects],
        total=total,
        avg_percentage=avg_percentage,
        mean_grade=mean_grade,
        mean_points=mean_points,
        total_possible_marks=total_possible_marks,
        total_points=total_points,
        table_data=table_data,
        admission_no=f"HS{grade}{stream[-1]}{str(Student.query.filter_by(stream_id=stream_obj.id).all().index(student) + 1).zfill(3)}",
        current_date=datetime.now().strftime("%Y-%m-%d")
    )

@app.route("/generate_all_individual_reports/<grade>/<stream>/<term>/<assessment_type>")
def generate_all_individual_reports(grade, stream, term, assessment_type):
    stream_obj = Stream.query.join(Grade).filter(Grade.level == grade, Stream.name == stream[-1]).first()
    term_obj = Term.query.filter_by(name=term).first()
    assessment_type_obj = AssessmentType.query.filter_by(name=assessment_type).first()
    
    if not (stream_obj and term_obj and assessment_type_obj):
        return "Invalid grade, stream, term, or assessment type", 404

    students = Student.query.filter_by(stream_id=stream_obj.id).all()
    subjects = Subject.query.all()
    class_data = []
    total_marks = 0

    for student in students:
        student_marks = {}
        for subject in subjects:
            mark = Mark.query.filter_by(
                student_id=student.id,
                subject_id=subject.id,
                term_id=term_obj.id,
                assessment_type_id=assessment_type_obj.id
            ).first()
            student_marks[subject.name] = mark.mark if mark else 0
            if mark:
                total_marks = mark.total_marks
        total = sum(student_marks.values())
        avg_percentage = (total / (len(subjects) * total_marks)) * 100 if total_marks > 0 else 0
        class_data.append({
            'student': student.name,
            'marks': student_marks,
            'total_marks': total,
            'average_percentage': avg_percentage
        })

    if not class_data:
        return "No student data available for this class.", 404

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for student_data in class_data:
            student_name = student_data['student']
            pdf_file = generate_individual_report_pdf(
                grade, stream, term, assessment_type, student_name,
                class_data, "", total_marks, [subject.name for subject in subjects]
            )
            if pdf_file and os.path.exists(pdf_file):
                zip_file.write(pdf_file, os.path.basename(pdf_file))
                os.remove(pdf_file)

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f"individual_reports_{grade}_{stream}_{term}_{assessment_type}.zip"
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)