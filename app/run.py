from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager, login_user, login_required, logout_user, current_user
# from werkzeug.security import generate_password_hash, check_password_hash

from routes.login import login_bp
app = Flask(__name__)
app.register_blueprint(login_bp)

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    # Check if user is logged in and is admin
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return redirect(url_for('login_bp.login'))
    return render_template('dashboard/admin_dashboard.html')

@app.route('/student/<user_id>')
def student_dashboard(user_id):
    # Check if user is logged in and is the correct student
    if session.get('user_id') != user_id:
      return redirect(url_for('login_bp.login'))
    return render_template('dashboard/student_dashboard.html', user_id=user_id)


if __name__ == '__main__':
    app.run(debug=True)