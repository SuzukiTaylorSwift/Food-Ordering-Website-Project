from flask import (jsonify, render_template,
                  request, url_for, flash, redirect,send_file)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from datetime import datetime, timezone, timedelta


from sqlalchemy.sql import text
from flask_login import login_user, login_required, logout_user,current_user
from app import app
from app import db
from app import login_manager
#db
from app.models.authuser import AuthUser
from app.models.menu import Menu
from app.models.order_table import Order_table
from app.models.order import Order
from app.models.table import Table
#end db
from app.forms import MenuForm
import os
from app import scheduler
#excle
# import openpyxl
# from openpyxl import Workbook
# from datetime import datetime, timedelta
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine

#set time
# def job_function():
    # print("Job executed!")

# การตั้งเวลา job ทุก 1 นาที
# scheduler.add_job(id='my_job', func=job_function, trigger='interval', minutes=0.5)


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our
    # user table, use it in the query for the user
    return AuthUser.query.get(int(user_id))

@app.route('/')
def home():
    return "Flask says 'Hello world!'"

@app.route('/crash')
def crash():
    return 1/0

@app.route('/db')
def db_connection():
    try:
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return '<h1>db works.</h1>'
    except Exception as e:
        return '<h1>db is broken.</h1>' + str(e)


#db (upload)
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_image():
    if current_user.role != "admin":
        flash("You do not have permission.", 'error')
        return redirect(url_for('admin'))  # เปลี่ยนเส้นทางไปที่หน้าโปรไฟล์
    form = MenuForm()  # สร้างฟอร์มจาก MenuForm
    if form.validate_on_submit():  # ตรวจสอบว่าฟอร์มถูกส่งและผ่านการตรวจสอบ
        # ตรวจสอบว่าไฟล์ถูกส่งมาหรือไม่
        if 'image' not in request.files:
            return "No file part"
        
        file = form.image.data  # เข้าถึงไฟล์จากฟอร์ม
        if file.filename == '':
            return "ได้โปรดเลือกรูปภาพ"

        if file:
            filename = secure_filename(file.filename)  # ปลอดภัยในการตั้งชื่อไฟล์
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # สร้างไดเรกทอรีหากไม่มีก่อนที่จะบันทึก
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # บันทึกไฟล์
            file.save(file_path)
            
            # ดึงข้อมูลจากฟอร์ม
            name_food = form.nameFood.data
            type_food = form.type.data  # สามารถใช้ข้อมูลประเภทได้ตามต้องการ
            price = form.price.data
            options = form.options.data
            option = ''
            for i in options:
                option += i+" "
                
            print(option)
            # print(option)
            # สร้างวัตถุใหม่ในฐานข้อมูล
            new_image = Menu(nameFood=name_food, price=price,image_path=f"static/img/{filename}", type=type_food,option=option)  # บันทึกข้อมูลในฐานข้อมูล
            db.session.add(new_image)
            db.session.commit()

            return redirect(url_for('display_images'))  # เปลี่ยนไปที่หน้าที่แสดงภาพ

    return render_template('admin/upload_pages/upload.html', form=form)  # ส่งฟอร์มไปที่ template

@app.route('/images')
@login_required
def display_images():
    if current_user.role != "admin":
        flash("You do not have permission.", 'error')
        return redirect(url_for('admin'))  # เปลี่ยนเส้นทางไปที่หน้าโปรไฟล์
    images = Menu.query.all()
    for item in images:
        print(item.image_path)
    print(images)
    return render_template('admin/upload_pages/gallery.html', images=images)

@app.route('/delete_menu/<int:menu_id>', methods=['POST'])
@login_required
def delete_menu(menu_id):
    if current_user.role != "admin":
            flash("You do not have permission.", 'error')
            return redirect(url_for('admin'))  # เปลี่ยนเส้นทางไปที่หน้าโปรไฟล์
    
    menu_item = Menu.query.get_or_404(menu_id)

    # ลบไฟล์รูปภาพออกจากระบบ (ถ้ามี)
    if os.path.exists(menu_item.image_path):
        os.remove(menu_item.image_path)

    db.session.delete(menu_item)
    db.session.commit()

    return redirect(url_for('display_images'))

