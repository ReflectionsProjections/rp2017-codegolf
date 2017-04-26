from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    desc_link = db.Column(db.String(50))
    test_link = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    answers = db.relationship('Answer', backref='task', lazy='dynamic')

    def to_dict(self):
        task_dict = {
            'id': self.id,
            'name': self.name,
            'desc_link': self.desc_link,
            'test_link': self.test_link,
            'created_at': self.created_at,
            'answers': self.answers.count()
        }
        return task_dict

class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    length = db.Column(db.Integer)
    runtime = db.Column(db.Float)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def to_dict(self):
        answer_dict = {
            'id': self.id,
            'username': self.username,
            'length': self.length,
            'runtime': self.runtime,
            'task_id': self.task_id,
            'created_at': self.created_at
        }
        return answer_dict