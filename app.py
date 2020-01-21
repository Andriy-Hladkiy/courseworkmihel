from random import randint

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sklearn.compose import ColumnTransformer
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sqlalchemy import create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.attributes import InstrumentedAttribute
import numpy as np

from forms.form import StudentValidForm, LaboratoryValidForm, RequirementsValidForm, studentRequirementsDoneForm, \
    laboratoryRequirementsForm, AIForm
from dao.dto import StudentRequirementDTO, LaboratoryRequirementDTO

app = Flask(__name__)
app.secret_key = 'key'
db_string = 'postgresql://postgres:changeme123@localhost/Course'
engine = create_engine(db_string)
Session = sessionmaker(bind=engine)
Base = declarative_base()
metadata = Base.metadata
session = Session()
ENV = 'dev'
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = db_string
else:
    app.debug = False
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = 'postgres://fhehffwmvlzkku:e4e9539062e2cd4765550e4ad36e835e630b2d4b442504998f870733d03df2a0@ec2-79-125-2-142.eu-west-1.compute.amazonaws.com:5432/d1jhdnlc95ioeq'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class ormStudent(db.Model):
    __tablename__ = 'Student'

    student_recordbook = db.Column(db.String(10), primary_key=True)
    student_name = db.Column(db.String(50), nullable=False)
    student_surname = db.Column(db.String(50), nullable=False)
    student_groupe = db.Column(db.String(10), nullable=False)
    student_faculty = db.Column(db.String(50), nullable=False)
    student_is_worker = db.Column(db.String(50), nullable=False)
    student_time_work = db.Column(db.Integer, nullable=False)
    requirement_name = db.Column(db.String(50), nullable=False)


class ormLaboratory(db.Model):
    __tablename__ = 'Laboratory'

    laboratory_name = db.Column(db.String(50), primary_key=True)
    laboratory_subject = db.Column(db.String(50), nullable=False)
    laboratory_mark = db.Column(db.Integer, nullable=False)


class ormRequirement(db.Model):
    __tablename__ = 'Requirement'

    requirement_name = db.Column(db.String(20), primary_key=True)
    requirement_point = db.Column(db.Integer, nullable=False)


class ormStudentRequirementsDone(db.Model):
    __tablename__ = 'StudentRequirementsDone'

    ukey = db.Column(db.Integer, primary_key=True)
    student_recordbook = db.Column(db.String(10),
                                   db.ForeignKey('Student.student_recordbook', ondelete="CASCADE", onupdate="CASCADE"))
    requirement_name = db.Column(db.String(20),
                                 db.ForeignKey('Requirement.requirement_name', ondelete="CASCADE", onupdate="CASCADE"))

    def __init__(self, ukey: object, student_recordbook: object, requirement_name: object) -> object:
        self.ukey = ukey
        self.student_recordbook = student_recordbook
        self.requirement_name = requirement_name


class ormLaboratoryRequirements(db.Model):
    __tablename__ = 'LaboratoryRequirements'

    ukey = db.Column(db.Integer, primary_key=True)
    laboratory_name = db.Column(db.String(50),
                                db.ForeignKey('Laboratory.laboratory_name', ondelete="CASCADE", onupdate="CASCADE"))
    requirement_name = db.Column(db.String(50),
                                 db.ForeignKey('Requirement.requirement_name', ondelete="CASCADE", onupdate="CASCADE"))
    requirement_point = db.Column(db.Integer)

    def __init__(self, ukey: object, laboratory_name: object, requirement_name: object,
                 requirement_point: object) -> object:
        self.ukey = ukey
        self.laboratory_name = laboratory_name
        self.requirement_name = requirement_name
        self.requirement_point = requirement_point


db.create_all()

session.query(ormStudent).delete()
session.query(ormLaboratory).delete()
session.query(ormRequirement).delete()
session.query(ormStudentRequirementsDone).delete()

Student1 = ormStudent(student_recordbook='km-6207',
                      student_name='Michael',
                      student_surname='Evlentiev',
                      student_groupe='km-62',
                      student_faculty='PMA',
                      student_is_worker='true',
                      student_time_work=1,
                      requirement_name='use react')
