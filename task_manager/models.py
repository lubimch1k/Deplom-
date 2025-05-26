from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, Date, Boolean

db = SQLAlchemy() # Создаем экземпляр SQLAlchemy БЕЗ привязки к приложению

class Task(db.Model):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(Date, nullable=True)
    location = Column(String(100), nullable=True)
    completed = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Task id={self.id}, title='{self.title[:20]}...'>"

class User(db.Model):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(128), nullable=False)

    def __repr__(self):
        return f"<User username='{self.username}'>"