from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from forms import TaskForm, RegistrationForm, LoginForm
from models import db, Task, User
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from datetime import datetime
import requests

app = Flask(__name__)

# Конфигурация приложения Flask
app.config['SECRET_KEY'] = 'ваш_секретный_ключ'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@host:port/database_name'
# Если вы временно используете SQLite:
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem' # Используем файловую систему для хранения сессий
db.init_app(app)

# Создание таблиц базы данных при первом запуске приложения
with app.app_context():
    db.create_all()


def get_coordinates(city_name):
    """Получает географические координаты для заданного названия города."""
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': city_name,
        'format': 'json',
        'limit': 1
    }
    headers = {
        'User-Agent': 'Task Manager App (your_email@example.com)'  # <---- ВАЖНО: Замените на свой email или название приложения
    }
    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
        else:
            print(f"Не удалось найти координаты для города: {city_name}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API геокодирования: {e}")
        return None
    except Exception as e:
        print(f"Ошибка при обработке ответа API геокодирования: {e}")
        return None

def get_weather(latitude, longitude):
    """Получает текущую погоду по заданным географическим координатам с Open-Meteo."""
    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'current_weather': True,
        'temperature_unit': 'celsius',
        'windspeed_unit': 'kmh',
        'precipitation_unit': 'mm',
        'language': 'ru'
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        weather_data = response.json()
        return weather_data.get('current_weather') # Используем .get() чтобы избежать KeyError
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API погоды Open-Meteo: {e}")
        return None
    except Exception as e:
        print(f"Ошибка при обработке ответа API погоды Open-Meteo: {e}")
        return None

@app.route('/')
def index():
    """Отображает список всех задач с информацией о погоде (если указано местоположение)."""
    tasks = Task.query.all()
    weather_info = {} # Словарь для хранения информации о погоде для каждого местоположения
    for task in tasks:
        if task.location:
            if task.location not in weather_info:
                coordinates = get_coordinates(task.location)
                if coordinates:
                    latitude, longitude = coordinates
                    weather_data = get_weather(latitude, longitude)
                    weather_info[task.location] = weather_data
                else:
                    weather_info[task.location] = None
    return render_template('index.html', tasks=tasks, weather_info=weather_info)





@app.route('/new_task', methods=['GET', 'POST'])
def new_task():
    """Отображает форму для создания новой задачи и обрабатывает ее отправку."""
    form = TaskForm() # Создаем экземпляр формы TaskForm
    if form.validate_on_submit(): # Проверяем, была ли отправлена форма и все ли поля прошли валидацию
        title = form.title.data
        description = form.description.data
        due_date = form.due_date.data
        location = form.location.data
        new_task = Task(title=title, description=description, due_date=due_date, location=location)
        db.session.add(new_task) # Добавляем новую задачу в сессию базы данных
        db.session.commit() # Фиксируем изменения в базе данных
        flash('Задача успешно добавлена!', 'success') # Отображаем сообщение об успехе
        return redirect(url_for('index')) # Перенаправляем пользователя на главную страницу
    return render_template('new_task.html', form=form) # Отображаем форму для создания новой задачи

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Отображает форму регистрации и обрабатывает регистрацию пользователя."""
    form = RegistrationForm() # Создаем экземпляр формы RegistrationForm
    if form.validate_on_submit(): # Проверяем, была ли отправлена форма и все ли поля прошли валидацию
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first() # Проверяем, существует ли уже пользователь с таким именем
        if user is None:
            hashed_password = generate_password_hash(password) # Хэшируем пароль перед сохранением
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Вы успешно зарегистрированы! Теперь вы можете войти.', 'success')
            return redirect(url_for('login')) # Перенаправляем на страницу входа
        else:
            flash('Имя пользователя уже занято.', 'warning') # Отображаем сообщение, если имя пользователя уже существует
    return render_template('register.html', form=form) # Отображаем форму регистрации

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Отображает форму входа и обрабатывает аутентификацию пользователя."""
    form = LoginForm() # Создаем экземпляр формы LoginForm
    if form.validate_on_submit(): # Проверяем, была ли отправлена форма и все ли поля прошли валидацию
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first() # Ищем пользователя по имени
        if user and check_password_hash(user.password, password): # Проверяем, найден ли пользователь и совпадает ли пароль
            session['user_id'] = user.id # Сохраняем ID пользователя в сессии для аутентификации
            flash('Вы успешно вошли!', 'success')
            return redirect(url_for('index')) # Перенаправляем на главную страницу
        else:
            flash('Неверное имя пользователя или пароль.', 'danger') # Отображаем сообщение об ошибке входа
    return render_template('login.html', form=form) # Отображаем форму входа

@app.route('/logout')
def logout():
    """Выходит из сессии пользователя."""
    session.pop('user_id', None) # Удаляем ID пользователя из сессии
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index')) # Перенаправляем на главную страницу


@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    """Отображает форму для редактирования существующей задачи и обрабатывает ее отправку."""
    task = Task.query.get_or_404(task_id) # Получаем задачу по ID или возвращаем 404, если не найдена
    form = TaskForm(obj=task) # Инициализируем форму данными из объекта задачи
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        task.location = form.location.data
        db.session.commit()
        flash('Задача успешно обновлена!', 'success')
        return redirect(url_for('index'))
    return render_template('edit_task.html', form=form, task_id=task_id)




@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    """Удаляет задачу из базы данных."""
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Задача успешно удалена!', 'info')
    return redirect(url_for('index')) 

if __name__ == '__main__':
    app.run(debug=True)
