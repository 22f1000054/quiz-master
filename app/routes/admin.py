from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from models import Subject, Chapter, Quiz, Question, Answer, Option
from extensions import db

from forms import SubjectForm, ChapterForm, QuizForm, QuestionForm
admin_bp = Blueprint('admin_bp', __name__, template_folder='templates', static_folder='static')

# ---- helper functions ----

def handle_model_edit(model_instance, form_class, success_url_name, success_url_param, 
                     template_name, title, extra_context=None, custom_action=None):
    """
    Generic function to handle edit operations for models.
    
    Args:
        model_instance: Model instance to edit
        form_class: The form class to use
        success_url_name: The URL name to redirect to on success
        success_url_param: The parameter name for the success URL
        template_name: The template to render
        title: Page Title
        extra_context: Additional context for the template
        custom_action: Function to call before commit (receives form and model)
    """

    form = form_class(obj=model_instance)
    
    if form.validate_on_submit():
        form.populate_obj(model_instance)
        
        if custom_action and not custom_action(form, model_instance):
            # If custom action returns False, don't proceed with save
            pass
        else:
            try:
                db.session.commit()
                flash(f'{title} updated successfully!', 'success')
                return redirect(url_for(success_url_name, **{success_url_param: getattr(model_instance, success_url_param.split('_')[-1])}))
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {e}", 'error')

    context = {
        'form': form,
        'title': title
    }
    if extra_context:
        context.update(extra_context)
    
    return render_template(template_name, **context)

# ||---------------------- Admin Routes ----------------------||#

@admin_bp.route('/')
@admin_bp.route('/dashboard')
def admin_dashboard():
    # Check if user is logged in and is admin
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return redirect(url_for('login_bp.login'))
    subjects = Subject.query.all()
    return render_template('admin/dashboard.html', subjects=subjects)