Student2 = ormStudent(student_recordbook='km-6211',
                      student_name='Ivan',
                      student_surname='Ivanov',
                      student_groupe='km-62',
                      student_faculty='PMA',
                      student_is_worker='true',
                      student_time_work=2,
                      requirement_name='use css')
Student3 = ormStudent(student_recordbook='km-6222',
                      student_name='Petro',
                      student_surname='Petrov',
                      student_groupe='km-62',
                      student_faculty='PMA',
                      student_is_worker='false',
                      student_time_work=2,
                      requirement_name='use html5')
Laboratory1 = ormLaboratory(laboratory_name='React-basic',
                            laboratory_subject='web',
                            laboratory_mark=5)
Laboratory2 = ormLaboratory(laboratory_name='function in js',
                            laboratory_subject='web',
                            laboratory_mark=5)
Laboratory3 = ormLaboratory(laboratory_name='closing',
                            laboratory_subject='web',
                            laboratory_mark=5)
Requirement1 = ormRequirement(requirement_name='use react',
                              requirement_point=1)
Requirement2 = ormRequirement(requirement_name='use css',
                              requirement_point=1)
Requirement3 = ormRequirement(requirement_name='use html5',
                              requirement_point=1)
session.add_all([Student1, Student2, Student3])
session.add_all([Laboratory1, Laboratory2, Laboratory3])
session.add_all([Requirement1, Requirement2, Requirement3])
session.commit()


# main page
@app.route('/', methods=['GET', 'POST'])
def root():
    return render_template('index.html')


# student page
@app.route('/student', methods=['GET'])
def students():
    student_list = session.query(ormStudent).all()

    return render_template('student/student_page.html', student_list=student_list)


# student delete
@app.route('/remove-student/<string:current_student>', methods=['GET', 'POST'])
def remove_student(current_student):
    remove_event = session.query(ormStudent).filter(ormStudent.student_recordbook == current_student).one()

    session.delete(remove_event)
    session.commit()

    return redirect('/student')


# student edit
@app.route('/edit_student_info/<string:current_student>', methods=['GET', 'POST'])
def edit_student(current_student):
    student = session.query(ormStudent).filter(ormStudent.student_recordbook == current_student).one()
    form = StudentValidForm()

    if request.method == 'GET':

        form.student_recordbook.data = student.student_recordbook
        form.student_name.data = student.student_name
        form.student_surname.data = student.student_surname
        form.student_groupe.data = student.student_groupe
        form.student_faculty.data = student.student_faculty

        return render_template('student/student_edit_page.html', form=form, form_name="Edit student")

    else:

        if form.validate():
            student.student_recordbook = form.student_recordbook.data
            student.student_name = form.student_name.data
            student.student_surname = form.student_surname.data
            student.student_groupe = form.student_groupe.data
            student.student_faculty = form.student_faculty.data

            try:
                session.commit()
                return redirect('/student')
            except:
                form.student_recordbook.errors = ['Student with this record book already exists!']
                return render_template('student/student_edit_page.html', form=form, form_name="Edit student")

        else:
            return render_template('student/student_edit_page.html', form=form, form_name="Edit student")


# add student
@app.route('/add_student', methods=['POST', 'GET'])
def add_student():
    form = StudentValidForm()

    if request.method == 'GET':
        return render_template('student/add_student.html', form=form, form_name="add student form")
    else:
        if form.validate():
            new_student = ormStudent(
                student_recordbook=form.student_recordbook.data,
                student_name=form.student_name.data,
                student_surname=form.student_surname.data,
                student_groupe=form.student_groupe.data,
                student_faculty=form.student_faculty.data)

            try:
                session.add(new_student)
                session.commit()
                return redirect('/student')
            except:
                form.student_recordbook.errors = ['Student with this record book already exists!']
                return render_template('student/add_student.html', form=form, form_name="add student form")

        else:
            return render_template('student/add_student.html', form=form, form_name="add student form")


# laboratory page
@app.route('/laboratory', methods=['GET'])
def laboratories():
    laboratory_list = session.query(ormLaboratory).all()

    return render_template('laboratory/laboratory_page.html', laboratory_list=laboratory_list)


