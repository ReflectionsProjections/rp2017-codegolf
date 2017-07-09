# -*- coding: utf-8 -*-
# @warut-vijit

import hashlib
import sys
import subprocess as sp
import requests
from datetime import datetime
from requests.exceptions import ConnectionError

from verify import python_verify, js_verify

HOST = 'http://localhost:21337'
SUPPORTED_TYPES = {'py':python_verify, 'js':js_verify, 'C':cpp_verify, 'cc':cpp_verify}

def request(task_id):
    try:
        task = requests.get(HOST + '/golf/' + str(task_id) + '/task_info').json()
        print('\n------------Task #%s--------------' % task_id)
        print('  Name: %s' % task['task']['name'])
        print('  Description:')
        for line in task['desc'].split('\n'):
            print('    %s' % line)
        print('\nDescription and test files have been saved in folder task')
        sp.call(['mkdir', 'task'], stderr=sp.PIPE)
        with open('task/desc.md', 'w') as desc_file:
            desc_file.write(task['desc'])
        with open('task/test.py', 'w') as test_file:
            test_file.write(task['test'])
        
    except ConnectionError:
        print('Failed to establish a connection to the server.\nPlease check your Internet connection.')
    except ValueError:
        print('The task you requested does not exist.\nPlease contact a staff member if you think this is in error.')

def task_list():
    try:
        tasks = requests.get(HOST + '/golf/task_list').json()
        if len(tasks) == 0:
            print('No tasks are currently active.\nMore tasks will be activated shortly.')
        for task in tasks:
            print(' %s:  %s' % (task['id'], task['name']))
    except ConnectionError:
        print('Failed to establish a connection to the server.\nPlease check your Internet connection.')
    except ValueError:
        # if this gets called we messed up. soz
        print('The dev team messed up.')

def submit(task_id, user_file):
    try:
        ext = user_file.split('.')[-1]
        if ext not in SUPPORTED_TYPES:
            print('This language is not supported for this competition.')
            sys.exit(1)
        user_file_length = len(open(user_file).read())
        submit_date = datetime.now()
        # compute a hash of the current date and time
        # use as argument to verify scripts
        time_hash = hexdigest(submit_date.isoformat())
        # run build/test scripts and get plaintext response
        verify_result = str(SUPPORTED_TYPES[ext](time_hash, user_file))
        verify_hash = str(hexdigest(verify_result))
        params = {
            'answer': verify_hash, 
            'timestamp': submit_date.isoformat(),
            'length': user_file_length,
            'username': 'TEMP_USERNAME'} # TODO: implement registration
        submit_request = requests.request('POST', HOST + '/golf/%s/answer' % task_id, params=params)
        try:
            response_json = submit_request.json()
            print('Your submission was judged as %s.' % ('correct' if response_json['correct'] else 'incorrect'))
            print('\nSubmission contained %s characters' % response_json['length'])
            print('You are now in %s place for this task.' % "TODO: Implement leaderboard")
        except ValueError: # server returned a 400 error for non-existent task
            print('The requested task is either closed to entries or does not exist.')
    except IOError:
        print('The file %s is either\nan invalid script or could not be opened.' % user_file)

def hexdigest(string):
    hashobj = hashlib.sha256()
    hashobj.update(bytes(string, 'utf-8'))
    return hashobj.digest()

if __name__=='__main__':
    print('\n#--------------------------------#')
    print('#           Code Golf            #')
    print('#   Reflections | Projections    #')
    print('#             2017               #')
    print('#--------------------------------#\n')
    #endpoint: python client.py request <task_id>
    if len(sys.argv) == 3 and sys.argv[-2] == 'request':
        request(sys.argv[-1])
    
    #endpoint: python client.py list
    elif len(sys.argv) == 2 and sys.argv[-1] == 'list':
        task_list()
    
    #endpoint: python client.py submit <task_name> <submission_file>
    elif len(sys.argv) == 4 and sys.argv[-3] == 'submit':
        submit(sys.argv[-2], sys.argv[-1])
    
    #invalid command
    else:
        print('TODO: Implement help screen here')
