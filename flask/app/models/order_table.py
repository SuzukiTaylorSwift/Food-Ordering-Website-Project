from app import db
from sqlalchemy_serializer import SerializerMixin
from .menu import Menu
from .order import Order
#middle table
class Order_table(db.Model,SerializerMixin):
    __tablename__ = "order_tables"
    id = db.Column(db.Integer, primary_key=True)  # หมายเลขโต๊ะ
    menu_id = db.Column(db.Integer,db.ForeignKey('menus.id'))
    order_id  = db.Column(db.Integer,db.ForeignKey('orders.id'))
    totalPrice = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    option = db.Column(db.String(50))
    note = db.Column(db.String(75))
    
    def __init__(self, menu_id, order_id, totalPrice,quantity,option,note):
        self.menu_id = menu_id
        self.order_id = order_id
        self.totalPrice = totalPrice
        self.quantity = quantity
        self.option = option
        self.note = note