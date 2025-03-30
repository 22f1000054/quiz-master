from flask import Blueprint, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from models import Subject, Chapter, Quiz, Question, Answer, Option
from extensions import db

from forms import SubjectForm, ChapterForm, QuizForm, QuestionForm
admin_bp = Blueprint('admin_bp', __name__, template_folder='templates', static_folder='static')

@admin_bp.route('/subject/add', methods=['GET', 'POST'])
def add_subject():
    form = SubjectForm()
    if form.validate_on_submit():
        subject = Subject(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(subject)
        db.session.commit()
        flash('Subject added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/subject_form.html', form=form, title='Add Subject')

@admin_bp.route('/admin/subject/<int:subject_id>/edit', methods=['GET', 'POST'])
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    form = SubjectForm(obj=subject)
    if form.validate_on_submit():
        subject.name = form.name.data
        subject.description = form.description.data
        db.session.commit()
        flash('Subject updated successfully!', 'success')
        return redirect(url_for('subject_detail', subject_id=subject.id))
    return render_template('admin/subject_form.html', form=form, title='Edit Subject')

@admin_bp.route('/admin/subject/<int:subject_id>/delete')
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# ||---------------------- Chapter Routes ----------------------||#

@admin_bp.route('/admin/subject/<int:subject_id>/chapter/add', methods=['GET', 'POST'])
def add_chapter(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    form = ChapterForm()
    if form.validate_on_submit():
        chapter = Chapter(
            name=form.name.data,
            description=form.description.data,
            subject_id=subject.id
        )
        db.session.add(chapter)
        db.session.commit()
        flash('Chapter added successfully!', 'success')
        return redirect(url_for('subject_detail', subject_id=subject.id))
    return render_template('admin/chapter_form.html', form=form, subject=subject, title='Add Chapter')

@admin_bp.route('/admin/chapter/<int:chapter_id>/edit', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    form = ChapterForm(obj=chapter)
    if form.validate_on_submit():
        chapter.name = form.name.data
        chapter.description = form.description.data
        db.session.commit()
        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('subject_detail', subject_id=chapter.subject_id))
    return render_template('admin/chapter_form.html', form=form, subject=chapter.subject, title='Edit Chapter')

@admin_bp.route('/admin/chapter/<int:chapter_id>/delete')
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    subject_id = chapter.subject_id # Get subject_id before deleting
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted successfully!', 'success')
    return redirect(url_for('subject_detail', subject_id=subject_id))

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
        return redirect(url_for('subject_detail', subject_id=chapter.subject_id))
    return render_template('admin/quiz_form.html', form=form, chapter=chapter, title='Add Quiz')

@admin_bp.route('/admin/quiz/<int:quiz_id>/edit', methods=['GET', 'POST'])
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuizForm(obj=quiz)
    if form.validate_on_submit():
        quiz.title = form.title.data
        quiz.description = form.description.data
        quiz.time_duration = form.time_duration.data
        quiz.is_published = form.is_published.data
        db.session.commit()
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('quiz_detail', quiz_id=quiz.id))
    return render_template('admin/quiz_form.html', form=form, chapter=quiz.chapter, title='Edit Quiz')

@admin_bp.route('/admin/quiz/<int:quiz_id>/delete')
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    chapter_id = quiz.chapter_id
    subject_id = quiz.chapter.subject_id # Need this for redirect
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully!', 'success')
    # Redirect back to the subject detail page which lists chapters and quizzes
    return redirect(url_for('subject_detail', subject_id=subject_id))

# ||---------------------- Question Routes ----------------------||#

@admin_bp.route('/quiz/<int:quiz_id>/question/add', methods=['GET', 'POST'])
def add_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    # Add default empty options for the form
    form = QuestionForm(options=[{}, {}]) # Start with 2 empty option fields
    form.correct_option.choices = [(i, f"Option {i+1}") for i, _ in enumerate(form.options.entries)] # Set initial choices

    if form.validate_on_submit():
        # Create the question first
        question = Question(text=form.text.data, quiz_id=quiz.id)
        db.session.add(question)
        # Flush to get the question ID before creating options
        db.session.flush()

        # Create options and link them
        for i, option_form in enumerate(form.options.entries):
            is_correct = (i == form.correct_option.data)
            option = Option(
                text=option_form.form.text.data,
                is_correct=is_correct,
                question_id=question.id
            )
            db.session.add(option)

        db.session.commit()
        flash('Question added successfully!', 'success')
        return redirect(url_for('quiz_detail', quiz_id=quiz.id))

    return render_template('admin/question_form.html', form=form, quiz=quiz, title='Add Question')


@admin_bp.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    # Pre-populate form data
    form_data = {
        'text': question.text,
        'options': [{'text': opt.text} for opt in question.options.all()], # Get existing options
        'correct_option': next((i for i, opt in enumerate(question.options.all()) if opt.is_correct), None) # Find index of correct option
    }
    form = QuestionForm(data=form_data)
    form.correct_option.choices = [(i, f"Option {i+1}") for i, _ in enumerate(form.options.entries)] # Set choices

    if form.validate_on_submit():
        question.text = form.text.data

        # Update options: Delete old ones, add new ones (simpler than tracking changes)
        # This assumes options don't need to preserve their IDs across edits.
        # If they do, you'd need more complex logic to update existing ones.
        Option.query.filter_by(question_id=question.id).delete()
        db.session.flush() # Ensure deletes hadmin_bpen before adds

        for i, option_form in enumerate(form.options.entries):
            is_correct = (i == form.correct_option.data)
            option = Option(
                text=option_form.form.text.data,
                is_correct=is_correct,
                question_id=question.id
            )
            db.session.add(option)

        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('quiz_detail', quiz_id=question.quiz_id))

    return render_template('admin/question_form.html', form=form, quiz=question.quiz, title='Edit Question')


@admin_bp.route('/question/<int:question_id>/delete')
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id # Get quiz_id before deleting
    db.session.delete(question) # Cascade should delete options
    db.session.commit()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('quiz_detail', quiz_id=quiz_id))