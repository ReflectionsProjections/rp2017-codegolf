from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    task_id = db.Column(db.Integer)
    length = db.Column(db.Integer)
    correct = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    points = db.Column(db.Integer)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'length': self.length,
            'correct': self.correct,
            'task_id': self.task_id,
            'created_at': self.created_at,
            'points': self.points
        }

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True)
    email = db.Column(db.String(32), unique=True)
    answers = db.relationship('Answer', backref='user', lazy='dynamic')
    password_hash = db.Column(db.String(256))

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'answers': self.answers.count()
        }
