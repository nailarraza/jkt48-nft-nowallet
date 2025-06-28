# D:\jkt48-nft-app\app\auth_routes.py
# MODIFIKASI: Sistem login sekarang hanya menggunakan username, bukan email.

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Menampilkan halaman registrasi dan memproses pendaftaran pengguna baru."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('  Password dan konfirmasi password tidak cocok!', 'danger')
            return redirect(url_for('auth.register'))

        user_by_email = User.query.filter_by(email=email).first()
        if user_by_email:
            flash('  Alamat email sudah terdaftar. Silakan gunakan email lain.', 'warning')
            return redirect(url_for('auth.register'))

        user_by_username = User.query.filter_by(username=username).first()
        if user_by_username:
            flash('  Username sudah digunakan. Silakan pilih username lain.', 'warning')
            return redirect(url_for('auth.register'))

        new_user = User(username=username, email=email)
        new_user.password = password
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('  Akun Anda berhasil dibuat! Silakan login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='Register')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Menampilkan halaman login dan memproses upaya login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # Mengambil input 'username' dari form
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        # Mencari user hanya berdasarkan username
        user = User.query.filter_by(username=username).first()

        if user and user.verify_password(password):
            login_user(user, remember=remember)
            flash('  Login berhasil! Selamat datang kembali.', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('  Login gagal. Periksa kembali username dan password Anda.', 'danger')

    return render_template('auth/login.html', title='Login')


@auth_bp.route('/logout')
@login_required
def logout():
    """Memproses logout pengguna."""
    logout_user()
    flash('  Anda telah berhasil logout.', 'info')
    return redirect(url_for('main.index'))
