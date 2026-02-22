import os
import re
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from sqlalchemy.exc import IntegrityError
from ..models import Item, Unit, AssetTransaction
from ..extensions import db
from ..utils.image_handler import save_picture, delete_old_picture
from ..utils import log_activity, is_nonsensical

items = Blueprint('items', __name__)

@items.route('/')
@items.route('/items')
@login_required
def items_list():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Maksimal 10 item per halaman

    query = Item.query

    if search:
        query = query.filter(Item.name.contains(search))
    if category:
        query = query.filter(Item.category == category)
    
    # Filter by unit status if needed (complex query)
    if status:
        # Get items that have units with matching status
        items_with_status = db.session.query(Item.id).join(Unit).filter(Unit.status == status).distinct()
        query = query.filter(Item.id.in_(items_with_status))
    
    # Pagination
    pagination = query.order_by(Item.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    items_found = pagination.items

    return render_template('items.html', 
                           items=items_found, 
                           pagination=pagination,
                           search=search,
                           category=category,
                           status=status)


@items.route('/item/add', methods=['GET', 'POST'])
@login_required
def add_item():
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        quantity = int(request.form.get('quantity', 1))
        initial_status = request.form.get('status', 'Ready')
        description = request.form.get('description', '')
        
        # 1. Validation: Prevent "Data Aneh"
        if not name or not name.strip():
            flash('Nama alat tidak boleh kosong.', 'error')
            return redirect(request.url)
        
        # Anti Key-Mashing
        is_bad, msg = is_nonsensical(name)
        if is_bad:
            flash(msg, 'error')
            return redirect(request.url)
        
        if len(name.strip()) < 3:
            flash('Nama alat terlalu pendek (minimal 3 karakter).', 'error')
            return redirect(request.url)
            
        if quantity < 1:
            flash('Jumlah unit minimal adalah 1.', 'error')
            return redirect(request.url)

        # Save image if uploaded
        image_file = 'default.jpg'
        if 'image' in request.files and request.files['image'].filename != '':
            image_file = save_picture(request.files['image'])

        # Smart Add: Check if item exists
        item = Item.query.filter_by(name=name.strip()).first()
        if not item:
            item = Item(name=name.strip(), category=category, description=description, image_file=image_file)
            db.session.add(item)
            db.session.flush() # Get ID before commit
        else:
            # Update existing item image if a new one was uploaded
            if image_file != 'default.jpg':
                delete_old_picture(item.image_file)
                item.image_file = image_file
        
        # Auto-increment SN logic
        prefixes = {
            'Lighting': 'LGT',
            'Audio': 'AUD',
            'Multimedia': 'MUL',
            'Stage Production': 'STG',
            'Power Generator': 'PWR'
        }
        prefix = prefixes.get(category, 'OTH')
        
        # Inisial Barang (e.g., Mixer -> MI, Moving Head -> MH)
        words = name.strip().split()
        item_code = "".join([w[0].upper() for w in words]) if len(words) > 1 else name.strip()[:2].upper()
        
        # Cari nomor urut terakhir khusus untuk item ini
        last_unit = Unit.query.filter(Unit.serial_number.like(f"{prefix}-{item_code}-%")).order_by(Unit.id.desc()).first()
        next_num = 1
        if last_unit:
            match = re.search(r'-(\d+)$', last_unit.serial_number)
            if match:
                next_num = int(match.group(1)) + 1
        
        try:
            for i in range(quantity):
                sn = f"{prefix}-{item_code}-{next_num + i}"
                new_unit = Unit(item_id=item.id, serial_number=sn, status=initial_status)
                db.session.add(new_unit)
            
            db.session.commit()
            log_activity('Tambah Barang', f'Menambah {quantity} unit untuk "{name}" ({category})')
            flash(f'Berhasil menambah {quantity} unit untuk "{name}".', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Gagal menambah barang: Serial Number sudah terdaftar di sistem.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
            
        return redirect(url_for('items.items_list'))

    item_names = [i.name for i in Item.query.all()]
    return render_template('add_item.html', item_names=item_names)

@items.route('/item/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    if request.method == 'POST':
        new_name = request.form.get('name', '').strip()
        new_category = request.form.get('category')
        new_description = request.form.get('description', '').strip()
        add_stock_qty = int(request.form.get('add_quantity', 0))

        # Validation
        if not new_name:
            flash('Nama alat tidak boleh kosong.', 'error')
            return redirect(request.url)
        
        # Anti Key-Mashing
        is_bad, msg = is_nonsensical(new_name)
        if is_bad:
            flash(msg, 'error')
            return redirect(request.url)
            
        if len(new_name) < 3:
            flash('Nama alat terlalu pendek (minimal 3 karakter).', 'error')
            return redirect(request.url)

        if add_stock_qty < 0:
            flash('Jumlah stok tambahan tidak boleh negatif.', 'error')
            return redirect(request.url)

        item.name = new_name
        item.category = new_category
        item.description = new_description
        add_stock = add_stock_qty
        
        # 1. Update Serial Numbers if name or category changed (Cascade)
        prefixes = {
            'Lighting': 'LGT',
            'Audio': 'AUD',
            'Multimedia': 'MUL',
            'Stage Production': 'STG',
            'Power Generator': 'PWR'
        }
        prefix = prefixes.get(item.category, 'OTH')
        
        # Recalculate Initial Barang
        words = item.name.split()
        item_code = "".join([w[0].upper() for w in words]) if len(words) > 1 else item.name[:2].upper()
        
        for unit in item.units:
            match = re.search(r'-(\d+)$', unit.serial_number)
            if match:
                # Update prefix and item code but keep the unique sequence number
                unit.serial_number = f"{prefix}-{item_code}-{match.group(1)}"
        
        # 2. Add new stock if requested
        if add_stock > 0:
            # Cari nomor urut terakhir khusus untuk item ini (setelah pembaruan SN di atas)
            last_unit = Unit.query.filter(Unit.serial_number.like(f"{prefix}-{item_code}-%")).order_by(Unit.id.desc()).first()
            next_num = 1
            if last_unit:
                match = re.search(r'-(\d+)$', last_unit.serial_number)
                if match:
                    next_num = int(match.group(1)) + 1
            
            for i in range(add_stock):
                sn = f"{prefix}-{item_code}-{next_num + i}"
                new_unit = Unit(item_id=item.id, serial_number=sn, status='Ready')
                db.session.add(new_unit)

        # 3. Update Status of existing units
        for unit in item.units:
            new_status = request.form.get(f'status_{unit.id}')
            if new_status:
                unit.status = new_status
        
        try:
            db.session.commit()
            log_activity('Ubah Barang', f'Memperbarui data item ID: {item_id} ("{item.name}")')
            flash('Data barang berhasil diperbaharui.', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Gagal memperbarui: Serial Number duplikat ditemukan.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal memperbarui: {str(e)}', 'error')
            
        return redirect(url_for('items.items_list'))

    return render_template('edit_item.html', item=item)

@items.route('/item/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    try:
        # Delete image if not default
        delete_old_picture(item.image_file)
        
        # Explicitly clean up related transactions from raw tables if needed
        # (Though cascade should handle it via AssetTransaction)
        db.session.delete(item)
        db.session.commit()
        log_activity('Hapus Barang', f'Menghapus item: "{item.name}" (ID: {item_id})')
        flash('Barang dan semua unitnya berhasil dihapus.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Gagal menghapus: {str(e)}', 'error')
    return redirect(url_for('items.items_list'))
