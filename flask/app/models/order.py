from app import db
from sqlalchemy_serializer import SerializerMixin
from .table import Table
from datetime import datetime

class Order(db.Model,SerializerMixin):
    __tablename__ = "orders"
    id = db.Column(db.Integer,primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey('tables.id'), nullable=True)  # รองรับ Takeaway (NULL)
    takeaway = db.Column(db.Boolean, default=False)  # เพิ่มตัวบอกว่าเป็น Takeaway ไหม
    food_status = db.Column(db.String(20))
    paid_status = db.Column(db.String(20))
    totalPrice = db.Column(db.Integer)
    order_time = db.Column(db.DateTime,default=datetime.utcnow)
    #soft delete
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    def __init__(self,table_id,takeaway,status,totalPrice,paid_status,order_time):
        self.table_id = table_id
        self.takeaway = takeaway
        self.food_status = status
        self.paid_status = paid_status
        self.totalPrice = totalPrice
        self.order_time = order_time

    @classmethod
    def active(cls):
        return cls.query.filter_by(is_deleted=False).all()  # กรองเฉพาะข้อมูลที่ยังไม่ถูกลบ
    
    @classmethod
    def nonActive(cls):
        return cls.query.filter_by(is_deleted=True).all()  # กรองเฉพาะข้อมูลที่ถูกลบ (soft delete)

    def update(self,status):
        self.status = status
        
    def delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()  # กำหนดเวลาเมื่อข้อมูลถูกลบ
        db.session.commit()

    # ฟังก์ชันที่ใช้ในการกู้คืนข้อมูล
    def restore(self):
        self.is_deleted = False
        self.deleted_at = None  # ลบวันที่ถูกลบเมื่อคืนข้อมูล
        db.session.commit()