@app.route('/edit_menu/<int:menu_id>', methods=['GET', 'POST'])
@login_required
def edit_menu(menu_id):
    if current_user.role != "admin":
        print("eiei")
        flash("You do not have permission.", 'error')
        return redirect(url_for('admin'))  # เปลี่ยนเส้นทางไปที่หน้าโปรไฟล์
    menu_item = Menu.query.get_or_404(menu_id)  # ดึงข้อมูลเมนูจาก ID
    form = MenuForm(obj=menu_item)  # กำหนดค่าเริ่มต้นให้ฟอร์ม

    if form.validate_on_submit():
        # อัปเดตค่าต่าง ๆ
        menu_item.nameFood = form.nameFood.data
        menu_item.type = form.type.data
        menu_item.price = form.price.data
        options = form.options.data
        option = ""
        for i in options:
            option += i +" "
        menu_item.option = option
        # ตรวจสอบว่ามีการอัปโหลดไฟล์ใหม่หรือไม่
        if form.image.data:
            file = form.image.data
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # สร้างโฟลเดอร์ถ้ายังไม่มี
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # ลบรูปเดิมก่อน (ถ้ามี)
            if menu_item.image_path and os.path.exists(menu_item.image_path):
                os.remove(menu_item.image_path)

            file.save(file_path)
            menu_item.image_path = f"static/img/{filename}"  # อัปเดตพาธรูปภาพในฐานข้อมูล
        else:
            # ถ้าไม่มีการอัปโหลดใหม่ → ใช้รูปเดิม
            pass  

        db.session.commit()
        return redirect(url_for('display_images'))

    return render_template('admin/upload_pages/edit_menu.html', form=form, menu_item=menu_item)

#end upload
#client
@app.route('/takeAway', methods=['GET', 'POST'])
@login_required
def takeAway():
    if request.method == "POST":
        data = request.get_json()  # รับ JSON request
        print(data)
        print(data['table_id'], '------------------takeAway')

        # ตรวจสอบว่ามี "total_price" เป็น list หรือไม่
        total_price = sum(data["total_price"]) if isinstance(data["total_price"], list) else data["total_price"]

        # สร้างออเดอร์ใหม่
        newOrder = Order(table_id=data['table_id'], totalPrice=total_price,takeaway=True, status="Cooking",paid_status="Unpaid",order_time=data["time"])
        db.session.add(newOrder)
        db.session.commit()

      
        for i in range(len(data["menu_id"])):
            db.session.add(Order_table(menu_id=data["menu_id"][i],order_id=newOrder.id,quantity=data["quantity"][i],totalPrice=data["total_price"][i],option=data["option"][i],note=data["note"][i]))
            # db.session.add(order_table(menu_id=2,order_id=newOrder.id,quantity=3,totalPrice=500))
            db.session.commit()
        
    menus = Menu.query.all()
    return render_template("client_page/takeAway.html",menus = menus)
    

@app.route('/table<int:table_number>', methods=['GET', 'POST'])
def order_for_table(table_number):
    if(table_number <= 9 and table_number > 0):
        if request.method == "POST":
            data = request.get_json()  # รับ JSON request
            print(data)
            print(data['table_id'], 'aaaaaaaaaaaaaaaa')

            # ตรวจสอบว่ามี "total_price" เป็น list หรือไม่
            total_price = sum(data["total_price"]) if isinstance(data["total_price"], list) else data["total_price"]

            # สร้างออเดอร์ใหม่
            newOrder = Order(table_id=data['table_id'], totalPrice=total_price, status="Cooking",paid_status="Unpaid",takeaway=False,order_time=data["time"])
            db.session.add(newOrder)
            db.session.commit()

            # อัปเดตสถานะของโต๊ะเป็น "Taken"
            hi = Table.query.get(data['table_id'])
            if hi:
                hi.status = "Taken"  # เปลี่ยนค่าตรง ๆ แทน update()
                db.session.commit()
            
            # print(tables    )
            
            #12/2 3am
            for i in range(len(data["menu_id"])):
                db.session.add(Order_table(menu_id=data["menu_id"][i],order_id=newOrder.id,quantity=data["quantity"][i],totalPrice=data["total_price"][i],option=data["option"][i],note=data["note"][i] ))
                # db.session.add(order_table(menu_id=2,order_id=newOrder.id,quantity=3,totalPrice=500))
                db.session.commit()
            
        menus = Menu.query.all()
        return render_template("client_page/table.html",table_number = table_number,menus = menus)
    else:
        return "Table number not available", 404
    
    
