from flask import (jsonify, render_template,
                  request, url_for, flash, redirect,send_file)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
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
#HW
# from app.models.contact import Contact

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


#db
@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    form = MenuForm()  # สร้างฟอร์มจาก MenuForm
    if form.validate_on_submit():  # ตรวจสอบว่าฟอร์มถูกส่งและผ่านการตรวจสอบ
        # ตรวจสอบว่าไฟล์ถูกส่งมาหรือไม่
        if 'image' not in request.files:
            return "No file part"
        
        file = form.image.data  # เข้าถึงไฟล์จากฟอร์ม
        if file.filename == '':
            return "No selected file"

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
            # สร้างวัตถุใหม่ในฐานข้อมูล
            new_image = Menu(nameFood=name_food, price=price,image_path=f"static/img/{filename}", type=type_food)  # บันทึกข้อมูลในฐานข้อมูล
            db.session.add(new_image)
            db.session.commit()

            return redirect(url_for('display_images'))  # เปลี่ยนไปที่หน้าที่แสดงภาพ

    return render_template('upload.html', form=form)  # ส่งฟอร์มไปที่ template

@app.route('/images')
def display_images():
    images = Menu.query.all()
    for item in images:
        print(item.image_path)
    print(images)
    return render_template('gallery.html', images=images)

#client

@app.route('/table<int:table_number>', methods=['GET', 'POST'])
def order_for_table(table_number):
    if(table_number <= 9 and table_number > 0):
        if request.method == "POST":
            data = request.get_json()  # รับ JSON request
            print(data,'aaaaaaaaaaaaaaaa')
            newOrder = Order(table_id=data[0][3],totalPrice=data[0][1],status="Cooking")
            db.session.add(newOrder)
            db.session.commit()
            validated_dict = {}
            validated_dict["status"] = "Taken"
            hi = Table.query.get(data[0][3])
            if hi:
                hi.update(**validated_dict)
                db.session.commit()
                        
            # print(tables    )
            for item in data:
                print(item)
                db.session.add(Order_table(menu_id=item[4],order_id=newOrder.id,quantity=item[2],totalPrice=200))
                # db.session.add(order_table(menu_id=2,order_id=newOrder.id,quantity=3,totalPrice=500))
                db.session.commit()
            
            return "a"
        menus = Menu.query.all()
        return render_template("table.html",table_number = table_number,menus = menus)
    else:
        return "Table number not available", 404
    
    
#all menu
@app.route('/table/data')
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
def admin():
    return render_template('admin/lobby.html')

@app.route("/admin/cashier")
def Cashier():
    return render_template("admin/cashier.html")

@app.route("/admin/serve", methods=['GET', 'POST'])
def Server():
    if request.method == "POST":
        print("post request for serving")
        result = request.get_json()
        print(result)
        app.logger.debug(str(result))

        id_ = result.get('id', '')
        if not id_:
            return jsonify({"error": "Missing ID"}), 400  # เช็คว่า id_ มีค่าจริงหรือไม่

        validated = True
        validated_dict = dict()
        valid_keys = ['status']

        # Validate input
        for key in result:
            app.logger.debug(f"{key}: {result[key]}")
            if key not in valid_keys:
                continue
            value = result[key].strip()
            if not value or value == 'undefined':
                validated = False
                break
            validated_dict[key] = value

        if not validated_dict:  
            return jsonify({"error": "No valid data received"}), 400  # ป้องกัน validated_dict ว่าง

        print(validated_dict, "11111111111111111111111")
        print(id_)
        # **สามารถเพิ่มโค้ดอัปเดต database ได้ที่นี่**
        hi = Order.query.get(id_)
        if hi:
            hi.update(**validated_dict)
            db.session.commit()
        # return render_template("admin/serve.html")
        return jsonify({"success": True, "data": validated_dict})
    else:
        db_order_list = Order_table.query.all() 
        db_order = Order.query.all()
        db_menu = Menu.query.all()
        filter_order = []

        for i in db_order:
            # หาคำสั่งที่มีสถานะ "Serving"
            order_info = next((o for o in db_order if o.status == "Serving" and o == i), None)
            
            if order_info:  # ถ้ามี order_info ที่ตรงกับเงื่อนไข
                print(i, order_info, "eiieieieie")
                filter_order.append(order_info)

        print(filter_order)

        return render_template(
            "admin/serve.html",
            menu=db_menu,
            order=filter_order,
            order_list = db_order_list
        )

        

@app.route("/admin/kitchen", methods=['GET', 'POST'])
def Kitchen():
        
    db_order_list = Order_table.query.all() 
    db_order = Order.query.all()
    db_menu = Menu.query.all()
    # return render_template("admin/kitchen.html" , order_list=db_order_list,menu=db_menu,order=db_order)
    # จัดกลุ่ม order_list ตาม table_id
    grouped_orders = {}
    for i in db_order_list:
        order_info = next((o for o in db_order if o.id == i.order_id), None)
        if order_info:
            table_id = order_info.table_id
            if table_id not in grouped_orders:
                grouped_orders[table_id] = {
                    "orders": [],
                    "order_time": order_info.order_time,
                }
            grouped_orders[table_id]["orders"].append({
                "menu_id": i.menu_id,
                "quantity": i.quantity,
            })
    print(grouped_orders,'tttttttttttttttttt')
    return render_template(
        "admin/kitchen.html",
        grouped_orders=grouped_orders,
        menu=db_menu
    )





@app.route('/lab11')
def lab11_index():
    print('aaa')
    return render_template('lab11/index.html')

@app.route('/lab11/login', methods=('GET', 'POST'))
def lab11_login():
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
            return redirect(url_for('lab11_login'))

        # if the above check passes, then we know the user has the right
        # credentials
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            #login done -> profile lobby page
            next_page = url_for('lab11_profile')
        return redirect(next_page)

    return render_template('lab11/login.html')

@app.route('/lab11/profile')
def lab11_profile():
   return render_template('lab11/profile.html')


@app.route('/lab11/signup', methods=('GET', 'POST'))
@login_required
def lab11_signup():
    role = AuthUser.query.all()
    # print(current_user.role == "admin")
    if current_user.role != "admin":
        # flash("You do not have permission to signup.", 'error') ทำไม่ได้
        return redirect(url_for('lab11_profile'))  # เปลี่ยนเส้นทางไปที่หน้าโปรไฟล์
    
    print(role)
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
                return redirect(url_for('lab11_signup'))

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

        return redirect(url_for('lab11_login'))
    return render_template('lab11/signup.html')

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

@app.route('/lab11/logout')
@login_required
def lab11_logout():
    logout_user()
    return redirect(url_for('lab11_index'))

#end login
