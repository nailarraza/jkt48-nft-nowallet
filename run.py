# D:\jkt48-nft-app\run.py
# File ini adalah titik masuk (entry point) untuk menjalankan aplikasi Flask.
# MODIFIKASI: Menambahkan fungsi untuk membuat SuperAdmin default saat aplikasi pertama kali dijalankan.

from app import create_app, db
import os
from app.models import User, Event, Ticket 

# Membuat instance aplikasi menggunakan factory function
app = create_app()

def create_initial_user(app_instance):
    """
    Fungsi ini akan membuat SuperAdmin 'owner@razagopo.my.id' jika belum ada di database.
    Ini akan berjalan setiap kali aplikasi dimulai, tetapi hanya akan membuat
    user satu kali.
    """
    with app_instance.app_context():
        # Ambil email dan password dari environment variables
        admin_email = os.environ.get('DEFAULT_ADMIN_EMAIL', 'owner@razagopo.my.id')
        admin_password = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'razagopo')

        if not admin_password:
            print("Peringatan: DEFAULT_ADMIN_PASSWORD tidak diatur di environment variable. SuperAdmin tidak akan dibuat.")
            return

        # Cek apakah user dengan email 'owner@razagopo.my.id' sudah ada
        admin_user = User.query.filter_by(email=admin_email).first()
        
        if not admin_user:
            print(f"Menciptakan user SuperAdmin default: {admin_email}")
            # Membuat instance user baru
            new_admin = User(
                username='minjot', # Username unik untuk admin
                email=admin_email,
                full_name='JKT48 Operation Team',
                role='SuperAdmin',
                is_verified=True # Admin langsung terverifikasi
            )
            # Mengatur password (akan di-hash oleh model)
            new_admin.password = admin_password
            
            # Menambahkan dan menyimpan ke database
            db.session.add(new_admin)
            db.session.commit() 
            print(f"User SuperAdmin '{admin_email}' berhasil dibuat.")

# Panggil fungsi untuk membuat user admin saat aplikasi start
create_initial_user(app)

# Menambahkan konteks ke shell Flask untuk mempermudah debugging.
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Event': Event, 'Ticket': Ticket}

# Blok ini akan dieksekusi hanya jika skrip dijalankan secara langsung
if __name__ == '__main__':
    # Menjalankan server pengembangan Flask
    app.run(host='0.0.0.0', port=5001, debug=True)
