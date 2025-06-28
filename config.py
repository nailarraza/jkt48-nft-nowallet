# D:\jkt48-nft-app\config.py
# File ini bertanggung jawab untuk memuat konfigurasi aplikasi.
# MODIFIKASI: Menambahkan logika untuk membuat SECRET_KEY yang aman secara otomatis.

import os
import secrets # Modul untuk menghasilkan data acak yang aman secara kriptografis
from dotenv import load_dotenv

# Menentukan direktori dasar proyek
basedir = os.path.abspath(os.path.dirname(__file__))
# Memuat variabel dari file .env
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """
    Kelas konfigurasi utama.
    Mengambil nilai dari environment variables atau membuatnya jika tidak ada.
    """
    # Coba ambil SECRET_KEY dari environment variable
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Jika SECRET_KEY tidak ditemukan di file .env (misalnya, saat pertama kali setup)
    if not SECRET_KEY:
        # Generate sebuah kunci acak yang aman (32 bytes, direpresentasikan sebagai 64 karakter hex)
        SECRET_KEY = secrets.token_hex(32)
        
        # Berikan peringatan dan kunci yang dihasilkan di terminal
        print("="*80)
        print("PERINGATAN: SECRET_KEY tidak ditemukan di file .env.")
        print("Sebuah kunci sementara yang aman telah dibuat secara otomatis untuk sesi ini.")
        print("Untuk penggunaan di lingkungan produksi atau jika Anda ingin sesi tetap")
        print("bertahan setelah server restart, Anda HARUS menyalin baris berikut")
        print("ke dalam file .env Anda:")
        print(f"SECRET_KEY='{SECRET_KEY}'")
        print("="*80)

    # URI untuk koneksi ke database MySQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    
    # Nonaktifkan fitur tracking modifikasi SQLAlchemy untuk menghemat resource
    SQLALCHEMY_TRACK_MODIFICATIONS = False
