from turtle import update
from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Regexp, Length
from wtforms.fields import FileField
from flask_sqlalchemy import SQLAlchemy
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_migrate import Migrate
from flask_mysqldb import MySQL
from sqlalchemy.exc import IntegrityError
import cloudinary
import cloudinary.uploader
from config import CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET, CLOUDINARY_CLOUD_NAME, SQLALCHEMY_DATABASE_URI, SECRET_KEY
from dotenv import load_dotenv

load_dotenv('.env')

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']

app = Flask(__name__, template_folder='templates',
            instance_relative_config=True)
app.config.from_mapping(SECRET_KEY=SECRET_KEY,
                        SQLALCHEMY_DATABASE_URI=SQLALCHEMY_DATABASE_URI)
mysql = MySQL(app)

cloudinary.config(
    CLOUDINARY_CLOUD_NAME=CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY=CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET=CLOUDINARY_API_SECRET
)


db = SQLAlchemy(app)
migrate = Migrate(app, db)

# College Table


class Colleges(db.Model):
    college_code = db.Column(
        db.String(150), primary_key=True)
    college_name = db.Column(db.String(150), unique=True)
    av_courses = db.relationship(
        'Courses', backref='colleges')

# College ComboBox
    def __repr__(self):
        return '{}'.format(self.college_code)


def college_choice_query():
    return Colleges.query
# Course Table


class Courses(db.Model):
    course_name = db.Column(db.String(150))
    course_code = db.Column(db.String(150), primary_key=True)
    resp_college = db.Column(db.String(150), db.ForeignKey(
        'colleges.college_code', ondelete='SET NULL', onupdate='cascade'), nullable=True)
    students = db.relationship(
        'Student', backref='courses')

    def __repr__(self):
        return '{}'.format(self.course_code)


def course_choice_query():
    return Courses.query

# Student Table


