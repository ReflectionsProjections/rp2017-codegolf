# -*- coding: utf-8 -*-

from flask import Flask, jsonify, make_response, render_template, request
import os
from datetime import datetime
import time
import requests
import logging
from flask_restful import Resource, Api, reqparse
from models import Answer, db
from docker_verify import docker_verify
from task_manager import TaskManager

app = Flask(__name__)
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=UTF-8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

PORT = 21337

api = Api(app)
manager = None

# REST API Endpoints

class AnswerResource(Resource):
    def post(self, task_id):
        ''' Endpoint for submitting code '''
        parser = reqparse.RequestParser()
        parser.add_argument('username', location='args', required=True)
        parser.add_argument('language', location='args', required=True)
        args = parser.parse_args()
        test_cases = manager.get_test_cases(task_id)
        if task is None: # no task exists with the stated id
            return make_response("Tried to respond to an invalid task.", 400)
        # get body of response
        data = request.get_data()

        # verify response using same input
        correct_answer = str(get_correct_answer(time_hash, task.test_link, task.answer_link))
        answer = Answer(
            username = args.username,
            length = len(data),
            correct = docker_verify(data, args.language, test_cases),
            task_id = task_id
        )
        db.session.add(answer)
        db.session.commit()
        logging.info("%s submitted response to task id %s" % (args.username, task_id))
        return jsonify(answer.to_dict())

class AnswerInfoResource(Resource):
    def get(self, answer_id):
        ''' Endpoint for getting information about a particular answer '''
        answer = Answer.query.filter_by(id=answer_id).first()
        if not answer:
            return make_response("Tried to query an invalid answer.", 400)
        return jsonify(answer.to_dict())

class TaskInfoResource(Resource):
    def get(self, task_id):
        ''' Endpoint for getting information about current state of task '''
        order_queries = {
            'latest': Answer.query.filter_by(task_id=task_id).order_by(Answer.created_at.desc()),
            'shortest': Answer.query.filter_by(task_id=task_id).order_by(Answer.length)
        }
        parser = reqparse.RequestParser()
        parser.add_argument('order', location='args', default='latest')
        args = parser.parse_args()
        task = manager.get_task(task_id)
        if not task:
            return make_response("Tried to query an invalid task.", 400)
        answers = [answer.to_dict() for answer in order_queries[args.order].all()]
        return jsonify({
            'task': task,
            'answers': answers
        })

class TaskListResource(Resource):
    def get(self):
        '''Endpoint for getting a list of all available tasks'''
        return jsonify(manager.get_tasks())


# hashing function, returns bytes
def hexdigest(string):
    hashobj = hashlib.sha256()
    hashobj.update(bytes(string, 'utf-8'))
    return hashobj.digest()

api.add_resource(TaskListResource, '/golf/task_list')
api.add_resource(AnswerResource, '/golf/<int:task_id>/answer')
api.add_resource(AnswerInfoResource, '/golf/<int:answer_id>/answer_info')
api.add_resource(TaskInfoResource, '/golf/<int:task_id>/task_info')
db.app = app
db.init_app(app)
db.create_all(app=app)

if __name__ == '__main__':
    manager = TaskManager('tasks.xml')
    logging.basicConfig(level="INFO")
    app.run(host='0.0.0.0', port=PORT, debug=True, threaded=True)
