from subprocess import call, Popen, PIPE
import logging

# wrapper function for all verification routines
# Arguments:
#     answer     filename of user-submitted code
#     language   string, one of [py, cc, js, java]
#     cases      array of dicts
#       args     array of arguments
#       answer   string
# Returns:
#     array of bools length = len(cases)
#     None       if invalid
# Raises:
#     RuntimeError

SUPPORTED_LANGUAGES = ['py', 'cc', 'js', 'java']


def docker_verify(answer, language, cases):
    sp = Popen('docker-machine status', stdout=PIPE)
    stdout, _ = sp.communicate()
    if sp.poll() or stdout != b'Running\n':
        raise RuntimeError('docker environment is not operational')
    if language not in SUPPORTED_LANGUAGES:
        logging.error('this language is not supported')
        return None

    if sp.poll():
        raise RuntimeError('verify_%s.sh failed' % language)
    if language == 'py': return __py_verify(answer, cases)
    if language == 'cc': return __cc_verify(answer, cases)
    if language == 'js': return __js_verify(answer, cases)
    if language == 'java': return __java_verify(answer, cases)


def __py_verify(answer, cases):
    sp = Popen('docker run -id python bash', stdout=PIPE)
    cid_bytes, _ = sp.communicate()
    cid = cid_bytes.decode()[:-1]
    results = [False] * len(cases)
    with open('answer.py', 'w') as tempfile:
        tempfile.write(answer.decode())
    call('docker cp answer.py %s:usr/src/answer.py' % cid)
    call('rm answer.py')
    for i in range(len(cases)):
        args = ' '.join(cases[i].get('input', None))
        sp = Popen('docker exec -i %s python usr/src/answer.py %s' % (cid, args), stdout=PIPE)
        res_bytes, _ = sp.communicate()
        res = res_bytes.decode()[:-1]
        logging.warning(res + " == " + cases[i].get('output', None))
        results[i] = (res == cases[i].get('output', None)) 
    call('docker kill %s' % cid)
    return results


def __cc_verify(answer, cases):
    sp = Popen('docker run -id gcc bash', stdout=PIPE)
    cid_bytes, _ = sp.communicate()
    cid = cid_bytes.decode()[:-1]
    results = [False] * len(cases)
    with open('answer.cc', 'w') as tempfile:
        tempfile.write(answer.decode())
    call('docker cp answer.cc %s:usr/src/answer.cc' % cid)
    call('rm answer.cc')
    call('docker exec %s gcc usr/src/answer.cc -o usr/src/answer' % cid)
    for i in range(len(cases)):
        args = ' '.join(cases[i].get('input', None))
        sp = Popen('docker exec -i %s usr/src/answer %s' % (cid, args), stdout=PIPE)
        res_bytes, _ = sp.communicate()
        res = res_bytes.decode()[:-1]
        logging.warning(res + " == " + cases[i].get('output', None))
        results[i] = (res == cases[i].get('output', None)) 
    call('docker kill %s' % cid)
    return results


def __js_verify(answer, cases):
    sp = Popen('docker run -id node bash', stdout=PIPE)
    cid_bytes, _ = sp.communicate()
    cid = cid_bytes.decode()[:-1]
    results = [False] * len(cases)
    with open('answer.js', 'w') as tempfile:
        tempfile.write(answer.decode())
    call('docker cp answer.js %s:usr/src/answer.js' % cid)
    call('rm answer.js')
    for i in range(len(cases)):
        args = ' '.join(cases[i].get('input', None))
        sp = Popen('docker exec -i %s node usr/src/answer.js %s' % (cid, args), stdout=PIPE)
        res_bytes, _ = sp.communicate()
        res = res_bytes.decode()[:-1]
        logging.warning(res + " == " + cases[i].get('output', None))
        results[i] = (res == cases[i].get('output', None)) 
    call('docker kill %s' % cid)
    return results


def __java_verify(answer, cases):
    sp = Popen('docker run -id java bash', stdout=PIPE)
    cid_bytes, _ = sp.communicate()
    cid = cid_bytes.decode()[:-1]
    results = [False] * len(cases)
    with open('Answer.java', 'w') as tempfile:
        tempfile.write(answer.decode())
    call('docker cp Answer.java %s:usr/src/Answer.java' % cid)
    call('rm Answer.java')
    call('docker exec %s javac usr/src/Answer.java' % cid)
    for i in range(len(cases)):
        args = ' '.join(cases[i].get('input', None))
        sp = Popen('docker exec -i %s java -cp usr/src Answer %s' % (cid, args), stdout=PIPE)
        res_bytes, _ = sp.communicate()
        res = res_bytes.decode()[:-1]
        logging.warning(res + " == " + cases[i].get('output', None))
        results[i] = (res == cases[i].get('output', None)) 
    call('docker kill %s' % cid)
    return results

