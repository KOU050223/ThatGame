from apps.app import db
from sqlalchemy.sql import func

class Kweet(db.Model):
    __tablename__ = "kweet"
    id = db.Column(db.Integer,primary_key=True)
    message = db.Column(db.String)
    create_at = db.Column(db.DateTime,server_default=func.now())