#all menu
@app.route('/table/data')
@login_required
def all_menu():
    data = []
    db_contacts = Menu.query.all() 
    data = list(map(lambda x: x.to_dict(), db_contacts))
    app.logger.debug(f"DB Contacts: {data}")
    return jsonify(data)



# @app.route('/order_list',methods=["POST"])
# def orderList():
#     data = request.get_json()  # รับ JSON request
#     print(data,'aaaaaaaaaaaaaaaa')
#     # table = table_list(totalPrice=data["price"])
#     # db.session.add(table)
#     # db.session.commit()
#     return 'a'

#end client
#admin 
@app.route('/admin/lobby')
@login_required
def admin():
    
    return render_template('admin/lobby.html')


#all data
@app.route("/admin/all_data/<int:table_id>")
@login_required
def all_data(table_id):
    # ฟิลเตอร์ข้อมูลจาก Order โดยเลือกเฉพาะ order ที่มี table_id ตรงกับที่เลือก
    order = Order.query.filter(
            Order_table.is_deleted == False,
            Order.table_id == table_id,
            Order.paid_status != "Paided"
        ).all()
    
    # ฟิลเตอร์ข้อมูลจาก Order_table โดยเลือกเฉพาะที่มี order_id ตรงกับ id ของ order ที่เลือก
    order_list = Order_table.query.filter(Order_table.order_id.in_([o.id for o in order])).all()
    
    # ดึงแค่เมนูที่โต๊ะนั้นสั่ง
    menu_ids = [o.menu_id for o in order_list]
    menu = Menu.query.filter(Menu.id.in_(menu_ids)).all()
    print(order)
    # ส่งข้อมูลที่กรองมาไปยัง JSON format
    return jsonify({
        "order": [o.to_dict() for o in order],  
        "order_list": [o.to_dict() for o in order_list],  
        "menu": [m.to_dict() for m in menu]  
    })

#take home
@app.route("/admin/all_data")
@login_required
def all_data_takehome():
    # ฟิลเตอร์ข้อมูลจาก Order โดยเลือกเฉพาะ order ที่มี table_id ตรงกับที่เลือก
    order = Order.query.filter(
            Order_table.is_deleted == False,
            Order.table_id == None,
            Order.paid_status != "Paided"
        ).all()
    
    # ฟิลเตอร์ข้อมูลจาก Order_table โดยเลือกเฉพาะที่มี order_id ตรงกับ id ของ order ที่เลือก
    order_list = Order_table.query.filter(Order_table.order_id.in_([o.id for o in order])).all()
    
    # ดึงแค่เมนูที่โต๊ะนั้นสั่ง
    menu_ids = [o.menu_id for o in order_list]
    menu = Menu.query.filter(Menu.id.in_(menu_ids)).all()
    print(order)
    print(order_list)
    print(menu)
    # ส่งข้อมูลที่กรองมาไปยัง JSON format
    return jsonify({
        "order": [o.to_dict() for o in order],  
        "order_list": [o.to_dict() for o in order_list],  
        "menu": [m.to_dict() for m in menu]  
    })
    

@app.route("/admin/cashier", methods=['GET', 'POST'])
@login_required
def Cashier():
    if request.method == "POST":
        data = request.get_json()  
        print(data,"---------------- > data cashier")
        if data["table_id"] == None:
            table_id = None
        else:
            table_id = data.get('table_id') 
        order = Order.query.filter(
            Order_table.is_deleted == False,
            Order.table_id == table_id,
            Order.paid_status != "Paided"
        ).all()
        print(order,"orderrrrr",table_id) 
        for i in order:
            i.paid_status = "Paided"
            db.session.commit()
        hi = Table.query.get(table_id)
        if hi:
            hi.status = "Available"  # เปลี่ยนค่าตรง ๆ แทน update()
            db.session.commit()
        return "done"
            
                
    table = Table.query.order_by(Table.id).all()  # ดึงข้อมูลเรียงตาม id
    print(table)
    return render_template("admin/cashier.html",table=table)

@app.route("/admin/table_status")
@login_required
def table_status():
    tables = Table.query.all()
    table_data = {table.id: table.status for table in tables}
    return jsonify(table_data)

