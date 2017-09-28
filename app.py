# -*- coding: utf-8 -*-

import logging
import rest_api
from flask import Flask, render_template, request, redirect, session, jsonify
from flask_restful import Api
from models import db, User
from task_manager import TaskManager
import json

app = Flask(__name__)
app.secret_key = 'secretkey'
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=UTF-8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
logging.basicConfig(level=logging.INFO)

# Configure port
PORT = 21337
CHALLENGES_PATH = 'data/challenges.json'

api = Api(app)

# API Resources for competition
api.add_resource(rest_api.TaskListResource, '/golf/task_list')
api.add_resource(rest_api.AnswerResource, '/golf/<int:task_id>/answer')
api.add_resource(rest_api.AnswerInfoResource, '/golf/<int:answer_id>/answer_info')
api.add_resource(rest_api.TaskInfoResource, '/golf/<int:task_id>/task_info')

# API Resource for registration
api.add_resource(rest_api.LoginResource, '/golf/login')
api.add_resource(rest_api.SignupResource, '/golf/signup')

# Front-end routing
@app.route('/', methods=['POST', 'GET'])
def home():
    if 'task' in request.args:
        task = int(request.args.get('task'))
    else: task = None
    if 'code' in request.args:
        code = request.args.get('code')
    else: code = ''
    if task is not None:
        try:
            task_dict = rest_api.manager.get_task(task)
            task_title = task_dict['name']
            task_text = task_dict['desc']
        except TypeError:
            logging.error("not valid task")	
            task=None
            task_title = ''
            task_text = ''
    else:
        task_title = ''
        task_text = ''
        task = 'null'
    if 'username' in session:
        username = session['username']
    else: username = 'null'
    leaders = User.query.filter(User.points>0).order_by(User.points.desc()).limit(8)
    leaderboard = json.dumps([user.to_dict() for user in leaders])
    return render_template('index.html', 
                           code=code,
                           task_title=task_title,
                           task_text=task_text,
                           task_id=task,
                           leaderboard=leaderboard,
                           username=username)

db.app = app
db.init_app(app)
db.create_all(app=app)

if __name__ == '__main__':
    rest_api.manager = TaskManager(CHALLENGES_PATH)
    rest_api.best_answer = [{
        'cc':float('inf'), 
        'java':float('inf'), 
        'js':float('inf'), 
        'py':float('inf')} for _ in rest_api.manager.get_tasks()]
    logging.basicConfig(level="INFO")
    app.run(host='0.0.0.0', port=PORT, debug=True, threaded=True)
