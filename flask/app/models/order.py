from app import db
from sqlalchemy_serializer import SerializerMixin
from .table import table
from datetime import datetime

class order(db.Model,SerializerMixin):
    __tablename__ = "orders"
    id = db.Column(db.Integer,primary_key=True)
    table_id = db.Column(db.Integer,db.ForeignKey('tables.id'))
    status = db.Column(db.String(20))
    totalPrice = db.Column(db.Integer)
    order_time = db.Column(db.DateTime,default=datetime.utcnow)
    
    def __init__(self,table_id,status,totalPrice):
        self.table_id = table_id
        self.status = status
        self.totalPrice = totalPrice

    def update(self,status):
        self.status = status