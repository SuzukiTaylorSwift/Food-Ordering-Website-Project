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
    image = FileField('เลือกรูปภาพ', validators=[DataRequired()])
    submit = SubmitField('บันทึก')

# <form
#       action="{{ url_for('upload_image') }}"
#       method="POST"
#       enctype="multipart/form-data"
#     >
#       <input type="file" name="image" required />
#       <button type="submit">Upload</button>
#     </form>