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
    
    def __init__(self, nameFood, price,type ,image_path=None):
        self.nameFood = nameFood
        self.price = price
        self.image_path = image_path
        self.type = type

    # def __init__(self, image_path):
    #     self.image_path = image_path
    def update(self, nameFood, price, type,image_path=None):
        self.nameFood = nameFood
        self.price = price
        if image_path:
            self.image_path = image_path
        self.type = type
        
# class table_list(db.Model,SerializerMixin):
#     __tablename__ = "table_lists"
#     id = db.Column(db.Integer,primary_key=True)
#     totalPrice = db.Column(db.Integer)
#     def __init__(self,totalPrice):
#         self.totalPrice = totalPrice

# #middle table
# class order_table(db.Model,SerializerMixin):
#     __tablename__ = "order_tables"
#     id = db.Column(db.Integer, primary_key=True)  # หมายเลขโต๊ะ
#     menu_id = db.Column(db.Integer,db.ForeignKey('menus.id'))
#     table_id  = db.Column(db.Integer,db.ForeignKey('table_lists.id'))
#     totalPrice = db.Column(db.Integer)
#     def __init__(self, table_id, menu_id, totalPrice):
#         self.table_id = table_id
#         self.menu_id = menu_id
#         self.totalPrice = totalPrice
