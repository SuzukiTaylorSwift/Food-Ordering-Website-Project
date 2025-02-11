from flask.cli import FlaskGroup
from flask import url_for
from werkzeug.security import generate_password_hash
from app import app, db
from app.models.menu import Menu
from app.models.authuser import AuthUser
from app.models.order import Order
from app.models.order_table import Order_table
from app.models.table import Table
import os

cli = FlaskGroup(app)

@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

@cli.command("seed_db")
def seed_db():
    db.session.add(AuthUser(email="aheye@gmail.com", name='Aheye',
                            password=generate_password_hash('1234',
                                                            method='sha256'),
                            avatar_url='https://ui-avatars.com/api/?name=\
Aheye&background=83ee03&color=fff',role="admin"))
    # print(img,'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
    # image_path = url_for('static', filename='img/aheye.png')
    new_menu = Menu(nameFood="Haerin",price=1000,type="drink",image_path="static/img/download.jpg")
    db.session.add(new_menu)
    new_menu = Menu(nameFood="E here Eye",price=5,type="naHee",image_path="static/img/aheye.png")
    db.session.add(new_menu)
    #ถ้ามีโต๊ะเพิ่มจะทำยังไงวะน้อง
    for i in range(9):
        print(i)
        db.session.add(Table(status="Available"))
    # db.session.add(table_list(totalPrice=100))
    # db.session.add(table_list(totalPrice=1000))
    # db.session.commit()
    # db.session.commit()
    # db.session.add(order_table(table_id=1,order_id=2,totalPrice=200))
    # db.session.add(order_table(totalPrice=5,menu_id=1,table_id=1))
    # db.session.add(order(table_id=2,totalPrice=200,status="young"))
   
    db.session.commit()
    
    


if __name__ == "__main__":
    cli()