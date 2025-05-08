from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, FloatField, SelectField, DateField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from config import Config
from datetime import datetime, timedelta

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

class InventoryForm(FlaskForm):
    ingredient_name = StringField('Ingredient Name', validators=[DataRequired(), Length(max=100)])
    category = SelectField('Category', choices=Config.INGREDIENT_CATEGORIES, validators=[DataRequired()])
    quantity = FloatField('Quantity', validators=[DataRequired()])
    unit = SelectField('Unit', choices=Config.INGREDIENT_UNITS, validators=[DataRequired()])
    expiry_date = DateField('Expiry Date', format='%Y-%m-%d', validators=[Optional()])

class MealPlanForm(FlaskForm):
    recipe_id = HiddenField('Recipe ID', validators=[DataRequired()])
    day_of_week = SelectField('Day', choices=Config.DAYS_OF_WEEK, validators=[DataRequired()])
    meal_type = SelectField('Meal Type', choices=Config.MEAL_TYPES, validators=[DataRequired()])

class PreferencesForm(FlaskForm):
    vegetarian = BooleanField('Vegetarian')
    vegan = BooleanField('Vegan')
    gluten_free = BooleanField('Gluten Free')
    dairy_free = BooleanField('Dairy Free')

class RecipeCompleteForm(FlaskForm):
    servings = FloatField('Servings Made', validators=[DataRequired()], default=1)
