from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class TaskForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired(), Length(max=80)])
    description = TextAreaField('Описание')
    due_date = DateField('Дата выполнения', format='%Y-%m-%d', render_kw={'placeholder': 'YYYY-MM-DD'})
    location = StringField('Местоположение', validators=[Length(max=100)])
    submit = SubmitField('Сохранить задачу')

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=4, max=80)])
    password = StringField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = StringField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')