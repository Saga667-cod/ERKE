import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# Импорты для безопасности паролей
from werkzeug.security import generate_password_hash, check_password_hash

# Инициализация
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super-secret-key-999' # Нужно для работы сессий (входа)

db = SQLAlchemy(app)

# --- МОДЕЛИ БАЗЫ ДАННЫХ ---

# 1. Таблица заявок (Контактная форма)
class ContactRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

# 2. Таблица пользователей (Регистрация)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Создание БД
with app.app_context():
    db.create_all()

# --- МАРШРУТЫ ---

@app.route('/')
def index():
    return render_template('index.html')

# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form.get('username')
        email = request.form.get('email')
        pw = request.form.get('password')
        
        hashed_pw = generate_password_hash(pw)
        new_user = User(username=user, email=email, password=hashed_pw)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            print(f"Пользователь {user} успешно зарегистрирован!")
            return redirect(url_for('index'))
        except:
            return "Ошибка: такой Email или Логин уже занят!"
            
    return render_template('register.html')

# Обработка формы контактов
@app.route('/submit_form', methods=['POST'])
def submit_form():
    name = request.form.get('name')
    email = request.form.get('email')
    msg = request.form.get('message')
    
    new_request = ContactRequest(name=name, email=email, message=msg)
    db.session.add(new_request)
    db.session.commit()
    print(f"--- УСПЕХ: Данные от {name} сохранены ---")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)