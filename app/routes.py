# D:\jkt48-nft-app\app\routes.py
# File ini menangani rute-rute utama yang dapat diakses oleh semua pengguna,
# termasuk fitur verifikasi tiket publik yang baru ditambahkan.

from flask import Blueprint, render_template, redirect, url_for, flash, abort, session, request, current_app
from flask_login import current_user, login_required
from app.models import Event, Ticket, User
from app import db
from datetime import datetime, timezone
import qrcode
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
def index():
    """Menampilkan halaman utama (homepage)."""
    upcoming_events = Event.query.filter(Event.date >= datetime.now(timezone.utc)).order_by(Event.date.asc()).limit(3).all()
    return render_template('index.html', title='Selamat Datang', events=upcoming_events)

@main_bp.route('/events')
def events():
    """Menampilkan semua event yang akan datang."""
    all_upcoming_events = Event.query.filter(Event.date >= datetime.now(timezone.utc)).order_by(Event.date.asc()).all()
    return render_template('events.html', title='Semua Event', events=all_upcoming_events)

@main_bp.route('/event/<int:event_id>')
def event_detail(event_id):
    """Menampilkan halaman detail untuk satu event spesifik."""
    event = Event.query.get_or_404(event_id)
    return render_template('event_detail.html', title=event.title, event=event)

@main_bp.route('/verify', methods=['GET', 'POST'])
def verify():
    """Menangani halaman verifikasi tiket untuk publik."""
    ticket_identifier = None
    ticket_to_verify = None

    if request.method == 'POST':
        ticket_identifier = request.form.get('ticket_identifier', '').strip()
    elif request.method == 'GET':
        ticket_identifier = request.args.get('ticket_identifier', '').strip()

    if ticket_identifier:
        # Cari tiket berdasarkan Ticket UID atau NFT Hash
        ticket_to_verify = Ticket.query.filter(
            (Ticket.ticket_uid == ticket_identifier) | (Ticket.nft_hash == ticket_identifier)
        ).first()
        
        if ticket_to_verify:
            flash('Tiket berhasil ditemukan dan terverifikasi keasliannya.', 'success')
        else:
            # Hanya tampilkan pesan 'tidak ditemukan' jika ada input dari pengguna
            flash('Tiket dengan kode tersebut tidak ditemukan di sistem kami.', 'danger')
    elif request.method == 'POST':
        flash('Harap masukkan Kode Unik atau Hash Tiket.', 'warning')
        
    return render_template('verify.html', title='Verifikasi Keaslian Tiket', ticket=ticket_to_verify)

@main_bp.route('/checkout/<int:event_id>', methods=['POST'])
@login_required
def checkout(event_id):
    """Menangani proses saat pengguna menekan tombol 'Beli Tiket'."""
    event = Event.query.get_or_404(event_id)
    
    if not current_user.nik or len(current_user.nik) != 16:
        flash('Anda harus melengkapi NIK di profil Anda sebelum membeli tiket.', 'warning')
        return redirect(url_for('main.profile'))
        
    if event.tickets_available() <= 0:
        flash('Maaf, tiket untuk event ini sudah habis.', 'danger')
        return redirect(url_for('main.event_detail', event_id=event.id))
    
    session['checkout_event_id'] = event.id
    
    return render_template('checkout.html', title='Konfirmasi Pembelian', event=event)

@main_bp.route('/process_payment', methods=['POST'])
@login_required
def process_payment():
    """Memproses simulasi pembayaran dan membuat tiket."""
    event_id = session.get('checkout_event_id')
    if not event_id:
        flash('Sesi checkout tidak valid atau telah kedaluwarsa.', 'danger')
        return redirect(url_for('main.events'))

    event = Event.query.get_or_404(event_id)

    if event.tickets_available() <= 0:
        flash('Sayang sekali! Tiket habis terjual saat Anda memproses pembayaran.', 'danger')
        return redirect(url_for('main.event_detail', event_id=event.id))

    try:
        # 1. Buat instance tiket baru. `ticket_uid` akan dibuat secara otomatis oleh model.
        new_ticket = Ticket(owner=current_user, event_info=event)
        # 2. Pembuatan `ticket_uid` dan `nft_hash` sekarang ditangani secara otomatis
        #    di dalam konstruktor (__init__) model Ticket.
        
        # 3. Buat QR code menggunakan `ticket_uid` yang sudah ada dan siapkan URL-nya.
        qr_data = new_ticket.ticket_uid
        qr_img = qrcode.make(qr_data)
        
        qr_code_dir = os.path.join(current_app.root_path, 'static/qrcodes')
        if not os.path.exists(qr_code_dir):
            os.makedirs(qr_code_dir)
            
        qr_filename = f'{new_ticket.ticket_uid}.png'
        qr_filepath = os.path.join(qr_code_dir, qr_filename)
        qr_img.save(qr_filepath)
        new_ticket.qr_code_url = f'qrcodes/{qr_filename}'
        
        # 4. Setelah semua atribut tiket (hash, qr_code_url) terisi,
        # tambahkan objek ke sesi, perbarui jumlah tiket terjual, dan commit.
        db.session.add(new_ticket)
        event.tickets_sold += 1
        
        db.session.commit()
        
        flash('Pembayaran berhasil! Tiket Anda telah diterbitkan.', 'success')
        session.pop('checkout_event_id', None)
        # Atribut `new_ticket.id` akan terisi secara otomatis setelah commit berhasil.
        return redirect(url_for('main.ticket_detail', ticket_id=new_ticket.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Terjadi kesalahan saat menerbitkan tiket: {e}', 'danger')
        return redirect(url_for('main.event_detail', event_id=event.id))

@main_bp.route('/my_tickets')
@login_required
def my_tickets():
    """Menampilkan semua tiket yang dimiliki oleh pengguna yang sedang login."""
    tickets = Ticket.query.filter_by(user_id=current_user.id).order_by(Ticket.purchase_date.desc()).all()
    return render_template('my_tickets.html', title='Tiket Saya', tickets=tickets)

@main_bp.route('/ticket/<int:ticket_id>')
@login_required
def ticket_detail(ticket_id):
    """Menampilkan detail dari satu tiket spesifik."""
    ticket = Ticket.query.get_or_404(ticket_id)
    if ticket.user_id != current_user.id and current_user.role != 'SuperAdmin':
        abort(403)
    return render_template('ticket_detail.html', title='Detail Tiket', ticket=ticket)

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Menampilkan dan memproses pembaruan profil pengguna."""
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name')
        nik_input = request.form.get('nik')

        if not current_user.is_verified:
            if nik_input and len(nik_input) == 16 and nik_input.isdigit():
                existing_nik = User.query.filter(User.nik == nik_input, User.id != current_user.id).first()
                if existing_nik:
                    flash('NIK ini sudah terdaftar pada akun lain.', 'danger')
                else:
                    current_user.nik = nik_input
                    current_user.is_verified = True
                    flash('Profil berhasil diperbarui dan NIK telah diverifikasi!', 'success')
            else:
                flash('NIK harus terdiri dari 16 digit angka.', 'warning')
        else:
            flash('Profil berhasil diperbarui.', 'success')
        
        db.session.commit()
        return redirect(url_for('main.profile'))

    return render_template('profile.html', title='Profil Saya')
