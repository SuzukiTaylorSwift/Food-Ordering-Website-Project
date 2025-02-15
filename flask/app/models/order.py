from app import db
from sqlalchemy_serializer import SerializerMixin
from .table import Table
from datetime import datetime

class Order(db.Model,SerializerMixin):
    __tablename__ = "orders"
    id = db.Column(db.Integer,primary_key=True)
    table_id = db.Column(db.Integer,db.ForeignKey('tables.id'))
    food_status = db.Column(db.String(20))
    paid_status = db.Column(db.String(20))
    totalPrice = db.Column(db.Integer)
    order_time = db.Column(db.DateTime,default=datetime.utcnow)
    
    def __init__(self,table_id,status,totalPrice,paid_status):
        self.table_id = table_id
        self.food_status = status
        self.paid_status = paid_status
        self.totalPrice = totalPrice

    def update(self,status):
        self.status = status