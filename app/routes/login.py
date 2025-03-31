from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

from extensions import db
from models import User

login_bp = Blueprint('login_bp', __name__, template_folder='templates', static_folder='static')

# --- Helper Functions ---
def generate_token():
    """Temporary simple token, will be replaced with proper JWT in production)"""
    return str(uuid.uuid4())

def authenticate_user(email, password):
    """Authenticate a user against our dummy database"""
    # user = USERS_DB.get(email)
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return {
            "authenticated": True,
            "user_id": user.id,
            "user_role": user.role,
            "full_name": user.full_name,
            "access_token": generate_token(),
            "refresh_token": generate_token(),
            "message": "Login successful"
        }
    return {"authenticated": False, "message": "Invalid email or password"}

def register_user(email, password, full_name, dob):
    """Register a new user in our dummy database"""
    if User.query.filter_by(email=email).first():
        return {"success": False, "message": "Email already registered"}

    if len(password) < 8:
        return {"success": False, "message": "Password must be at least 8 characters long"}
    if not full_name:
        return {"success": False, "message": "Full name is required"}
    if not email:
        return {"success": False, "message": "Email is required"}
    if not password:
        return {"success": False, "message": "Password is required"}

    new_user = User(
        email=email, 
        password_hash=generate_password_hash(password), 
        full_name=full_name,
        role='student',
        dob=dob
    )
    db.session.add(new_user)
    db.session.commit()
    
    return {"success": True, "message": "Registration successful"}

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
      flash('Email and password are required.', 'error')
      return render_template('authentication/login.html')

    auth_result = authenticate_user(email, password)

    if auth_result["authenticated"]:
      session['user_id'] = auth_result["user_id"]
      session['user_role'] = auth_result["user_role"]
      session['full_name'] = auth_result["full_name"]
      
      response = make_response()
      response.set_cookie(
          'access_token', 
          auth_result['access_token'], 
          httponly=True, 
          max_age=3600,  # 1 hour
          samesite='Lax'
      )
      response.set_cookie(
          'refresh_token', 
          auth_result['refresh_token'], 
          httponly=True, 
          max_age=86400 * 7,  # 7 days
          samesite='Lax'
      )

      # Redirect based on Authorization
      if auth_result["user_role"] == "admin":
          response = make_response(redirect(url_for('admin_bp.admin_dashboard')))
      else:
          response = make_response(redirect(url_for('student_dashboard', user_id=auth_result['user_id'])))

      response.set_cookie('access_token', auth_result['access_token'], httponly=True)
      response.set_cookie('refresh_token', auth_result['refresh_token'], httponly=True)

      return response
    else:
      flash(auth_result["message"], 'error')
      return redirect(url_for('login_bp.login'))

  return render_template('authentication/login.html')

@login_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        dob = request.form.get('dob')
        
        if not email or not password or not confirm_password or not full_name:
            flash("Please fill out all required fields", "error")
            return redirect(url_for('login_bp.register', error="Please fill out all required fields"))
            
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for('login_bp.register', error="Passwords do not match"))
            
        if len(password) < 8:
            flash("Password must be at least 8 characters long", "error")
            return redirect(url_for('login_bp.register', error="Password must be at least 8 characters long"))
        
        result = register_user(email, password, full_name, dob)

        if result["success"]:
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login_bp.login', success="Registration successful! Please log in."))
        else:
            flash(result["message"], "error")
            return redirect(url_for('login_bp.register', error=result["message"]))
            
    error = request.args.get('error')
    return render_template('authentication/register.html', error=error)


@login_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash("Please enter your email address", "error")
            return redirect(url_for('login_bp.forgot_password', error="Please enter your email address"))
            
        # Check if email exists in our database
        if User.query.filter_by(email=email).first():
            # For actual implementation, we would:
            # 1. Generate a password reset token
            # 2. Store it with an expiration time
            # 3. Send an email with a reset link
            
            flash("If your email is registered, you will receive password reset instructions.", "info")
            # For demo purposes, we'll just redirect to login
            return redirect(url_for('login_bp.login', info="Password reset email sent (simulated)"))
        else:
            flash("If your email is registered, you will receive password reset instructions.", "info")
            return redirect(url_for('login_bp.login', info="Password reset email sent (simulated)"))
            
    error = request.args.get('error')
    return render_template('authentication/forgot_password.html', error=error)

@login_bp.route('/logout')
def logout():
    session.clear()

    response = make_response(redirect(url_for('login_bp.login')))
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')

    flash("You have been logged out successfully", "info")
    return response

@login_bp.route('/terms-of-service')
def terms_of_service():
    return render_template('terms_of_service.html')

@login_bp.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')