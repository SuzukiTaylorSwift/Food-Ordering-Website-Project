from app import db
from sqlalchemy_serializer import SerializerMixin

class table(db.Model,SerializerMixin):
    __tablename__ = "tables"
    id = db.Column(db.Integer,primary_key=True)
    status = db.Column(db.String(20))
    def __init__(self,status):
        self.status = status
