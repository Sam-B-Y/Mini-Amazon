from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, TextAreaField, URLField, SubmitField
from wtforms.validators import DataRequired, URL, NumberRange

class InventoryForm(FlaskForm):
    category_name = StringField('Category Name', validators=[DataRequired()])
    name = StringField('Product Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image_url = URLField('Image URL', validators=[DataRequired(), URL()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Add to Inventory') 