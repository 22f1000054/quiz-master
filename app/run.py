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

if __name__ == '__main__':
    app.run(debug=True)