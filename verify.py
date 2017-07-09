import os
import sys
import subprocess as sp

def python_verify(data, user_file):
    answer = open(user_file).read()
    # write to temporary files
    with open('answer.py', 'w') as temp:
        temp.write(answer)
    try:
        test = open('task/test.py').read()
    except IOError: # user has not requested task yet
        print("A task folder could not be found. Request a task\nusing python client.py request <task_id>")
        sys.exit(1) # terminate program TODO: find a better way of doing this
    with open('test.py', 'w') as temp:
        temp.write(test)
    proc = sp.Popen(['python', 'test.py'], stdin=sp.PIPE, stdout=sp.PIPE)
    (test_result, err) = proc.communicate(input=data.encode('utf-8'))
    # dispose of temporary files
    os.remove('answer.py')
    os.remove('test.py')

    return test_result

def js_verify(data, user_file):
    answer = open(user_file).read()
    # write to temporary files
    with open('answer.js', 'w') as temp:
        temp.write(answer)
    try:
        test = open('task/test.js').read()
    except IOError: # user has not requested task yet
        print("A task folder could not be found. Request a task\nusing python client.py request <task_id>")
        sys.exit(1) # terminate program TODO: find a better way of doing this
    with open('test.js', 'w') as temp:
        temp.write(test)
    proc = sp.Popen(['node', 'test.js'], stdin=sp.PIPE, stdout=sp.PIPE)
    (test_result, err) = proc.communicate(input=data.encode('utf-8'))
    # dispose of temporary files
    os.remove('answer.js')
    os.remove('test.js')
    
    return test_result

