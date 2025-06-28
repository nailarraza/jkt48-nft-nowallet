# D:\jkt48-nft-app\app\__init__.py
# File ini berfungsi sebagai "Application Factory".
# Tugasnya adalah membuat dan mengonfigurasi instance aplikasi Flask.

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

# Inisialisasi ekstensi Flask
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()

# Mengarahkan pengguna yang belum login ke halaman login
login_manager.login_view = 'auth.login'
# Pesan yang akan ditampilkan kepada pengguna
login_manager.login_message = "Silakan login untuk mengakses halaman ini."
login_manager.login_message_category = 'warning'

def create_app(config_class=Config):
    """
    Factory function untuk membuat aplikasi Flask.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Menghubungkan ekstensi dengan instance aplikasi
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Import dan daftarkan blueprint di sini untuk mengorganisir rute
    from app.routes import main_bp
    from app.auth_routes import auth_bp
    from app.admin_routes import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Custom Jinja2 filter untuk format mata uang Rupiah
    @app.template_filter('currency')
    def currency_filter(value):
        # Memformat angka menjadi string mata uang, misal: 150000 -> Rp 150.000
        if value is None:
            return "Rp 0"
        return f"Rp {value:,.0f}".replace(",", ".")

    with app.app_context():
        # Bagian ini bisa digunakan untuk mendaftarkan command atau proses lain
        # yang membutuhkan application context.
        pass

    return app
