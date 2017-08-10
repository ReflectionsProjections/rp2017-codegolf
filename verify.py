import os, sys
import subprocess as sp

def python_verify(data, user_file):
    answer = open(user_file).read()
    # write to temporary files
    with open('answer.py', 'w') as temp:
        temp.write(answer)

    try:
        test = open('task/test.py').read()
        with open('test.py', 'w') as temp:
            temp.write(test)
    except IOError: # user has not requested task yet
        print("A task folder could not be found. Request a task using python client.py request <task_id>")
        sys.exit(1) # terminate program TODO: find a better way of doing this
    proc = sp.Popen(['python', 'test.py'], stdin=sp.PIPE, stdout=sp.PIPE)
    test_result, _ = proc.communicate(input=data)
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
    test_result, _ = proc.communicate(input=data)
    # dispose of temporary files
    os.remove('answer.js')
    os.remove('test.js')
    
    return test_result

def cpp_verify(data, user_file):
    answer = open(user_file).read()
    # write to temp file
    with open('answer.cpp', 'w') as temp:
        temp.write(answer)
    try:
        test = open('task/test.h').read()
        with open('test.h', 'w') as temp:
            temp.write(test)
    except IOError: # user has not requested task yet
        print("A task folder could not be found. Request a task\nusing python client.py request <task_id>")
        sys.exit(1) # terminate program
    proc = sp.Popen(['g++', 'answer.cpp', 'test.h', '-o', 'test'], stderr=sp.DEVNULL, stdout=sp.DEVNULL)
    proc.wait()
    if(proc.returncode):
        print("Answer failed to compile.")
        sys.exit(1)
    proc = sp.Popen(['./test'], stdin=sp.PIPE, stdout=sp.PIPE)
    test_result, _ = proc.communicate(input=data)
    # dispose of temporary files
    os.remove('answer.cpp')
    os.remove('test.h')
    os.remove('test')

    return test_result
