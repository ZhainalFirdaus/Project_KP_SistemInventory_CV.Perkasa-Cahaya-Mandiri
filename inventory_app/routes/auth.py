from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from ..models import User
from ..extensions import db
from ..utils import log_activity

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            log_activity('Login', f'User {username} masuk ke sistem')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid Credentials', 'error')
    return render_template('login.html')

@auth.route('/logout')
def logout():
    if current_user.is_authenticated:
        log_activity('Logout', f'User {current_user.username} keluar dari sistem')
    logout_user()
    return redirect(url_for('auth.login'))

# @auth.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         confirm_password = request.form.get('confirm_password')
#         
#         if password != confirm_password:
#             flash('Password tidak cocok!', 'error')
#             return redirect(url_for('auth.register'))
#         
#         if User.query.filter_by(username=username).first():
#             flash('Username sudah digunakan!', 'error')
#             return redirect(url_for('auth.register'))
#         
#         hashed_password = generate_password_hash(password)
#         new_user = User(username=username, password_hash=hashed_password)
#         db.session.add(new_user)
#         db.session.commit()
#         log_activity('Registrasi', f'User baru terdaftar: {username}')
#         
#         flash('Account created! Please login.', 'success')
#         return redirect(url_for('auth.login'))
#         
#     return render_template('register.html')

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        from ..utils import save_picture, delete_old_picture
        new_username = request.form.get('username')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        profile_pic = request.files.get('profile_pic')
        
        # Handle Username
        if new_username and new_username != current_user.username:
            if User.query.filter_by(username=new_username).first():
                flash('Username sudah digunakan!', 'error')
                return redirect(url_for('auth.profile'))
            current_user.username = new_username
            
        # Handle Profile Picture
        if profile_pic:
            # Delete old picture if it's not the default
            if current_user.image_file != 'default_user.jpg':
                delete_old_picture(current_user.image_file)
            
            # Save new picture
            picture_file = save_picture(profile_pic)
            current_user.image_file = picture_file
            
        # Handle Password
        if new_password:
            if new_password != confirm_password:
                flash('Password baru tidak cocok!', 'error')
                return redirect(url_for('auth.profile'))
            current_user.password_hash = generate_password_hash(new_password)
            
        try:
            db.session.commit()
            log_activity('Update Profil', f'User {current_user.username} memperbarui data profil')
            flash('Profil berhasil diperbaharui!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal memperbaharui profil: {str(e)}', 'error')
            
        return redirect(url_for('auth.profile'))
        
    # Get current profile image URL
    if current_user.image_file == 'default_user.jpg':
        image_url = f"https://ui-avatars.com/api/?name={current_user.username}&size=128&background=3b82f6&color=fff&bold=true"
    else:
        image_url = url_for('static', filename='uploads/' + current_user.image_file)
        
    return render_template('profile.html', now=datetime.utcnow(), image_url=image_url)
