# D:\jkt48-nft-app\app\admin_routes.py
# File ini berisi semua rute yang hanya boleh diakses oleh SuperAdmin.
# Ini termasuk dashboard, manajemen event (CRUD), dan verifikasi tiket.

from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app import db
from app.models import Event, Ticket, User
from functools import wraps
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# Membuat decorator custom untuk memproteksi rute admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Jika pengguna tidak login atau perannya bukan SuperAdmin, tolak akses.
        if not current_user.is_authenticated or current_user.role != 'SuperAdmin':
            abort(403) # Error 403: Forbidden
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Menampilkan halaman dashboard admin."""
    total_events = Event.query.count()
    total_users = User.query.count()
    total_tickets = Ticket.query.count()
    return render_template('admin/dashboard.html', title='Admin Dashboard', total_events=total_events, total_users=total_users, total_tickets=total_tickets)

@admin_bp.route('/manage-events')
@login_required
@admin_required
def manage_events():
    """Menampilkan halaman untuk mengelola semua event."""
    events = Event.query.order_by(Event.date.desc()).all()
    return render_template('admin/manage_events.html', title='Kelola Event', events=events)

@admin_bp.route('/add-event', methods=['GET', 'POST'])
@login_required
@admin_required
def add_event():
    """Menampilkan form dan memproses penambahan event baru."""
    if request.method == 'POST':
        try:
            # Mengambil data dari form
            title = request.form.get('title')
            description = request.form.get('description')
            date_str = request.form.get('date')
            date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M') # Konversi string ke objek datetime
            location = request.form.get('location')
            ticket_price = float(request.form.get('ticket_price'))
            total_tickets = int(request.form.get('total_tickets'))
            image_url = request.form.get('image_url')

            new_event = Event(
                title=title,
                description=description,
                date=date,
                location=location,
                ticket_price=ticket_price,
                total_tickets=total_tickets,
                image_url=image_url if image_url else 'https://placehold.co/600x400/DC143C/FFFFFF?text=Event'
            )
            db.session.add(new_event)
            db.session.commit()
            flash('Event baru berhasil ditambahkan!', 'success')
            return redirect(url_for('admin.manage_events'))
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan: {e}', 'danger')
            
    return render_template('admin/add_event.html', title='Tambah Event Baru')


@admin_bp.route('/edit-event/<int:event_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_event(event_id):
    """Menampilkan form dan memproses pengeditan event yang ada."""
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        try:
            event.title = request.form.get('title')
            event.description = request.form.get('description')
            date_str = request.form.get('date')
            event.date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            event.location = request.form.get('location')
            event.ticket_price = float(request.form.get('ticket_price'))
            event.total_tickets = int(request.form.get('total_tickets'))
            event.image_url = request.form.get('image_url')
            
            db.session.commit()
            flash('Event berhasil diperbarui!', 'success')
            return redirect(url_for('admin.manage_events'))
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan saat memperbarui: {e}', 'danger')

    # Format tanggal agar sesuai dengan value input 'datetime-local'
    form_date = event.date.strftime('%Y-%m-%dT%H:%M')
    return render_template('admin/edit_event.html', title='Edit Event', event=event, form_date=form_date)

@admin_bp.route('/delete-event/<int:event_id>', methods=['POST'])
@login_required
@admin_required
def delete_event(event_id):
    """Memproses penghapusan event."""
    event = Event.query.get_or_404(event_id)
    try:
        db.session.delete(event)
        db.session.commit()
        flash('Event berhasil dihapus.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Gagal menghapus event: {e}', 'danger')
    return redirect(url_for('admin.manage_events'))

@admin_bp.route('/verify-ticket', methods=['GET', 'POST'])
@login_required
@admin_required
def verify_ticket():
    """Menampilkan halaman verifikasi tiket dan mencari tiket."""
    ticket_to_verify = None
    if request.method == 'POST':
        ticket_identifier = request.form.get('ticket_identifier')
        if not ticket_identifier:
            flash('Harap masukkan Kode Unik atau Hash Tiket.', 'warning')
        else:
            # Cari tiket berdasarkan Ticket UID atau NFT Hash
            ticket_to_verify = Ticket.query.filter(
                (Ticket.ticket_uid == ticket_identifier) | (Ticket.nft_hash == ticket_identifier)
            ).first()
            if not ticket_to_verify:
                flash('Tiket tidak ditemukan.', 'danger')

    return render_template('admin/verify_ticket.html', title='Verifikasi Tiket', ticket=ticket_to_verify)


@admin_bp.route('/mark-ticket-used/<int:ticket_id>', methods=['POST'])
@login_required
@admin_required
def mark_ticket_used(ticket_id):
    """Memproses check-in dengan mengubah status tiket menjadi 'Used'."""
    ticket = Ticket.query.get_or_404(ticket_id)
    if ticket.status == 'Purchased':
        ticket.status = 'Used'
        db.session.commit()
        flash(f'Tiket {ticket.ticket_uid} berhasil ditandai sebagai "Telah Digunakan".', 'success')
    elif ticket.status == 'Used':
        flash(f'Tiket {ticket.ticket_uid} sudah pernah digunakan sebelumnya.', 'warning')
    else:
        flash(f'Tiket ini tidak bisa digunakan (status: {ticket.status}).', 'danger')

    # Redirect kembali ke halaman verify dengan data tiket yang sama untuk dilihat hasilnya
    return redirect(url_for('admin.verify_ticket', ticket_identifier=ticket.ticket_uid))
