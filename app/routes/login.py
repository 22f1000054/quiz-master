from flask import Blueprint, render_template, request, redirect, url_for


login_bp = Blueprint('login_bp', __name__, template_folder='templates', static_folder='static')

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login logic here
        username = request.form['username']
        password = request.form['password']
        # Check credentials and log in the user
        return redirect(url_for('main'))
    return render_template('login.html')

@login_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Handle registration logic here
        username = request.form['username']
        password = request.form['password']
        # Save user to the database
        return redirect(url_for('login_bp.login'))
    return render_template('register.html')



@login_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        # Handle password reset logic here
        email = request.form['email']
        # Send password reset email
        return redirect(url_for('login_bp.login'))
    return render_template('forgot_password.html')

@login_bp.route('/logout')
def render_register_page():
    return redirect(url_for('login_bp.login'))