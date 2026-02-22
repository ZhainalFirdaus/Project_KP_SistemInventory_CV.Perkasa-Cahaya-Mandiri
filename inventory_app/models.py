from datetime import datetime
from flask_login import UserMixin
from .extensions import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    image_file = db.Column(db.String(100), default='default_user.jpg')

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), nullable=False, index=True) # Lighting, Audio, Multimedia System
    description = db.Column(db.Text)
    image_file = db.Column(db.String(100), default='default.jpg')
    units = db.relationship('Unit', backref='item', lazy=True, cascade="all, delete-orphan")

class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    serial_number = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(20), default='Ready', index=True) # 'Ready', 'Rented', 'Maintenance'
    last_check_in = db.Column(db.DateTime, default=datetime.utcnow)
    transactions = db.relationship('AssetTransaction', backref='unit', lazy=True, cascade="all, delete-orphan")

class AssetTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)
    type = db.Column(db.String(10), nullable=False, index=True) # 'OUT', 'IN'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    notes = db.Column(db.String(255))
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    admin = db.relationship('User', backref='transactions', lazy=True)

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False) # e.g., 'DELETE_ITEM', 'EDIT_UNIT', 'LOGIN'
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user = db.relationship('User', backref='activities', lazy=True)
