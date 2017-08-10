from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    length = db.Column(db.Integer)
    correct = db.Column(db.Boolean)
    task_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'length': self.length,
            'correct': self.correct,
            'task_id': self.task_id,
            'created_at': self.created_at
        }