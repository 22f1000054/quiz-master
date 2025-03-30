from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, BooleanField, FieldList, FormField, RadioField
from wtforms.validators import DataRequired, Length, Optional, ValidationError, NumberRange

class SubjectForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Save')

class ChapterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Save Chapter')

class QuizForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    time_duration = IntegerField('Duration (minutes)', validators=[Optional(), NumberRange(min=1)])
    is_published = BooleanField('Publish Quiz?')
    submit = SubmitField('Save Quiz')

class OptionForm(FlaskForm):
    class Meta:
        csrf = False
    text = StringField('Option Text', validators=[DataRequired()])

class QuestionForm(FlaskForm):
    text = TextAreaField('Question Text', validators=[DataRequired()])
    options = FieldList(FormField(OptionForm), min_entries=2, max_entries=6)
    correct_option = RadioField('Correct Answer', coerce=int, validators=[DataRequired(message="Please select the correct answer.")])
    submit = SubmitField('Save Question')

    def validate_options(self, field):
        if len(field.entries) < 2:
             raise ValidationError('Please provide at least two options.')
        for entry in field.entries:
            if not entry.form.text.data:
                 raise ValidationError('All option fields must be filled.')

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.correct_option.choices = [(i, f"Option {i+1}") for i, _ in enumerate(self.options.entries)]