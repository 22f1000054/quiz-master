from flask import Flask, render_template, redirect, url_for, session, flash
from config import Config

from models import init_db
from routes.login import login_bp
from routes.admin import admin_bp
app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(login_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')

init_db(app)
@app.route('/')
def main():
    return redirect(url_for('student_dashboard', user_id=session.get('user_id')))

@app.route('/student/<user_id>')
def student_dashboard(user_id):
    # Check if user is logged in and is the correct student
    if session.get('user_id') != user_id:
      return redirect(url_for('login_bp.login'))
    return render_template('student/dashboard.html', user_id=user_id)




if __name__ == '__main__':
    app.run(debug=True)