from flask_wtf import Form
from wtforms import StringField, SubmitField, PasswordField, DateField, HiddenField, IntegerField, SelectField,ValidationError
from wtforms import validators

def validStr(form, field):
    for i in field.data:
        if i.lower() not in list('qwertyuioplkjhgfdsazxcvbnm '):
            raise ValidationError('Enter symbol!')

def validInt(form, field):
    for i in field.data:
        if i.lower() not in list('0123456789'):
            raise ValidationError('Enter number!')


class StudentValidForm(Form):
    student_recordbook = StringField("Student recordbook: ", [
        validators.DataRequired("Please enter student recordbook."),
        validators.Length(7, 10, "Recordbook should be from 7 to 10 symbols")
    ])

    student_name = StringField("Student name: ", [
        validStr,
        validators.DataRequired("Please enter student name."),
        validators.Length(1, 50, "Student name should be from 1 to 50 symbols")
    ])

    student_surname = StringField("Student surname: ", [
        validStr,
        validators.DataRequired("Please enter student surname."),
        validators.Length(1, 50, "Student surname should be from 1 to 50 symbols")])

    student_groupe = StringField("Student group: ", [
        validators.DataRequired("Please enter student group."),
        validators.Length(5, 10, "Student group should be from 1 to 10 symbols")])

    student_faculty = StringField("Student faculty: ", [
        validStr,
        validators.DataRequired("Please enter student faculty."),
        validators.Length(3, 50, "Student faculty should be from 3 to 50 symbols")])

    submit = SubmitField("Save")


class LaboratoryValidForm(Form):
    laboratory_name = StringField("Laboratory name: ", [
        validStr,
        validators.DataRequired("Please enter laboratory name."),
        validators.Length(1, 50, "Laboratory name should be from 1 to 50 symbols")
    ])

    laboratory_subject = StringField("Laboratory subject: ", [
        validStr,
        validators.DataRequired("Please enter student name."),
        validators.Length(1, 50, "Student name should be from 1 to 50 symbols")
    ])

    laboratory_mark = IntegerField("Laboratory mark: ", [
        validators.DataRequired("Please enter Laboratory mark."),
        validators.NumberRange(min=1, max=5, message="Laboratory mark should be from 1 to 5"),
    ])

    submit = SubmitField("Save")


class RequirementsValidForm(Form):
    requirement_name = StringField("Requirement name: ", [
        validStr,
        validators.DataRequired("Please enter requirement name."),
        validators.Length(1, 50, "Requirement name should be from 1 to 50 symbols")
    ])

    requirement_point = IntegerField("Requirement point: ", [
        validators.DataRequired("Please enter Requirement point."),
        validators.NumberRange(min=1, max=5, message="Requirement point should be from 1 to 5"),
    ])

    submit = SubmitField("Save")


class studentRequirementsDoneForm(Form):
    ukey = HiddenField("Id")
    student_recordbook = SelectField("Student: ", choices=[], coerce=str)
    requirement_name = SelectField("Requirements: ", choices=[], coerce=str)

    submit = SubmitField("Save")


class laboratoryRequirementsForm(Form):
    ukey = HiddenField("Id")
    laboratory_name = SelectField("Laboratory: ", choices=[], coerce=str)
    requirement_name = SelectField("Requirements: ", choices=[], coerce=str)
    requirement_point = IntegerField("point: ", [
        validators.DataRequired("Please enter Requirement point."),
        validators.NumberRange(min=1, max=5, message="Requirement point should be from 1 to 5")
    ])

    submit = SubmitField("Save")


def booling(form, field):
    if (field.data) not in ['true', 'false']:
        raise ValidationError("true or false")


class AIForm(Form):
    student_is_worker = StringField("work ", [booling, validators.DataRequired("Please enter")])

    student_time_work = IntegerField("time: ", [
        validators.DataRequired("Please enter ."),
        validators.NumberRange(min=1, max=5, message="Requirement point should be from 1 to 5")
    ])


    submit = SubmitField("Save")
