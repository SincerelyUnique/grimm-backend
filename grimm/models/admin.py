from grimm import db
from sqlalchemy import func


class Admin(db.Model):
    __tablename__ = 'ADMIN'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    registration_date = db.Column(db.DateTime, default=func.now(), nullable=False)
    password = db.Column(db.String, default=0, nullable=False)
    name = db.Column(db.String(100))
    email = db.Column(db.String(32), unique=True)
    email_verified = db.Column(db.Integer)


class User(db.Model):
    __tablename__ = 'USER'
    openid = db.Column(db.String(28), primary_key=True, nullable=False)
    registration_date = db.Column(db.DateTime, nullable=False)
    role = db.Column(db.Integer)
    name = db.Column(db.String(100))
    real_name = db.Column(db.String(100))
    id_type = db.Column(db.String(100))
    idcard = db.Column(db.String(18))
    idcard_verified = db.Column(db.Integer)
    disabled_id = db.Column(db.String(60))
    disabled_id_verified = db.Column(db.Integer)
    phone = db.Column(db.String(16))
    phone_verified = db.Column(db.Integer)
    email = db.Column(db.String(32))
    email_verified = db.Column(db.Integer)
    contact = db.Column(db.String(16))
    gender = db.Column(db.String(1))
    birth = db.Column(db.DateTime)
    address = db.Column(db.String(80))
    emergent_contact = db.Column(db.String(8))
    emergent_contact_phone = db.Column(db.String(16))
    activities_joined = db.Column(db.Integer)
    activities_absence = db.Column(db.Integer)
    remark = db.Column(db.String(255))
    audit_status = db.Column(db.Integer)
    push_status = db.Column(db.Integer)
    recipient_name = db.Column(db.String(100))
    recipient_address = db.Column(db.String(80))
    recipient_phone = db.Column(db.String(16))
