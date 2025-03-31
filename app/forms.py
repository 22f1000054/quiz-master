from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, BooleanField, FieldList, FormField, RadioField
from wtforms.validators import DataRequired, Length, Optional, ValidationError, NumberRange
from models import Subject, Chapter, Quiz, Option, Question

class GenericForm(FlaskForm):
    """Base form for models that require unique names"""
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        _model_class = kwargs.pop('model_class', None)
        _model_instance = kwargs.pop('obj', None) # For editing
        _parent_field_name = kwargs.pop('parent_field_name', None) # e.g., 'subject_id'
        _parent_id = kwargs.pop('parent_id', None) # The actual ID value passed in

        # Call the parent __init__ first with the remaining standard kwargs
        super().__init__(*args, **kwargs)

        # Now, set the custom attributes on the instance
        self.model_class = _model_class
        self.model_instance = _model_instance
        self.parent_field_name = _parent_field_name
        self.parent_id = _parent_id

        
    def validate_name(self, field):
        """Validate that the name is unique within its context"""
        if not self.model_class:
            return

        query = self.model_class.query.filter(
            getattr(self.model_class, 'name') == field.data
        )

        # For models with parent relationships, restrict uniqueness to the parent
        if self.parent_field_name and self.parent_id is not None:
            query = query.filter(
                getattr(self.model_class, self.parent_field_name) == self.parent_id
            )
        
        # If we're editing an existing instance, exclude it from the check
        if self.model_instance and hasattr(self.model_instance, 'id'):
            query = query.filter(self.model_class.id != self.model_instance.id)
            
        existing = query.first()
        if existing:
            context = f" within the parent {self.parent_field_name.replace('_id', '')}" if self.parent_field_name else ""
            raise ValidationError(
                f"{self.model_class.__name__} with name '{field.data}' already exists{context}."
            )

class SubjectForm(GenericForm):
    submit = SubmitField('Add Subject') 
    def __init__(self, *args, **kwargs):
        kwargs['model_class'] = Subject
        super().__init__(*args, **kwargs)

class ChapterForm(GenericForm):
    submit = SubmitField('Add Chapter')
    
    def __init__(self, *args, **kwargs):
        subject_id = kwargs.get('subject_id')
        kwargs['model_class'] = Chapter
        kwargs['parent_field_name'] = 'subject_id'
        kwargs['parent_id'] = subject_id
        super().__init__(*args, **kwargs)

# Quiz Form - Note this one uses 'title' instead of 'name'
class QuizForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    time_duration = IntegerField('Time Duration (minutes)', validators=[Optional()])
    remarks = TextAreaField('Remarks', validators=[Optional()])
    is_published = BooleanField('Published', default=False)

    submit = SubmitField('Save Quiz')
    
    def __init__(self, *args, **kwargs):
        chapter_id = kwargs.get('chapter_id')
        kwargs['model_class'] = Quiz
        super().__init__(*args, **kwargs)
        self.chapter_id = chapter_id
        self.quiz_instance = kwargs.get('model_class')

    def validate_title(self, field):
        """Validate that the title is unique within the parent chapter."""
        query = Quiz.query.filter(
            Quiz.chapter_id == self.chapter_id,
            Quiz.title == field.data
        )

        if self.quiz_instance and hasattr(self.quiz_instance, 'id'):
            query = query.filter(Quiz.id != self.quiz_instance.id)

        existing = query.first()
        if existing:
            raise ValidationError(
                f"A quiz with title '{field.data}' already exists in this chapter."
            )

class OptionForm(FlaskForm):
    class Meta:
        csrf = False
    text = StringField('Option Text', validators=[DataRequired()])

class QuestionForm(FlaskForm):
    text = TextAreaField('Question Text', validators=[DataRequired()])
    options = FieldList(FormField(OptionForm), min_entries=2, max_entries=5)
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
        # Only set choices if there are options
        if self.options.entries:
            self.correct_option.choices = [(i, f"Option {i+1}") for i, _ in enumerate(self.options.entries)]