# laboratory delete
@app.route('/remove-laboratory/<string:current_laboratory>', methods=['GET', 'POST'])
def remove_laboratory(current_laboratory):
    remove_event = session.query(ormLaboratory).filter(ormLaboratory.laboratory_name == current_laboratory).one()

    session.delete(remove_event)
    session.commit()

    return redirect('/laboratory')


# laboratory edit
@app.route('/edit_laboratory_info/<string:current_laboratory>', methods=['GET', 'POST'])
def edit_laboratory(current_laboratory):
    laboratory = session.query(ormLaboratory).filter(ormLaboratory.laboratory_name == current_laboratory).one()
    form = LaboratoryValidForm()

    if request.method == 'GET':

        form.laboratory_name.data = laboratory.laboratory_name
        form.laboratory_subject.data = laboratory.laboratory_subject
        form.laboratory_mark.data = laboratory.laboratory_mark

        return render_template('laboratory/laboratory_edit_page.html', form=form, form_name="Edit laboratory")

    else:

        if form.validate():
            laboratory.laboratory_name = form.laboratory_name.data
            laboratory.laboratory_subject = form.laboratory_subject.data
            laboratory.laboratory_mark = form.laboratory_mark.data

            try:
                session.commit()
                return redirect('/laboratory')
            except:
                form.laboratory_name.errors = ['Laboratory with this name already exists!']
                return render_template('laboratory/laboratory_edit_page.html', form=form, form_name="Edit laboratory")

        else:
            return render_template('laboratory/laboratory_edit_page.html', form=form, form_name="Edit laboratory")


# add laboratory
@app.route('/add_laboratory', methods=['POST', 'GET'])
def add_laboratory():
    form = LaboratoryValidForm()

    if request.method == 'GET':
        return render_template('laboratory/add_laboratory.html', form=form, form_name="add laboratory form")
    else:
        if form.validate():
            new_lab = ormLaboratory(
                laboratory_name=form.laboratory_name.data,
                laboratory_subject=form.laboratory_subject.data,
                laboratory_mark=form.laboratory_mark.data)

            try:
                session.add(new_lab)
                session.commit()
                return redirect('/laboratory')
            except:
                form.laboratory_name.errors = ['Laboratory with this name already exists!']
                return render_template('laboratory/add_laboratory.html', form=form, form_name="add laboratory form")

        else:
            return render_template('laboratory/add_laboratory.html', form=form, form_name="add laboratory form")


# requirement page
@app.route('/requirement', methods=['GET'])
def requirement():
    requirement_list = session.query(ormRequirement).all()

    return render_template('requirement/requirement.html', requirement_list=requirement_list)


# requirement delete
@app.route('/remove-requirement/<string:current_requirement>', methods=['GET', 'POST'])
def remove_requirement(current_requirement):
    remove_event = session.query(ormRequirement).filter(ormRequirement.requirement_name == current_requirement).one()

    session.delete(remove_event)
    session.commit()

    return redirect('/requirement')


# requirement edit
@app.route('/edit_requirement_info/<string:current_requirement>', methods=['GET', 'POST'])
def edit_requirement(current_requirement):
    requirements = session.query(ormRequirement).filter(ormRequirement.requirement_name == current_requirement).one()
    form = RequirementsValidForm()

    if request.method == 'GET':

        form.requirement_name.data = requirements.requirement_name
        form.requirement_point.data = requirements.requirement_point

        return render_template('requirement/requirement_edit_page.html', form=form, form_name="Edit requirement")

    else:

        if form.validate():
            requirements.requirement_name = form.requirement_name.data
            requirements.requirement_point = form.requirement_point.data

            try:
                session.commit()
                return redirect('/requirement')
            except:
                form.requirement_name.errors = ['Requirement with this name already exists!']
                return render_template('requirement/requirement_edit_page.html', form=form,
                                       form_name="Edit requirement")


        else:
            return render_template('requirement/requirement_edit_page.html', form=form, form_name="Edit requirement")


