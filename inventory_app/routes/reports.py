import csv
import io
from flask import Blueprint, render_template, make_response, request, flash, redirect, url_for
from flask_login import login_required
from datetime import datetime, timedelta
from ..models import AssetTransaction, Unit, ActivityLog
from ..extensions import db

reports_blueprint = Blueprint('reports', __name__)

@reports_blueprint.route('/reports')
@login_required
def reports():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    search_query = request.args.get('q', '').strip()
    
    query = AssetTransaction.query
    if start_date:
        query = query.filter(AssetTransaction.timestamp >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        query = query.filter(AssetTransaction.timestamp <= end_dt)
        
    if search_query:
        # Search by Serial Number or Item Name
        from ..models import Item
        query = query.join(Unit).join(Item).filter(
            db.or_(
                Unit.serial_number.ilike(f"%{search_query}%"),
                Item.name.ilike(f"%{search_query}%"),
                AssetTransaction.notes.ilike(f"%{search_query}%")
            )
        )
        
    transactions = query.order_by(AssetTransaction.timestamp.desc()).all()

    total_out = Unit.query.filter_by(status='Rented').count()
    total_repair = Unit.query.filter_by(status='Maintenance').count()
    
    # Chart Data
    weekly_data = {'labels': [], 'outbound': [], 'inbound': []}
    today = datetime.utcnow()
    for i in range(3, -1, -1):
        end_of_week = today - timedelta(days=today.weekday()) + timedelta(days=6) - timedelta(weeks=i)
        start_of_week = (end_of_week - timedelta(days=6)).replace(hour=0, minute=0, second=0)
        end_of_week = end_of_week.replace(hour=23, minute=59, second=59)
        
        label = "This Week" if i == 0 else f"Week {4-i}"
        weekly_data['labels'].append(label)
        
        out_count = AssetTransaction.query.filter(AssetTransaction.type == 'OUT', AssetTransaction.timestamp >= start_of_week, AssetTransaction.timestamp <= end_of_week).count()
        in_count = AssetTransaction.query.filter(AssetTransaction.type == 'IN', AssetTransaction.timestamp >= start_of_week, AssetTransaction.timestamp <= end_of_week).count()
        
        weekly_data['outbound'].append(out_count)
        weekly_data['inbound'].append(in_count)
    
    return render_template('reports.html', 
                           total_out=total_out, 
                           total_repair=total_repair, 
                           transactions=transactions, 
                           weekly_data=weekly_data, 
                           now=datetime.utcnow(), 
                           start_date=start_date, 
                           end_date=end_date,
                           search_query=search_query)

@reports_blueprint.route('/reports/export/<type>')
@login_required
def export_reports(type):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    search_query = request.args.get('q', '').strip()
    
    query = AssetTransaction.query
    if start_date:
        query = query.filter(AssetTransaction.timestamp >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        query = query.filter(AssetTransaction.timestamp <= end_dt)
        
    if search_query:
        from ..models import Item
        query = query.join(Unit).join(Item).filter(
            db.or_(
                Unit.serial_number.ilike(f"%{search_query}%"),
                Item.name.ilike(f"%{search_query}%"),
                AssetTransaction.notes.ilike(f"%{search_query}%")
            )
        )

    transactions = query.order_by(AssetTransaction.timestamp.desc()).all()
    
    if type == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Serial Number', 'Item Name', 'Timestamp', 'Type', 'Notes', 'Admin'])
        
        for t in transactions:
            writer.writerow([t.unit.serial_number, t.unit.item.name, t.timestamp.strftime('%Y-%m-%d %H:%M'), t.type, t.notes, t.admin.username if t.admin else 'Unknown'])
            
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=log_mutasi_pemanahan.csv"
        response.headers["Content-type"] = "text/csv"
        return response
    
    return redirect(url_for('reports.reports'))

@reports_blueprint.route('/activity-log')
@login_required
def activity_log():
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(200).all()
    return render_template('activity_log.html', logs=logs, now=datetime.utcnow())

@reports_blueprint.route('/activity-log/clear', methods=['POST'])
@login_required
def clear_activity_log():
    try:
        # Log the action before clearing if possible, or just clear
        # Since we are clearing the WHOLE table, we might want to log it to a different system or just proceed.
        # Here we just clear the table.
        ActivityLog.query.delete()
        db.session.commit()
        
        # Log that the logs were cleared (this will be the only/first log entry now)
        log_activity('Reset Riwayat', f'User {current_user.username} menghapus seluruh riwayat aktivitas')
        
        flash('Seluruh riwayat aktivitas berhasil dihapus.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Gagal menghapus riwayat: {str(e)}', 'error')
    
    return redirect(url_for('reports.activity_log'))
