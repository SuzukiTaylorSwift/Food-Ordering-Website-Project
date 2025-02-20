from app import db
from sqlalchemy_serializer import SerializerMixin
from .menu import Menu
from .order import Order
from datetime import datetime
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
    #soft delete
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    @classmethod
    def active(cls):
        return cls.query.filter_by(is_deleted=False).all()  # กรองเฉพาะข้อมูลที่ยังไม่ถูกลบ
    
    @classmethod
    def nonActive(cls):
        return cls.query.filter_by(is_deleted=True).all()  # กรองเฉพาะข้อมูลที่ถูกลบ (soft delete)

    def __init__(self, menu_id, order_id, totalPrice,quantity,option,note):
        self.menu_id = menu_id
        self.order_id = order_id
        self.totalPrice = totalPrice
        self.quantity = quantity
        self.option = option
        self.note = note
        
    def delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()  # กำหนดเวลาเมื่อข้อมูลถูกลบ
        db.session.commit()

    # ฟังก์ชันที่ใช้ในการกู้คืนข้อมูล
    def restore(self):
        self.is_deleted = False
        self.deleted_at = None  # ลบวันที่ถูกลบเมื่อคืนข้อมูล
        db.session.commit()