# add requirement
@app.route('/add_requirement', methods=['POST', 'GET'])
def add_requirement():
    form = RequirementsValidForm()

    if request.method == 'GET':
        return render_template('requirement/add_requirement.html', form=form, form_name="add requirement form")
    else:
        if form.validate():
            new_req = ormRequirement(
                requirement_name=form.requirement_name.data,
                requirement_point=form.requirement_point.data)

            try:
                session.add(new_req)
                session.commit()
                return redirect('/requirement')
            except:
                form.requirement_name.errors = ['Requirement with this name already exists!']
                return render_template('requirement/add_requirement.html', form=form, form_name="add requirement form")

        else:
            return render_template('requirement/add_requirement.html', form=form, form_name="add requirement form")


@app.route('/student_requirements_done', methods=['GET', 'POST'])
def studentRequirementsDone():
    def select_data(ormStudent, ormStudentRequirementsDone, ormRequirement):
        res = session.query(ormStudentRequirementsDone.ukey, ormStudent.student_recordbook,
                            ormRequirement.requirement_name) \
            .select_from(ormStudent) \
            .join(ormStudentRequirementsDone) \
            .join(ormRequirement) \
            .all()

        return res

    def insert_data(data):
        session.add(data)

    def update_data(obj, class_name):
        mapped_values = {}
        for item in class_name.__dict__.items():
            field_name = item[0]
            field_type = item[1]
            is_column = isinstance(field_type, InstrumentedAttribute)
            if is_column:
                mapped_values[field_name] = getattr(obj, field_name)

        session.query(class_name).filter_by(ukey=obj.ukey).update(mapped_values)

    def save():
        session.commit()

    student_list = session.query(ormStudent).all()
    requirement_list = session.query(ormRequirement).all()
    data = select_data(ormStudent, ormStudentRequirementsDone, ormRequirement)
    student_requirement_done = [StudentRequirementDTO(i[0], i[1], i[2]) for i in data]
    form = studentRequirementsDoneForm(request.form)
    form.requirement_name.choices = [(requirement.requirement_name, requirement.requirement_name) for requirement in
                                     requirement_list]
    form.student_recordbook.choices = [(student.student_recordbook, student.student_recordbook) for student in
                                       student_list]

    if request.method == 'POST':
        print(form.ukey.data)
        if form.ukey.data == '':
            student_requirement = ormStudentRequirementsDone(randint(1, 50), form.student_recordbook.data,
                                                             form.requirement_name.data)
            insert_data(student_requirement)
        else:
            student_requirement = ormStudentRequirementsDone(randint(1, 50), form.student_recordbook.data,
                                                             form.requirement_name.data)
            update_data(student_requirement, ormStudentRequirementsDone)
        save()
        return redirect('/student_requirements_done')

    return render_template('student_requirements_done.html', student_requirement_done=student_requirement_done,
                           form=form)


@app.route('/remove_student_requirements_done/<string:student_requirements_done>', methods=['GET', 'POST'])
def remove_student_requirements_done(student_requirements_done):
    remove_event = session.query(ormStudentRequirementsDone).filter(
        ormStudentRequirementsDone.ukey == student_requirements_done).one()

    session.delete(remove_event)
    session.commit()

    return redirect('/student_requirements_done')


@app.route('/edit_student_requirements_done/<string:current_student_requirements_done>', methods=['GET', 'POST'])
def edit_student_requirements_done(current_student_requirements_done):
    requirements = session.query(ormStudentRequirementsDone).filter(
        ormStudentRequirementsDone.ukey == current_student_requirements_done).one()
    student_list = session.query(ormStudent).all()
    requirement_list = session.query(ormRequirement).all()
    form = studentRequirementsDoneForm(request.form)
    form.requirement_name.choices = [(requirement.requirement_name, requirement.requirement_name) for requirement in
                                     requirement_list]
    form.student_recordbook.choices = [(student.student_recordbook, student.student_recordbook) for student in
                                       student_list]

    if request.method == 'GET':

        form.requirement_name.data = requirements.requirement_name
        form.student_recordbook.data = requirements.student_recordbook

        return render_template('requirement/edit_student_requirements_done.html', form=form,
                               form_name="Edit requirement")

    else:

        if form.validate():
            requirements.requirement_name = form.requirement_name.data
            requirements.student_recordbook = form.student_recordbook.data

            try:
                session.commit()
                return redirect('/student_requirements_done')
            except:
                form.requirement_name.errors = ['Requirement with this name already exists!']
                return render_template('requirement/edit_student_requirements_done.html', form=form,
                                       form_name="Edit requirement")


        else:
            return render_template('requirement/requirement_edit_page.html', form=form, form_name="Edit requirement")


