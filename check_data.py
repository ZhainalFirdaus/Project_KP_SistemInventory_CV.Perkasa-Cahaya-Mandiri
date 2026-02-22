from inventory_app import create_app
from inventory_app.models import AssetTransaction, ActivityLog

app = create_app()
with app.app_context():
    print("=== TRANSAKSI TERBARU ===")
    trans = AssetTransaction.query.order_by(AssetTransaction.timestamp.desc()).limit(5).all()
    for t in trans:
        print(f"{t.timestamp} | {t.type} | SN: {t.unit.serial_number}")
    
    print("\n=== ACTIVITY LOG TERBARU ===")
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(5).all()
    for l in logs:
        details = l.details[:50] if l.details else "-"
        print(f"{l.timestamp} | {l.action} | {details}")
    
    print(f"\nTotal Transaksi: {AssetTransaction.query.count()}")
    print(f"Total Activity Log: {ActivityLog.query.count()}")