@admin_bp.route('/subject/<int:subject_id>')
def subject_detail(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return render_template('admin/subject_detail.html', subject=subject)

@admin_bp.route('/quiz/<int:quiz_id>')
def quiz_detail(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template('admin/quiz_detail.html', quiz=quiz)


@admin_bp.route('/subject/add', methods=['GET', 'POST'])
def add_subject():
    form = SubjectForm()
    if form.validate_on_submit():
        name=form.name.data
        description=form.description.data

        existing_subject = Subject.query.filter_by(name=name).first()
        if existing_subject:
            flash(f"Subject with name '{name}' already exists.", 'error')
            return render_template('admin/subject_form.html', form=form, title='Add Subject')

        subject = Subject(name=name, description=description)
        db.session.add(subject)
        
        try:
            db.session.commit()
            flash('Subject added successfully!', 'success')
            return redirect(url_for('admin_bp.admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", 'error')

    return render_template('admin/subject_form.html', form=form, title='Add Subject')

@admin_bp.route('/subject/<int:subject_id>/edit', methods=['GET', 'POST'])
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return handle_model_edit(
        model_instance=subject,
        form_class=SubjectForm,
        success_url_name='admin_bp.subject_detail',
        success_url_param='subject_id',
        template_name='admin/subject_form.html',
        title='Edit Subject'
    )

@admin_bp.route('/subject/<int:subject_id>/delete')
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('admin_bp.admin_dashboard'))

# ||---------------------- Chapter Routes ----------------------||#

@admin_bp.route('/subject/<int:subject_id>/chapter/add', methods=['GET', 'POST'])
def add_chapter(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    form = ChapterForm()
    if form.validate_on_submit():
        name=form.name.data
        description=form.description.data
        subject_id=subject.id
        existing_chapter = Chapter.query.filter_by(name=name, subject_id=subject.id).first()

        if existing_chapter:
            flash(f"Chapter with name '{name}' already exists in this subject.", 'error')
            return render_template('admin/chapter_form.html', form=form, subject=subject, title='Add Chapter')
        chapter = Chapter(
            name=name,
            description=description,
            subject_id=subject_id
        )
        db.session.add(chapter)
        try:
            db.session.commit()
            flash('Subject added successfully!', 'success')
            return redirect(url_for('admin_bp.subject_detail', subject_id=subject.id))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", 'error')
            
    return render_template('admin/chapter_form.html', form=form, subject=subject, title='Add Chapter')

@admin_bp.route('/chapter/<int:chapter_id>/edit', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    return handle_model_edit(
        model_instance=chapter,
        form_class=ChapterForm,
        success_url_name='admin_bp.subject_detail',
        success_url_param='subject_id',
        template_name='admin/chapter_form.html',
        title='Edit Chapter',
        extra_context={'subject': chapter.subject}
    )

@admin_bp.route('/chapter/<int:chapter_id>/delete')
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    subject_id = chapter.subject_id # Get subject_id before deleting
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted successfully!', 'success')
    return redirect(url_for('admin_bp.subject_detail', subject_id=subject_id))

# ||---------------------- Quiz Routes ----------------------||#

@admin_bp.route('/chapter/<int:chapter_id>/quiz/add', methods=['GET', 'POST'])
def add_quiz(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    form = QuizForm()
    if form.validate_on_submit():
        quiz = Quiz(
            title=form.title.data,
            description=form.description.data,
            time_duration=form.time_duration.data,
            is_published=form.is_published.data,
            chapter_id=chapter.id
        )
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz added successfully!', 'success')
        return redirect(url_for('admin_bp.subject_detail', subject_id=chapter.subject_id))
    return render_template('admin/quiz_form.html', form=form, chapter=chapter, title='Add Quiz')

# @admin_bp.route('/quiz/<int:quiz_id>/edit', methods=['GET', 'POST'])
# def edit_quiz(quiz_id):
#     quiz = Quiz.query.get_or_404(quiz_id)
#     form = QuizForm(obj=quiz)
#     if form.validate_on_submit():
#         quiz.title = form.title.data
#         quiz.description = form.description.data
#         quiz.time_duration = form.time_duration.data
#         quiz.is_published = form.is_published.data
#         db.session.commit()
#         flash('Quiz updated successfully!', 'success')
#         return redirect(url_for('quiz_detail', quiz_id=quiz.id))
#     return render_template('admin/quiz_form.html', form=form, chapter=quiz.chapter, title='Edit Quiz')


@admin_bp.route('/quiz/<int:quiz_id>/edit', methods=['GET', 'POST'])
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    form_kwargs = {'chapter_id': quiz.chapter_id}
    return handle_model_edit(
        model_instance=quiz,
        form_class=QuizForm,
        form_kwargs=form_kwargs,
        success_url_name='admin_bp.quiz_detail',
        success_url_param='quiz_id',
        template_name='admin/quiz_form.html',
        title='Edit Quiz',
        extra_context={'chapter': quiz.chapter}
    )

@admin_bp.route('/quiz/<int:quiz_id>/delete')
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    # chapter_id = quiz.chapter_id
    subject_id = quiz.chapter.subject_id # Need this for redirect
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully!', 'success')
    # Redirect back to the subject detail page which lists chapters and quizzes
    return redirect(url_for('admin_bp.subject_detail', subject_id=subject_id))

# ||---------------------- Question Routes ----------------------||#

@admin_bp.route('/quiz/<int:quiz_id>/question/add', methods=['GET', 'POST'])
def add_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    # Add default empty options for the form
    form = QuestionForm(options=[{}, {}]) # Start with 2 empty option fields
    form.correct_option.choices = [(i, f"Option {i+1}") for i, _ in enumerate(form.options.entries)] # Set initial choices

    if form.validate_on_submit():
        # Create the question first
        # Corrected line for your route
        question = Question(question_text=form.text.data, quiz_id=quiz.id)
        db.session.add(question)
        # Flush to get the question ID before creating options
        db.session.flush()

        # Create options and link them
        for i, option_form in enumerate(form.options.entries):
            is_correct = (i == form.correct_option.data)
            option = Option(
                option_text=option_form.form.text.data,
                is_correct=is_correct,
                question_id=question.id
            )
            db.session.add(option)

        db.session.commit()
        flash('Question added successfully!', 'success')
        return redirect(url_for('admin_bp.quiz_detail', quiz_id=quiz.id))

    return render_template('admin/question_form.html', form=form, quiz=quiz, title='Add Question')


@admin_bp.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    # Pre-populate form data
    form_data = {
        'text': question.question_text,
        'options': [{'text': opt.option_text} for opt in question.options],
        'correct_option': next((i for i, opt in enumerate(question.options) if opt.is_correct), None)
    }

    def custom_option_handling(form, model):
        """Handle the special case of options for questions"""
        model.text = form.text.data
        # Delete old options and create new ones
        Option.query.filter_by(question_id=model.id).delete()
        db.session.flush()
        
        for i, option_form in enumerate(form.options.entries):
            is_correct = (i == form.correct_option.data)
            option = Option(
                option_text=option_form.form.text.data,
                is_correct=is_correct,
                question_id=model.id
            )
            db.session.add(option)
        return True
    
    # Use a different approach for questions due to their complexity
    form = QuestionForm(data=form_data)
    form.correct_option.choices = [(i, f"Option {i+1}") for i, _ in enumerate(form.options.entries)]
    
    return handle_model_edit(
        model_instance=question,
        form_class=QuestionForm,
        success_url_name='admin_bp.quiz_detail',
        success_url_param='quiz_id',
        template_name='admin/question_form.html',
        title='Edit Question',
        extra_context={'quiz': question.quiz},
        custom_action=custom_option_handling
    )
    # form = QuestionForm(data=form_data)
    # form.correct_option.choices = [(i, f"Option {i+1}") for i, _ in enumerate(form.options.entries)] # Set choices

    # if form.validate_on_submit():
    #     question.text = form.text.data

    #     # Update options: Delete old ones, add new ones (simpler than tracking changes)
    #     # This assumes options don't need to preserve their IDs across edits.
    #     # If they do, you'd need more complex logic to update existing ones.
    #     Option.query.filter_by(question_id=question.id).delete()
    #     db.session.flush() # Ensure deletes hadmin_bpen before adds

    #     for i, option_form in enumerate(form.options.entries):
    #         is_correct = (i == form.correct_option.data)
    #         option = Option(
    #             text=option_form.form.text.data,
    #             is_correct=is_correct,
    #             question_id=question.id
    #         )
    #         db.session.add(option)

    #     db.session.commit()
    #     flash('Question updated successfully!', 'success')
    #     return redirect(url_for('quiz_detail', quiz_id=question.quiz_id))

    # return render_template('admin/question_form.html', form=form, quiz=question.quiz, title='Edit Question')


@admin_bp.route('/question/<int:question_id>/delete')
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id # Get quiz_id before deleting
    db.session.delete(question) # Cascade should delete options
    db.session.commit()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('admin_bp.quiz_detail', quiz_id=quiz_id))