from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FileField, SubmitField,RadioField,SelectField
from wtforms.validators import DataRequired

class MenuForm(FlaskForm):
    #... = ...(label,)
    nameFood = StringField('ชื่ออาหาร', validators=[DataRequired()])
    price = IntegerField('ราคา', validators=[DataRequired()])
    # type = RadioField('Level',
    #                    choices=['food', 'drink', 'appetizer'],
    #                    validators=[DataRequired()])
    #(value,label)
    type = SelectField('Type', choices=[('drink', 'Drink'), ('food', 'Food'),("appetizer",'Appetizer')], validators=[DataRequired()])
    
    image = FileField('เลือกรูปภาพ')
    # option_size = SelectField('Size', choices=[('Regular', 'Regular'), ('Large', 'Large')], validators=[DataRequired()])
    # Spice_Levels = SelectField('Spice', choices=[('Not Spicy', 'Not Spicy'), ('Mild', 'Mild'),('Medium','Medium'),('Spicy','Spicy')], validators=[DataRequired()])
    submit = SubmitField('บันทึก')
# Not Spicy – ไม่เผ็ด
# Mild – เผ็ดน้อย
# Medium – เผ็ดกลาง
# Spicy / Hot – เผ็ด
# Extra Spicy / Very Hot – เผ็ดมาก
# Super Spicy / Extreme – เผ็ดสุด ๆ 🔥🔥
# <form
#       action="{{ url_for('upload_image') }}"
#       method="POST"
#       enctype="multipart/form-data"
#     >
#       <input type="file" name="image" required />
#       <button type="submit">Upload</button>
#     </form>