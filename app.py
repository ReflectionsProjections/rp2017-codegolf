# -*- coding: utf-8 -*-

from flask import Flask, jsonify, make_response
import flask
import json
import os
from datetime import datetime
import time
from subprocess import Popen, PIPE
import requests
import logging
from flask_restful import Resource, Api, reqparse
from models import Task, Answer, db

app = Flask(__name__)
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=UTF-8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

PORT = 21337

api = Api(app)

def evaluate_user_code(user_code):
    user_code_file = open('submission.py', 'w')
    user_code_file.write(user_code)
    user_code_file.close()
    start_time = time.time()
    user_run_process = Popen(['python', 'submission.py'], stderr=PIPE)
    user_error = user_run_process.communicate()[1]
    if str.encode('Error') in user_error:
        return None
    time_elapsed = time.time()-start_time
    return time_elapsed


class AnswerResource(Resource):
    def post(self, task_id):
        ''' Endpoint for submitting code '''
        parser = reqparse.RequestParser()
        parser.add_argument('code', location='args', required=True)
        parser.add_argument('username', location='args', required=True)
        args = parser.parse_args()
        if not Task.query.filter_by(id=task_id).first():
            return make_response("Tried to respond to an invalid task.", 400)
        user_code = "".join(json.loads(args.code))
        time_elapsed = evaluate_user_code(user_code)
        if not time_elapsed:  # assertion or compilation error TODO (warut-vijit): disambiguate errors
            return make_response("User response to task %s was incorrect." % str(task_id), 400)
        logging.info("Received submission from user %s, took %s seconds" % (args.username, str(time_elapsed)))
        answer = Answer(
            username = args.username,
            length = len(user_code),
            runtime = time_elapsed,
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

class TaskResource(Resource):
    def post(self):
        ''' Endpoint for submitting tasks '''
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='args', required=True)
        parser.add_argument('desc_link', location='args', required=True)
        parser.add_argument('test_link', location='args', required=True)
        args = parser.parse_args()
        # TODO (warut-vijit): verify file existence for links
        if Task.query.filter_by(name=args.name).first():
            return make_response("Tried to create a task with duplicate name %s" % args.name)
        task = Task(
            name = args.name,
            desc_link = args.desc_link,
            test_link = args.test_link
        )
        db.session.add(task)
        db.session.commit()
        return jsonify(task.to_dict())

class TaskInfoResource(Resource):
    def get(self, task_id):
        ''' Endpoint for getting information about current state of task '''
        order_queries = {
            'latest': Answer.query.filter_by(task_id=task_id).order_by(Answer.created_at.desc()),
            'fastest': Answer.query.filter_by(task_id=task_id).order_by(Answer.runtime),
            'shortest': Answer.query.filter_by(task_id=task_id).order_by(Answer.length)
        }
        parser = reqparse.RequestParser()
        parser.add_argument('order', location='args', default='fastest')
        args = parser.parse_args()
        task = Task.query.filter_by(id=task_id).first()
        if not task:
            return make_response("Tried to query an invalid task.", 400)
        answers = [answer.to_dict() for answer in order_queries[args.order].all()]
        return jsonify({
            'task': task.to_dict(),
            'answers': answers
        })

api.add_resource(AnswerResource, '/golf/<int:task_id>/answer')
api.add_resource(AnswerInfoResource, '/golf/<int:answer_id>/answer_info')
api.add_resource(TaskResource, '/golf/task')
api.add_resource(TaskInfoResource, '/golf/<int:task_id>/task_info')
db.app = app
db.init_app(app)
db.create_all(app=app)

if __name__ == '__main__':
    logging.basicConfig(level="INFO")
    app.run(host='0.0.0.0', port=PORT, debug=True)