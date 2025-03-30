from flask import Flask, render_template, redirect, url_for, session, flash
from config import Config
# from flask_login import LoginManager, login_user, login_required, logout_user, current_user
# from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db 
from forms import SubjectForm, ChapterForm
from models import User, init_db, Subject, Quiz, Chapter
from routes.login import login_bp
from routes.admin import admin_bp
app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(login_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')

init_db(app)
@app.route('/')
def main():
    return render_template('main.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    # Check if user is logged in and is admin
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return redirect(url_for('login_bp.login'))
    subjects = Subject.query.all()
    return render_template('admin/dashboard.html', subjects=subjects)

@app.route('/admin/subject/<int:subject_id>')
def subject_detail(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return render_template('admin/subject_detail.html', subject=subject)

@app.route('/admin/quiz/<int:quiz_id>')
def quiz_detail(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template('admin/quiz_detail.html', quiz=quiz)

@app.route('/student/<user_id>')
def student_dashboard(user_id):
    # Check if user is logged in and is the correct student
    if session.get('user_id') != user_id:
      return redirect(url_for('login_bp.login'))
    return render_template('student/dashboard.html', user_id=user_id)




if __name__ == '__main__':
    app.run(debug=True)