@app.route('/laboratory_requirement', methods=['GET', 'POST'])
def laboratoryRequirements():
    def select_data(ormRequirement, ormLaboratoryRequirements, ormLaboratory):
        res = session.query(ormLaboratoryRequirements.ukey, ormRequirement.requirement_name,
                            ormRequirement.requirement_point, ormLaboratory.laboratory_name) \
            .select_from(ormRequirement) \
            .join(ormLaboratoryRequirements) \
            .join(ormLaboratory) \
            .all()

        return res

    def insert_data(data):
        session.add(data)

    def update_data(obj, class_name):
        mapped_values = {}
        for item in class_name.__dict__.items():
            field_name = item[0]
            field_type = item[1]
            is_column = isinstance(field_type, InstrumentedAttribute)
            if is_column:
                mapped_values[field_name] = getattr(obj, field_name)

        session.query(class_name).filter_by(ukey=obj.ukey).update(mapped_values)

    def save():
        session.commit()

    laboratory_list = session.query(ormLaboratory).all()
    requirement_list = session.query(ormRequirement).all()
    data = select_data(ormRequirement, ormLaboratoryRequirements, ormLaboratory)
    laboratory_requirement = [LaboratoryRequirementDTO(i[0], i[1], i[3], i[2]) for i in data]
    form = laboratoryRequirementsForm(request.form)
    form.requirement_name.choices = [(requirement.requirement_name, requirement.requirement_name) for requirement in
                                     requirement_list]
    form.laboratory_name.choices = [(laboratory.laboratory_name, laboratory.laboratory_name) for laboratory in
                                    laboratory_list]

    if request.method == 'POST':
        print(form.ukey.data)
        if form.ukey.data == '':
            laboratory_requirement = ormLaboratoryRequirements(randint(1, 1000), form.laboratory_name.data,
                                                               form.requirement_name.data, form.requirement_point.data)
            insert_data(laboratory_requirement)
        else:
            laboratory_requirement = ormLaboratoryRequirements(randint(1, 1000), form.laboratory_name.data,
                                                               form.requirement_name.data, form.requirement_point.data)
            update_data(laboratory_requirement, ormLaboratoryRequirements)
        save()
        return redirect('/laboratory_requirement')

    return render_template('laboratory_requirement.html', laboratory_requirement=laboratory_requirement, form=form)


@app.route('/remove_laboratory_requirements_/<string:remove_laboratory_requirements_>', methods=['GET', 'POST'])
def remove_laboratory_requirements(remove_laboratory_requirements_):
    remove_event = session.query(ormLaboratoryRequirements).filter(
        ormLaboratoryRequirements.ukey == remove_laboratory_requirements_).one()

    session.delete(remove_event)
    session.commit()

    return redirect('/laboratory_requirement')


@app.route('/edit_laboratory_requirements/<string:current_laboratory_requirements>', methods=['GET', 'POST'])
def edit_laboratory_requirements(current_laboratory_requirements):
    requirements = session.query(ormLaboratoryRequirements).filter(
        ormLaboratoryRequirements.ukey == current_laboratory_requirements).one()
    laboratory_list = session.query(ormLaboratory).all()
    requirement_list = session.query(ormRequirement).all()
    form = laboratoryRequirementsForm(request.form)
    form.requirement_name.choices = [(requirement.requirement_name, requirement.requirement_name) for requirement in
                                     requirement_list]
    form.laboratory_name.choices = [(laboratory.laboratory_name, laboratory.laboratory_name) for laboratory in
                                    laboratory_list]

    if request.method == 'GET':

        form.requirement_name.data = requirements.requirement_name
        form.laboratory_name.data = requirements.laboratory_name

        return render_template('requirement/edit_laboratory_requirements.html', form=form, form_name="Edit requirement")

    else:

        if form.validate():
            requirements.requirement_name = form.requirement_name.data
            requirements.laboratory_name = form.laboratory_name.data

            try:
                session.commit()
                return redirect('/laboratory_requirement')
            except:
                form.requirement_name.errors = ['Requirement with this name already exists!']
                return render_template('requirement/edit_laboratory_requirements.html', form=form,
                                       form_name="Edit requirement")


        else:
            return render_template('requirement/edit_laboratory_requirements.html', form=form,
                                   form_name="Edit requirement")


