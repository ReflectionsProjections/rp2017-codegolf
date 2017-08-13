# -*- coding: utf-8 -*-

import logging, rest_api
from flask import Flask
from flask_restful import Api
from models import db
from task_manager import TaskManager

app = Flask(__name__)
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=UTF-8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

PORT = 21337

api = Api(app)

api.add_resource(rest_api.TaskListResource, '/golf/task_list')
api.add_resource(rest_api.AnswerResource, '/golf/<int:task_id>/answer')
api.add_resource(rest_api.AnswerInfoResource, '/golf/<int:answer_id>/answer_info')
api.add_resource(rest_api.TaskInfoResource, '/golf/<int:task_id>/task_info')

db.app = app
db.init_app(app)
db.create_all(app=app)

if __name__ == '__main__':
    rest_api.manager = TaskManager('sample_data/tasks_to_json.json')
    logging.basicConfig(level="INFO")
    app.run(host='0.0.0.0', port=PORT, debug=True, threaded=True)