class Student(db.Model):
    id = db.Column(db.String(9), primary_key=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    year_lvl = db.Column(db.String(150))
    gender = db.Column(db.String(150))
    course = db.Column(db.String(150), db.ForeignKey(
        'courses.course_code', ondelete='SET NULL', onupdate='cascade'), nullable=True)
    profile_pic = db.Column(db.String(5000), nullable=True)


class add_student_form(FlaskForm):
    IDNumber = StringField("ID Number: ", validators=[
                           DataRequired(), Regexp('[0-9]+-\d\d\d\d', message="The format must be '[0-9]+-\d\d\d\d'"), Length(min=9, max=9, message='Must be exactly 9 characters!')])
    first_name = StringField("First Name: ", validators=[DataRequired()])
    last_name = StringField("Last Name: ", validators=[DataRequired()])
    course = QuerySelectField("Course: ",
                              query_factory=course_choice_query, allow_blank=False, get_label='course_code')
    year_level = SelectField("Year Level: ", coerce=str, choices=[
        ("1st Year", "1st Year"), ("2nd Year", "2nd Year"), ("3rd Year", "3rd Year"), ("4th Year", "4th Year")], validators=[DataRequired()])
    gender = SelectField('Gender:', choices=[
                        ('M', 'M'), ('F', 'F'), ('Other', 'Other')], validators=[DataRequired()])
    profile_pic = FileField("Student's Profile Picture: ")
    submit = SubmitField("Add Student")


class delete_student_form(FlaskForm):
    IDNumber_del = StringField("ID Number: ", validators=[
        DataRequired(), Regexp('[0-9]+-\d\d\d\d', message="The format must be '[0-9]+-\d\d\d\d'"), Length(min=9, max=9, message='Must be exactly 9 characters!')])
    submit = SubmitField("Delete Student")


class update_student_form(FlaskForm):
    upd_IDNumber = StringField("ID Number: ", validators=[
        DataRequired(), Regexp('[0-9]+-\d\d\d\d', message="The format must be '[0-9]+-\d\d\d\d'"), Length(min=9, max=9, message='Must be exactly 9 characters!')])
    upd_first_name = StringField("First Name: ", validators=[DataRequired()])
    upd_last_name = StringField("Last Name: ", validators=[DataRequired()])
    upd_course = QuerySelectField("Course: ",
                                  query_factory=course_choice_query, allow_blank=False, get_label='course_code')
    upd_year_level = SelectField("Year Level: ", coerce=str, choices=[
        ("1st Year", "1st Year"), ("2nd Year", "2nd Year"), ("3rd Year", "3rd Year"), ("4th Year", "4th Year")], validators=[DataRequired()])
    upd_gender = SelectField('Gender:', choices=[
        ('M', 'M'), ('F', 'F'), ('Other', 'Other')], validators=[DataRequired()])
    profile_pic = FileField("Student's Profile Picture: ")
    submit = SubmitField("Update Student")


class add_courses_form(FlaskForm):
    course_code = StringField("Course Code:", validators=[DataRequired()])
    course_name = StringField("Course Name:", validators=[
                              DataRequired(), Length(min=7, max=64)])
    resp_college = QuerySelectField("On which college will this course belong to?",
                                    query_factory=college_choice_query, allow_blank=False, get_label='college_code', render_kw={'style': 'width: 20ch'})
    submit = SubmitField("Add Course")


class delete_courses_form(FlaskForm):
    course_code_del = StringField("Course Code: ", validators=[DataRequired()])
    submit = SubmitField("Delete Course")


class update_courses_form(FlaskForm):
    new_course_name = StringField(
        "Update Course Name:", validators=[DataRequired(), Length(min=7, max=64)])
    new_course_code = StringField(
        "Update Course Code:", validators=[DataRequired()])
    new_resp_college = QuerySelectField("On which college will this course belong to?",
                                        query_factory=college_choice_query, allow_blank=False, get_label='college_code', render_kw={'style': 'width: 20ch'})
    submit = SubmitField("Update Course")


@app.route('/test1/<course_code>', methods=['GET', 'POST'])
def test1(course_code):
    updated_courses = Courses.query.order_by(Courses.course_code)
    form = update_courses_form()
    course_code_to_update = Courses.query.get_or_404(course_code)
    if request.method == 'POST':
        course_code_to_update.course_name = request.form['new_course_name']
        course_code_to_update.course_code = request.form['new_course_code']
        course_code_to_update.resp_college = request.form['new_resp_college']
        try:
            db.session.commit()
            flash("Course Updated Successfully!")
            return render_template("test1.html", updated_courses=updated_courses, form=form, course_code_to_update=course_code_to_update)
        except IntegrityError:
            db.session.rollback()
            flash("Course Update Failed!")
            return render_template("test1.html", updated_courses=updated_courses, form=form, course_code_to_update=course_code_to_update)
    else:
        return render_template("test1.html", updated_courses=updated_courses, form=form, course_code_to_update=course_code_to_update)


class add_college_form(FlaskForm):
    college_name = StringField("College Name: ", validators=[
                               DataRequired(), Length(min=7, max=64)])
    college_code = StringField("College Code: ", validators=[DataRequired()])
    submit = SubmitField("Add College")


class delete_college_form(FlaskForm):
    college_code_del = StringField(
        "College Code to delete: ", validators=[DataRequired()])
    submit = SubmitField("Delete College")


class update_college_form(FlaskForm):
    new_college_name = StringField(
        "Update College Name:", validators=[DataRequired(), Length(min=7, max=64)])
    new_college_code = StringField(
        "Update College Code:", validators=[DataRequired()])
    submit = SubmitField("Update College")


@app.route('/test/<college_code>', methods=['GET', 'POST'])
def test(college_code):
    updated_college = Colleges.query.order_by(Colleges.college_code)
    form = update_college_form()
    college_name_to_update = Colleges.query.get_or_404(college_code)
    if request.method == 'POST':
        college_name_to_update.college_name = request.form['new_college_name']
        college_name_to_update.college_code = request.form['new_college_code']
        try:
            db.session.commit()
            flash("College Updated Successfully!")
            return render_template("test.html", updated_college=updated_college, form=form, college_name_to_update=college_name_to_update)
        except IntegrityError:
            db.session.rollback()
            flash("College Update Failed! College code already exists!")
            return render_template("test.html", updated_college=updated_college, form=form, college_name_to_update=college_name_to_update)
    else:
        return render_template("test.html", updated_college=updated_college, form=form, college_name_to_update=college_name_to_update)


@app.route('/test2/<id>', methods=['GET', 'POST'])
def test2(id):
    updated_student = Student.query.order_by(Student.last_name)
    form = update_student_form()
    profile_pic = form.profile_pic.data
    student_record_to_update = Student.query.get_or_404(id)
    if form.validate_on_submit():
        student_record_to_update.id = request.form['upd_IDNumber']
        student_record_to_update.first_name = request.form['upd_first_name']
        student_record_to_update.last_name = request.form['upd_last_name']
        student_record_to_update.course = request.form['upd_course']
        student_record_to_update.year_lvl = request.form['upd_year_level']
        student_record_to_update.gender = request.form['upd_gender']
        try:
            if profile_pic and profile_pic.filename.split(".")[-1].lower() in ALLOWED_EXTENSIONS:
                upload_result = cloudinary.uploader.upload(
                    profile_pic, folder="SIS")
                student_record_to_update.profile_pic = upload_result['secure_url']
                db.session.commit()
                flash("Student Info Updated Successfully!")
                return render_template("test2.html", updated_student=updated_student, form=form, student_record_to_update=student_record_to_update)
            else:
                db.session.commit()
                flash("Student Info Updated Successfully!")
                return render_template("test2.html", updated_student=updated_student, form=form, student_record_to_update=student_record_to_update)
        except IntegrityError:
            db.session.rollback()
            flash("Student Info Update Failed!")
            return render_template("test2.html", updated_student=updated_student, form=form, student_record_to_update=student_record_to_update)
    else:
        flash("Make sure to write the ID in YYYY-NNNN format")
        return render_template("test2.html", updated_student=updated_student, form=form, student_record_to_update=student_record_to_update)


@app.route('/')
def home():
    student_table = Student.query.order_by(Student.id)
    course_table = Courses.query.order_by(Courses.course_code)
    college_table = Colleges.query.order_by(Colleges.college_code)
    return render_template("home.html", student_table=student_table, course_table=course_table, college_table=college_table)


@app.route('/add-student', methods=['GET', 'POST'])
def add_student():
    IDNumber = None
    first_name = None
    last_name = None
    course = None
    year_level = None
    gender = None
    form = add_student_form()
    add_student = Student.query.order_by(Student.last_name)
    profile_pic = form.profile_pic.data
    if form.validate_on_submit():
        some_variable = Student.query.filter_by(
            id=form.IDNumber.data).first()
        try:
            if profile_pic and profile_pic.filename.split(".")[-1].lower() in ALLOWED_EXTENSIONS:
                upload_result = cloudinary.uploader.upload(
                    profile_pic, folder="SIS")
                some_variable = Student(id=form.IDNumber.data, first_name=form.first_name.data,
                                        last_name=form.last_name.data, course=form.course.data, year_lvl=form.year_level.data, gender=form.gender.data, profile_pic=upload_result['secure_url'])
                db.session.add(some_variable)
                db.session.commit()
                flash("Data Added Successfully!")
            else:
                some_variable = Student(id=form.IDNumber.data, first_name=form.first_name.data,
                                        last_name=form.last_name.data, course=form.course.data, year_lvl=form.year_level.data, gender=form.gender.data)
                db.session.add(some_variable)
                db.session.commit()
                flash("Data Added Successfully!")
        except IntegrityError:
            db.session.rollback()
            flash("Student already exists!")
            return render_template("add-student.html", add_student=add_student, IDNumber=IDNumber, first_name=first_name, last_name=last_name, course=course, year_level=year_level, gender=gender, form=form)
        form.IDNumber.data = ''
        form.first_name.data = ''
        form.last_name.data = ''
        form.course.data = ''
        form.year_level.data = ''
        form.gender.data = ''
    else:
        flash("Make sure to write the ID in YYYY-NNNN format")
    return render_template("add-student.html", add_student=add_student, IDNumber=IDNumber, first_name=first_name, last_name=last_name, course=course, year_level=year_level, gender=gender, form=form)


@app.route('/delete-student', methods=['GET', 'POST'])
def delete_student():
    IDNumber_del = None
    form = delete_student_form()
    if form.validate_on_submit():
        some_variable = Student.query.filter_by(
            id=form.IDNumber_del.data).first()
        if some_variable:
            db.session.delete(some_variable)
            db.session.commit()
        IDNumber_del = form.IDNumber_del.data
        form.IDNumber_del.data = ''
        flash("Student Record Removed Successfully!")
    deleted_student = Student.query.order_by(Student.id)
    return render_template("delete-student.html", IDNumber_del=IDNumber_del, deleted_student=deleted_student, form=form)


@app.route('/update-student')
def update_student():
    updated_student = Student.query.order_by(Student.last_name)
    return render_template("update-student.html", updated_student=updated_student)


@app.route('/add-courses', methods=['GET', 'POST'])
def add_courses():
    course_code = None
    course_name = None
    form = add_courses_form()
    add_course = Courses.query.order_by(Courses.resp_college)
    if form.validate_on_submit():
        some_variable = Courses.query.filter_by(
            course_code=form.course_code.data).first()
        try:
            some_variable = Courses(course_name=form.course_name.data,
                                    course_code=form.course_code.data, resp_college=form.resp_college.data)
            db.session.add(some_variable)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Course code already exists!")
            return render_template("add-courses.html", course_name=course_name, add_course=add_course, form=form)
        form.course_name.data = ''
        form.course_code.data = ''
        form.resp_college.data = ''
    flash("Course added!")
    return render_template("add-courses.html", course_name=course_name, add_course=add_course, form=form)


@app.route('/delete-courses', methods=['GET', 'POST'])
def delete_courses():
    course_code_del = None
    form = delete_courses_form()
    if form.validate_on_submit():
        some_variable = Courses.query.filter_by(
            course_code=form.course_code_del.data).first()
        if some_variable:
            db.session.delete(some_variable)
            db.session.commit()
        course_code_del = form.course_code_del.data
        form.course_code_del.data = ''
        flash("Course Removed Successfully!")
    del_course = Courses.query.order_by(Courses.course_code)
    return render_template('delete-courses.html', course_code_del=course_code_del, del_course=del_course, form=form)


@app.route('/update-courses')
def update_courses():
    updated_courses = Courses.query.order_by(Courses.course_code)
    return render_template("update-courses.html", updated_courses=updated_courses)


@app.route('/add-colleges', methods=['GET', 'POST'])
def add_colleges():
    college_name = None
    form = add_college_form()
    add_college = Colleges.query.order_by(Colleges.college_code)
    if form.validate_on_submit():
        some_variable = Colleges.query.filter_by(
            college_code=form.college_code.data).first()
        try:
            some_variable = Colleges(
                college_name=form.college_name.data, college_code=form.college_code.data)
            db.session.add(some_variable)
            db.session.commit()
            flash("College Added Successfully!")
        except IntegrityError:
            db.session.rollback()
            flash("College already exists!")
            return render_template("add-colleges.html", college_name=college_name, form=form, add_college=add_college)
        college_name = form.college_name.data
        form.college_name.data = ''
        form.college_code.data = ''
    return render_template("add-colleges.html", college_name=college_name, form=form, add_college=add_college)


@app.route('/delete-colleges', methods=['GET', 'POST'])
def delete_colleges():
    college_code_del = None
    form = delete_college_form()
    if form.validate_on_submit():
        some_variable = Colleges.query.filter_by(
            college_code=form.college_code_del.data).first()
        if some_variable:
            db.session.delete(some_variable)
            db.session.commit()
        form.college_code_del.data = ''
        flash("College Removed Successfully!")
    del_college = Colleges.query.order_by(Colleges.college_code)
    return render_template('delete-colleges.html', college_code_del=college_code_del, del_college=del_college, form=form)


@app.route('/update-colleges')
def update_colleges():
    updated_college = Colleges.query.order_by(Colleges.college_code)
    return render_template("update-colleges.html", updated_college=updated_college)
