# D:\jkt48-nft-app\app\models.py
# File ini mendefinisikan semua model data (cetakan tabel database)
# menggunakan Flask-SQLAlchemy.

from datetime import datetime, timezone
from app import db, login_manager, bcrypt
from flask_login import UserMixin
import uuid      # Untuk membuat ID tiket yang unik (Universally Unique Identifier)
import hashlib   # Untuk membuat hash SHA-256 (konsep NFT)

# Callback function untuk Flask-Login.
# Memberitahu cara memuat user berdasarkan ID yang disimpan di session.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """Model untuk data pengguna."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    nik = db.Column(db.String(16), unique=True, nullable=True) # Nomor Induk Kependudukan
    is_verified = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), nullable=False, default='User') # Peran: 'User' atau 'SuperAdmin'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relasi one-to-many: satu user bisa memiliki banyak tiket.
    # `cascade` akan menghapus semua tiket user jika user tersebut dihapus.
    tickets = db.relationship('Ticket', backref='owner', lazy=True, cascade="all, delete-orphan")
    
    # Property 'password' digunakan untuk hashing otomatis saat password di-set.
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """Memverifikasi password yang diinput dengan hash di database."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Event(db.Model):
    """Model untuk data event atau konser."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    ticket_price = db.Column(db.Float, nullable=False)
    total_tickets = db.Column(db.Integer, nullable=False)
    tickets_sold = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(255), nullable=False, default='https://placehold.co/600x400/7c3aed/ffffff?text=JKT48+Event')
    
    # Relasi one-to-many: satu event memiliki banyak tiket.
    tickets = db.relationship('Ticket', backref='event_info', lazy=True, cascade="all, delete-orphan")

    def tickets_available(self):
        """Menghitung sisa tiket yang tersedia."""
        return self.total_tickets - self.tickets_sold

    def __repr__(self):
        return f'<Event {self.title}>'

class Ticket(db.Model):
    """Model untuk data tiket, representasi 'NFT' konseptual."""
    id = db.Column(db.Integer, primary_key=True)
    ticket_uid = db.Column(db.String(36), unique=True, nullable=False)
    nft_hash = db.Column(db.String(64), unique=True, nullable=False) # Hash SHA-256
    status = db.Column(db.String(20), nullable=False, default='Purchased') # Status: Purchased, Used, Expired
    purchase_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    qr_code_url = db.Column(db.String(255), nullable=True)

    # Foreign Key untuk menghubungkan tiket ke User dan Event.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

    def __init__(self, **kwargs):
        """
        Konstruktor untuk model Ticket.
        Secara otomatis membuat ticket_uid dan nft_hash saat objek baru dibuat.
        """
        super().__init__(**kwargs)
        # Pastikan ticket_uid dibuat jika belum ada saat objek diinisialisasi
        if not self.ticket_uid:
            self.ticket_uid = str(uuid.uuid4())
        # Buat hash setelah ticket_uid dijamin ada.
        self.generate_hash()

    def generate_hash(self):
        """
        Membuat hash unik (sidik jari digital) untuk tiket.
        PERBAIKAN: Hash sekarang dibuat HANYA dari ticket_uid.
        Karena ticket_uid dijamin unik (UUID), maka hash yang dihasilkan
        juga akan selalu unik. Ini adalah solusi definitif untuk error
        'Duplicate entry'.
        """
        data_to_hash = str(self.ticket_uid).encode('utf-8')
        self.nft_hash = hashlib.sha256(data_to_hash).hexdigest()

    def __repr__(self):
        return f'<Ticket {self.ticket_uid}>'