@app.route("/admin/serve", methods=['GET', 'POST'])
@login_required
def Server():
    if request.method == "POST":
        if request.method == "POST":
            result = request.get_json()
            print(result,'---------result by serve route')
            up = Order.query.get(result["id"])
            print(up)
            if up:
                up.food_status = "Complete"  # เปลี่ยนค่าตรง ๆ แทน update()
                db.session.commit()
            return "change already"
    else:
        db_order_list = Order_table.active() 
        db_order = Order.active()
        db_menu = Menu.query.all()
        # จัดกลุ่ม order_list ตาม table_id
        grouped_orders = {}
        for i in db_order_list:
            for j in db_order:
                if i.order_id == j.id and j.food_status == "Serving":
                    if j.id not in grouped_orders:
                        grouped_orders[j.id] = {"orders":[],"table_id":j.table_id,"order_time":j.order_time}
                    grouped_orders[j.id]["orders"].append(i)
        print(grouped_orders,"----------")
        print(db_menu)
        return render_template(
            "admin/serve.html",
            grouped_orders=grouped_orders,
            menu=db_menu
        )


    

@app.route("/admin/kitchen", methods=['GET', 'POST'])
@login_required
def Kitchen():
    if request.method == "POST":
        result = request.get_json()
        print(result,'---------result')
        up = Order.query.get(result["id"])
        print(up)
        if up:
            up.food_status = "Serving"  # เปลี่ยนค่าตรง ๆ แทน update()
            db.session.commit()
        return "change already"
    else:
        db_order_list = Order_table.active()
        db_order = Order.active()
        db_menu = Menu.query.all()
        # จัดกลุ่ม order_list ตาม table_id
        grouped_orders = {}
        for i in db_order_list:
            for j in db_order:
                if i.order_id == j.id and j.food_status == "Cooking":
                    if j.id not in grouped_orders:
                        grouped_orders[j.id] = {"orders":[],"table_id":j.table_id,"order_time":j.order_time}
                    grouped_orders[j.id]["orders"].append(i)
        print(grouped_orders,"----------")
        print(db_menu)
        return render_template(
            "admin/kitchen.html",
            grouped_orders=grouped_orders,
            menu=db_menu
        )
#hard delete
def hard_delete():
    from app import app  # Import Flask app

    with app.app_context():  # สร้าง application context
        print("Executing hard delete...")  # Debugging log
        THAILAND_TZ = timezone(timedelta(hours=7))  # Thailand time zone
        current_time = datetime.now(THAILAND_TZ)
        threshold_date = current_time - timedelta(days=2)
        
        # ลบ Order_table
        deleted_records = Order_table.query.filter(
            Order_table.is_deleted == True,
            Order_table.deleted_at < threshold_date
        ).all()
        for record in deleted_records:
            db.session.delete(record)
        db.session.commit()

        # ลบ Order
        deleted_records = Order.query.filter(
            Order.is_deleted == True,
            Order.deleted_at < threshold_date
        ).all()
        for record in deleted_records:
            db.session.delete(record)
        db.session.commit()

        print("-------hard delete completed-------")

#auto call hard delete function every day.
scheduler.add_job(id='delete', func=hard_delete, trigger='interval', days=1)

#soft delete
# @app.route("/restore-order/<int:order_id>", methods=["POST"])
@app.route("/restore-order/<int:order_id>", methods=["POST"])
@login_required
def restore_order(order_id):
    order = Order.query.get(order_id)
    if order:
        order.restore()
        return {"message": f"Order {order_id} has been restored."}, 200
    return {"error": "Order not found."}, 404

@app.route("/delete-order/<int:order_id>", methods=["POST"])
@login_required
def soft_delete_order(order_id):
    order = Order.query.get(order_id)
    if order:
        order.delete()
        return {"message": f"Order {order_id} has been marked as deleted."}, 200
    return {"error": "Order not found."}, 404

@app.route("/restore-order-list/<int:order_id>", methods=["POST"])
@login_required
def restore_order_list(order_id):
    order_list = Order_table.query.get(order_id)
    if order_list:
        order_list.restore()
        return {"message": f"Order {order_id} has been restored."}, 200
    return {"error": "Order not found."}, 404

@app.route("/delete-order-list/<int:order_id>", methods=["POST"])
@login_required
def soft_delete_order_list(order_id):
    order_list = Order_table.query.get(order_id)
    if order_list:
        order_list.delete()
        return {"message": f"Order {order_id} has been marked as deleted."}, 200
    return {"error": "Order not found."}, 404


