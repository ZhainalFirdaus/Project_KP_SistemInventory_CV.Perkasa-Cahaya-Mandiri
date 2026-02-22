from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from datetime import datetime
from ..models import Item, Unit, AssetTransaction
from ..extensions import db
from ..utils import generate_surat_jalan_pdf, log_activity, is_nonsensical
import io

transactions = Blueprint('transactions', __name__)

@transactions.route('/out', methods=['GET', 'POST'])
@login_required
def transaction_out():
    if request.method == 'POST':
        selected_unit_ids = request.form.getlist('unit_ids')
        event_name = request.form.get('event_name', '').strip()
        location = request.form.get('location', '').strip()
        
        # Validation: Prevent "Data Aneh"
        if not event_name or len(event_name) < 3:
            flash('Nama Event tidak valid (minimal 3 karakter).', 'error')
            return redirect(request.url)
            
        is_bad_event, msg_event = is_nonsensical(event_name)
        if is_bad_event:
            flash(f"Event: {msg_event}", 'error')
            return redirect(request.url)
            
        if not location:
            flash('Lokasi event wajib diisi.', 'error')
            return redirect(request.url)
            
        is_bad_loc, msg_loc = is_nonsensical(location)
        if is_bad_loc:
            flash(f"Lokasi: {msg_loc}", 'error')
            return redirect(request.url)
            
        if not selected_unit_ids:
            flash('Pilih minimal satu unit untuk dikeluarkan.', 'error')
            return redirect(request.url)
            
        try:
            processed_count = 0
            for uid in selected_unit_ids:
                unit = Unit.query.get(uid)
                if unit and unit.status == 'Ready':
                    full_notes = f"Event: {event_name} @ {location}"
                    new_trans = AssetTransaction(
                        unit_id=unit.id,
                        type='OUT',
                        notes=full_notes,
                        admin_id=current_user.id
                    )
                    unit.status = 'Rented'
                    db.session.add(new_trans)
                    processed_count += 1
            
            db.session.commit()
            if processed_count > 0:
                log_activity('Transaksi Keluar', f'Mengeluarkan {processed_count} unit untuk event: "{event_name}"')
                flash(f'Berhasil mengeluarkan {processed_count} unit untuk "{event_name}".', 'success')
                return redirect(url_for('transactions.print_surat_jalan_prompt', event=event_name, loc=location, count=processed_count))
            return redirect(url_for('transactions.transaction_in'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan: {str(e)}', 'error')
            return redirect(request.url)

    # GET: Item selection and FIFO list
    item_id = request.args.get('item_id')
    selected_item = None
    fifo_units = []
    
    if item_id:
        selected_item = Item.query.get(item_id)
        if selected_item:
            fifo_units = Unit.query.filter_by(item_id=item_id, status='Ready')\
                .order_by(Unit.last_check_in.asc()).all()
    
    all_items = Item.query.all()
    return render_template('transaction_out.html', items=all_items, selected_item=selected_item, fifo_units=fifo_units, now=datetime.utcnow())

@transactions.route('/in', methods=['GET', 'POST'])
@login_required
def transaction_in():
    if request.method == 'POST':
        selected_unit_ids = request.form.getlist('unit_ids')
        event_origin = request.form.get('event_origin', '').strip()
        location_origin = request.form.get('location_origin', '').strip()
        
        # Validation: Prevent "Data Aneh"
        if not event_origin or len(event_origin) < 3:
            flash('Data Event asal tidak valid (minimal 3 karakter).', 'error')
            return redirect(request.url)
            
        is_bad, msg = is_nonsensical(event_origin)
        if is_bad:
            flash(f"Event: {msg}", 'error')
            return redirect(request.url)
            
        if not selected_unit_ids:
            flash('Tidak ada unit yang dipilih untuk dikembalikan.', 'error')
            return redirect(request.url)
            
        try:
            processed = 0
            for uid in selected_unit_ids:
                unit = Unit.query.get(uid)
                if unit and unit.status == 'Rented':
                    condition = request.form.get(f'condition_{uid}', 'Good')
                    note = request.form.get(f'note_{uid}', '')
                    
                    new_status = 'Ready' if condition == 'Good' else 'Maintenance'
                    trans_note = f"Kembali dari: {event_origin} ({location_origin}). Kondisi: {condition}. {note}"
                    
                    new_trans = AssetTransaction(
                        unit_id=unit.id,
                        type='IN',
                        notes=trans_note,
                        admin_id=current_user.id
                    )
                    
                    unit.status = new_status
                    unit.last_check_in = datetime.utcnow()
                    db.session.add(new_trans)
                    processed += 1
            
            db.session.commit()
            log_activity('Transaksi Masuk', f'Memproses {processed} unit masuk dari event: "{event_origin}"')
            flash(f'{processed} unit berhasil diproses (Masuk Gudang).', 'success')
            return redirect(url_for('transactions.transaction_in'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal memproses: {str(e)}', 'error')
    
    # GET: Load items for selection
    item_id = request.args.get('item_id')
    selected_item = None
    rented_units = []
    
    if item_id:
        selected_item = Item.query.get(item_id)
        if selected_item:
            rented_units = Unit.query.filter_by(item_id=item_id, status='Rented').all()
            
    # Logic for Auto-Suggestion: Fetch unique events from currently rented units
    import re
    active_events = []
    # Get the latest 'OUT' transaction for each currently rented unit
    rented_transactions = db.session.query(AssetTransaction.notes)\
        .join(Unit, AssetTransaction.unit_id == Unit.id)\
        .filter(Unit.status == 'Rented', AssetTransaction.type == 'OUT')\
        .distinct().all()
    
    seen = set()
    for row in rented_transactions:
        note = row[0]
        match = re.search(r'Event: (.*) @ (.*)', note)
        if match:
            event_name = match.group(1).strip()
            location = match.group(2).strip()
            key = (event_name, location)
            if key not in seen:
                active_events.append({'event': event_name, 'location': location})
                seen.add(key)
                
    all_items = Item.query.all()
    return render_template('transaction_in.html', 
                          items=all_items, 
                          selected_item=selected_item, 
                          rented_units=rented_units, 
                          active_events=active_events,
                          now=datetime.utcnow())

@transactions.route('/print-prompt')
@login_required
def print_surat_jalan_prompt():
    event = request.args.get('event')
    loc = request.args.get('loc')
    count = request.args.get('count')
    return render_template('print_prompt.html', event=event, loc=loc, count=count)

@transactions.route('/export-pdf')
@login_required
def export_surat_jalan():
    event = request.args.get('event')
    loc = request.args.get('loc')
    
    # Fetch recent OUT transactions for this event (heuristic based on timestamp and notes)
    # In a real app, we'd use a unique Batch ID, but we'll filter by notes and recent time.
    recent_transactions = AssetTransaction.query.filter(
        AssetTransaction.type == 'OUT',
        AssetTransaction.notes.contains(event)
    ).order_by(AssetTransaction.timestamp.desc()).limit(50).all()
    
    unit_list = []
    for t in recent_transactions:
        unit_list.append({
            'sn': t.unit.serial_number,
            'name': t.unit.item.name,
            'category': t.unit.item.category
        })
    
    if not unit_list:
        flash("Tidak ada data transaksi untuk diekspor.", "error")
        return redirect(url_for('reports.reports'))

    pdf_content = generate_surat_jalan_pdf(
        event_name=event,
        location=loc,
        admin_name=current_user.username,
        unit_list=unit_list
    )
    
    log_activity('Ekspor PDF', f'Mengekspor Surat Jalan untuk event: "{event}"')
    return send_file(
        io.BytesIO(pdf_content),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"Surat_Jalan_{event.replace(' ', '_')}.pdf"
    )

# API untuk QR Scanner - Cari unit berdasarkan Serial Number
@transactions.route('/api/lookup-unit/<sn>')
@login_required
def lookup_unit_by_sn(sn):
    from flask import jsonify
    unit = Unit.query.filter_by(serial_number=sn).first()
    
    if not unit:
        return jsonify({'found': False, 'message': f'Unit dengan SN {sn} tidak ditemukan di database.'})
    
    return jsonify({
        'found': True,
        'unit_id': unit.id,
        'serial_number': unit.serial_number,
        'status': unit.status,
        'item_id': unit.item_id,
        'item_name': unit.item.name,
        'category': unit.item.category
    })

