from flask import Blueprint, render_template
from flask_login import login_required
from ..models import Item, Unit, AssetTransaction
from ..extensions import db

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/dashboard')
@login_required
def dashboard():
    # 1. Stats Counter
    total_items = Item.query.count()
    total_units = Unit.query.count()
    
    ready_count = Unit.query.filter_by(status='Ready').count()
    rented_count = Unit.query.filter_by(status='Rented').count()
    maintenance_count = Unit.query.filter_by(status='Maintenance').count()
    
    # Consolidated Stats for template
    stats_data = {
        'ready': ready_count,
        'rented': rented_count,
        'maintenance': maintenance_count,
        'total_units': total_units,
        'readiness_percent': round((ready_count / total_units * 100) if total_units > 0 else 0),
        'rented_percent': round((rented_count / total_units * 100) if total_units > 0 else 0),
        'maintenance_percent': round((maintenance_count / total_units * 100) if total_units > 0 else 0)
    }

    # 2. Distribution Data (by Category)
    categories = db.session.query(Item.category, db.func.count(Unit.id)).join(Unit).group_by(Item.category).all()
    dist_data = {cat: count for cat, count in categories}

    # 3. Recent Activity
    recent_transactions = AssetTransaction.query.order_by(AssetTransaction.timestamp.desc()).limit(5).all()

    # 4. Advanced Analytics (Phase 2 & 3)
    # 4.1. Top 5 Popular Items (Most Rented)
    popular_items = db.session.query(Item.name, db.func.count(AssetTransaction.id).label('rent_count'))\
        .join(Unit, Item.id == Unit.item_id)\
        .join(AssetTransaction, Unit.id == AssetTransaction.unit_id)\
        .filter(AssetTransaction.type == 'OUT')\
        .group_by(Item.name)\
        .order_by(db.text('rent_count DESC'))\
        .limit(5).all()

    # 4.2. Maintenance Watchist (Units often needing repair - heuristic)
    # We look for units with 'Maintenance' status or many 'IN' transactions with maintenance notes
    maintenance_watch = db.session.query(Item.name, db.func.count(Unit.id).label('m_count'))\
        .join(Unit)\
        .filter(Unit.status == 'Maintenance')\
        .group_by(Item.name)\
        .order_by(db.text('m_count DESC'))\
        .limit(5).all()

    # 4.3. Low Stock Alerts (Stock < 15% OR absolutely low)
    all_items_data = Item.query.all()
    low_stock_items = []
    for item in all_items_data:
        t_units = len(item.units)
        r_units = len([u for u in item.units if u.status == 'Ready'])
        if t_units > 0:
            ratio = r_units / t_units
            if ratio < 0.15 or r_units <= 1: # Alert if < 15% or only 1 left
                low_stock_items.append({
                    'name': item.name,
                    'available': r_units,
                    'total': t_units,
                    'percent': round(ratio * 100)
                })

    return render_template('dashboard.html', 
                         total_items=total_items,
                         stats=stats_data,
                         recent_transactions=recent_transactions,
                         dist_data=dist_data,
                         popular_items=popular_items,
                         maintenance_watch=maintenance_watch,
                         low_stock_items=low_stock_items)