@app.route('/result', methods=['GET'])
def result():
    laboratory_requirement = session.query(ormLaboratoryRequirements).all()
    student_requirement = session.query(ormStudentRequirementsDone).all()
    for x in laboratory_requirement:
        print(x)
    for x in student_requirement:
        print(x)

    return render_template('result.html', laboratory_requirement=laboratory_requirement,
                           student_requirement=student_requirement)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    def student_done_data(ormStudent, ormStudentRequirementsDone, ormRequirement):
        res = session.query(ormStudent.student_recordbook, func.count(ormRequirement.requirement_name)) \
            .select_from(ormStudent) \
            .join(ormStudentRequirementsDone) \
            .join(ormRequirement) \
            .group_by(ormStudent.student_recordbook).all()
        return res

    def student_count_data(ormStudent, ormStudentRequirementsDone, ormRequirement):
        res = session.query(ormRequirement.requirement_name, func.count(ormRequirement.requirement_name)) \
            .select_from(ormStudent) \
            .join(ormStudentRequirementsDone) \
            .join(ormRequirement) \
            .group_by(ormRequirement.requirement_name).all()
        return res

    done_object = student_done_data(ormStudent, ormStudentRequirementsDone, ormRequirement)
    count_object = student_count_data(ormStudent, ormStudentRequirementsDone, ormRequirement)
    values1 = [i[1] for i in done_object]
    labels1 = [i[0] for i in done_object]
    values2 = [i[1] for i in count_object]
    labels2 = [i[0] for i in count_object]

    x = []
    y = []

    query_for_cor = db.session.query(
        ormStudent.student_time_work,
        func.count(ormStudent.student_recordbook).label('time')
    ).group_by(ormStudent.student_time_work).all()
    print(query_for_cor)
    for i in query_for_cor:
        x.append(int(i[0]))
        y.append(i[1])
    corr_coef = np.corrcoef(x, y)[0][1]

    lab3 = x
    val3 = y


    return render_template('dashboard.html', val1=values1, lab1=labels1, val2=values2, lab2=labels2,lab3=lab3,val3=val3,corr_coef=corr_coef)


app.run(debug=True)


# AIfunc
@app.route('/AIform', methods=['GET', 'POST'])
def AIform_():
    form = AIForm()

    Sample = db.session.query(ormStudent).all()

    #student_is_worker = db.Column(db.String(50), nullable=False)
    #student_time_work = db.Column(db.Integer, nullable=False)
   # requirement_name = db.Column(db.String(50), nullable=False)


    X = []
    y = []
    for i in Sample:
        X.append([i.student_is_worker, i.student_time_work])
        y.append(i.requirement_name)

    Coder1 = ColumnTransformer(transformers=[('code1', OneHotEncoder(), [0])])

    Coder2 = MinMaxScaler(feature_range=(-1, 1))

    Model = MLPClassifier(hidden_layer_sizes=(5,))

    Model = Pipeline(steps=[('code1', Coder1), ('code2', Coder2), ('neur', Model)])
    Model.fit(X, y)

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('AIfunc.html', form=form)
        # db.session.add(new_)
        # db.session.commit()
        new_user = [[form.student_is_worker.data, form.student_time_work.data]]
        y_ = Model.predict(new_user)
        print(y_)
        return render_template('Oko.html', result=y_[0])
    elif request.method == 'GET':
        return render_template('AIfunc.html', form=form)
