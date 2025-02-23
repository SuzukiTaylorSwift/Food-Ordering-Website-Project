from app import db
from sqlalchemy_serializer import SerializerMixin

class Menu(db.Model,SerializerMixin):
    __tablename__ = 'menus'

    id = db.Column(db.Integer, primary_key=True)
    nameFood = db.Column(db.String(255), nullable=False)
    # description = db.Column(db.Text)
    price = db.Column(db.Integer)
    image_path = db.Column(db.String(255))
    type = db.Column(db.String(30))
    option = db.Column(db.String(75))
    
    def __init__(self, nameFood, price,type,option ,image_path=None):
        self.nameFood = nameFood
        self.price = price
        self.image_path = image_path
        self.type = type
        self.option = option

    # def __init__(self, image_path):
    #     self.image_path = image_path
    def update(self, nameFood, price, type,option,image_path=None ):
        self.nameFood = nameFood
        self.price = price
        if image_path:
            self.image_path = image_path
        self.type = type
        self.option = option