@app.route("/record", methods=["GET","POST"])
@login_required
def save_data():
    
    data_list = []
    # ดึงข้อมูลจากฐานข้อมูล
    if request.method == "POST":
        order = Order.active()
        order_list = Order_table.active()
        menu = Menu.query.all()
        for i in order_list:
            
            soft_delete_order_list(i.id)
            # print(i)
        for i in order:
            # print(i)    
            soft_delete_order(i.id)
        print('---------------done soft delete')
        return "done soft delete"
        # return "done"    
        # print(data_list
    else:
        data_list = []
        order_list = Order_table.nonActive() 
        order = Order.nonActive()
        menu = Menu.query.all()
        for i in order_list:
            if order[i.order_id-1].takeaway == True:
                buy = "take home"
            else:
                buy = "eat in"
            data = {"ID": i.id, "menu": menu[i.menu_id-1].nameFood, "options": i.option,"note":i.note,"quantity":i.quantity,
                    "price":i.totalPrice,"buy":buy,"time":order[i.order_id-1].order_time}
            
            data_list.append(data)
        return render_template("record.html",data_list=data_list)

@app.route("/restore",methods=["POST"])
@login_required
def restore():
    order = Order.nonActive()
    order_list = Order_table.nonActive()
    for i in order:
        restore_order(i.id)
    for i in order_list:
        restore_order_list(i.id)
    return "done restore data"

#login page


@app.route('/admin/login', methods=('GET', 'POST'))
def admin_login():
    if request.method == 'POST':
        # login code goes here
        email = request.form.get('email')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))

        user = AuthUser.query.filter_by(email=email).first()
 
        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the
        # hashed password in the database
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            # if the user doesn't exist or password is wrong, reload the page
            return redirect(url_for('admin_login'))

        # if the above check passes, then we know the user has the right
        # credentials
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            #login done ->  lobby page
            next_page = url_for('admin')
        return redirect(next_page)

    return render_template('admin/login_pages/login.html')



@app.route('/admin/signup', methods=('GET', 'POST'))
@login_required
def admin_signup():
    if current_user.role != "admin":
        flash("You do not have permission.", 'error')
        return redirect(url_for('admin'))  # เปลี่ยนเส้นทางไปที่หน้าโปรไฟล์
    if request.method == 'POST':
        result = request.form.to_dict()
        app.logger.debug(str(result))
 
        validated = True
        validated_dict = {}
        valid_keys = ['email', 'name', 'password','role']

        # validate the input
        for key in result:
            app.logger.debug(str(key)+": " + str(result[key]))
            # screen of unrelated inputs
            if key not in valid_keys:
                continue

            value = result[key].strip()
            if not value or value == 'undefined':
                validated = False
                break
            validated_dict[key] = value
            # code to validate and add user to database goes here
        app.logger.debug("validation done")
        print(validated_dict)
        if validated:
            app.logger.debug('validated dict: ' + str(validated_dict))
            email = validated_dict['email']
            name = validated_dict['name']
            password = validated_dict['password']
            role = validated_dict['role']
            print(role)
            # if this returns a user, then the email already exists in database
            user = AuthUser.query.filter_by(email=email).first()

            if user:
                # if a user is found, we want to redirect back to signup
                # page so user can try again
                flash('Email address already exists')
                return redirect(url_for('admin_signup'))

            # create a new user with the form data. Hash the password so
            # the plaintext version isn't saved.
            app.logger.debug("preparing to add")
            avatar_url = gen_avatar_url(email, name)
            new_user = AuthUser(email=email, name=name,
                                password=generate_password_hash(
                                    password, method='sha256'),
                                avatar_url=avatar_url,role=role)
            # add the new user to the database
            db.session.add(new_user)
            db.session.commit()

        return redirect(url_for('admin_login'))
    return render_template('admin/login_pages/signup.html')

def gen_avatar_url(email, name):
    bgcolor = generate_password_hash(email, method='sha256')[-6:]
    color = hex(int('0xffffff', 0) -
                int('0x'+bgcolor, 0)).replace('0x', '')
    lname = ''
    temp = name.split()
    fname = temp[0][0]
    if len(temp) > 1:
        lname = temp[1][0]


    avatar_url = "https://ui-avatars.com/api/?name=" + \
        fname + "+" + lname + "&background=" + \
        bgcolor + "&color=" + color
    return avatar_url

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

#end login