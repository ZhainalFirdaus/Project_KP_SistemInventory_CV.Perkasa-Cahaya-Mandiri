import pandas as pd
import io
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from ..models import Item, Unit
from ..extensions import db
from ..utils import log_activity, is_nonsensical
from datetime import datetime

bulk = Blueprint('bulk', __name__)

@bulk.route('/bulk')
@login_required
def bulk_home():
    return render_template('bulk_ops.html')

@bulk.route('/bulk/export')
@login_required
def export_assets():
    # Fetch all data
    items = Item.query.all()
    data = []
    for item in items:
        for unit in item.units:
            data.append({
                'Item Name': item.name,
                'Category': item.category,
                'Serial Number': unit.serial_number,
                'Status': unit.status,
                'Last Check In': unit.last_check_in.strftime('%Y-%m-%d %H:%M:%S') if unit.last_check_in else ''
            })
    
    df = pd.DataFrame(data)
    
    # Save to buffer
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Assets')
    
    output.seek(0)
    log_activity('Bulk Export', 'Mengekspor data aset ke Excel')
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f"PCM_Assets_{datetime.now().strftime('%Y%m%d')}.xlsx"
    )

@bulk.route('/bulk/import', methods=['POST'])
@login_required
def import_assets():
    import re
    if 'file' not in request.files:
        flash('Tidak ada file yang diunggah.', 'error')
        return redirect(url_for('bulk.bulk_home'))
    
    file = request.files['file']
    if file.filename == '':
        flash('File tidak valid.', 'error')
        return redirect(url_for('bulk.bulk_home'))

    try:
        df = pd.read_excel(file)
        # Required columns (Serial Number is now optional)
        required = ['Item Name', 'Category']
        if not all(col in df.columns for col in required):
            flash(f"Kolom wajib tidak ditemukan. Header harus minimal: {', '.join(required)}", 'error')
            return redirect(url_for('bulk.bulk_home'))

        processed = 0
        added_items = 0
        added_units = 0
        skipped = 0
        
        # SN Prefix Map
        prefixes = {
            'Lighting': 'LGT',
            'Audio': 'AUD',
            'Multimedia': 'MUL',
            'Multimedia System': 'MUL',
            'Stage Production': 'STG',
            'Power Generator': 'PWR'
        }
        
        # Local counter cache to handle multiple units of same item in one batch
        next_nums_cache = {}

        for _, row in df.iterrows():
            item_name = str(row['Item Name']).strip()
            category = str(row['Category']).strip()
            sn = str(row.get('Serial Number', '')).strip()
            if sn == 'nan': sn = '' # Handle pandas NaN
            status = str(row.get('Status', 'Ready')).strip()

            # Anti Key-Mashing Validation
            is_bad, _ = is_nonsensical(item_name)
            if is_bad or len(item_name) < 3:
                skipped += 1
                continue

            # 1. Get or Create Item
            item = Item.query.filter_by(name=item_name).first()
            if not item:
                item = Item(name=item_name, category=category)
                db.session.add(item)
                db.session.flush() # Get ID
                added_items += 1
            
            # 2. Logic for SN if missing
            if not sn:
                prefix = prefixes.get(category, 'OTH')
                
                # Inisial Barang
                words = item_name.split()
                item_code = "".join([w[0].upper() for w in words]) if len(words) > 1 else item_name[:2].upper()
                
                cache_key = (prefix, item_code)
                if cache_key not in next_nums_cache:
                    # Cari nomor urut terakhir khusus untuk item ini di DB
                    last_unit = Unit.query.filter(Unit.serial_number.like(f"{prefix}-{item_code}-%")).order_by(Unit.id.desc()).first()
                    next_num = 1
                    if last_unit:
                        match = re.search(r'-(\d+)$', last_unit.serial_number)
                        if match:
                            next_num = int(match.group(1)) + 1
                    next_nums_cache[cache_key] = next_num
                
                sn = f"{prefix}-{item_code}-{next_nums_cache[cache_key]}"
                next_nums_cache[cache_key] += 1

            # 3. Get or Create Unit
            unit = Unit.query.filter_by(serial_number=sn).first()
            if not unit:
                unit = Unit(item_id=item.id, serial_number=sn, status=status)
                db.session.add(unit)
                added_units += 1
            else:
                # Update status of existing unit if provided
                unit.status = status
            
            processed += 1
        
        db.session.commit()
        msg = f'Impor selesai! {added_items} Item baru dan {added_units} Unit baru ditambahkan.'
        if skipped > 0:
            msg += f' ({skipped} baris dilewati karena data tidak valid/asal-asalan).'
        
        log_activity('Bulk Import', f'Berhasil mengimpor {processed} entri')
        flash(msg, 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Gagal memproses file: {str(e)}', 'error')
        
    return redirect(url_for('bulk.bulk_home'))
