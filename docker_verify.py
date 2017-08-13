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

    sp = Popen('docker run -id code-golf-sandbox bash', stdout=PIPE)
    cid_bytes, _ = sp.communicate()
    cid = cid_bytes.decode()[:-1]
    if sp.poll():
        raise RuntimeError('verify_%s.sh failed' % language)
    if language == 'py': return __py_verify(cid, answer, cases)
    if language == 'cc': return __cc_verify(cid, answer, cases)
    if language == 'js': return __js_verify(cid, answer, cases)
    if language == 'java': return __java_verify(cid, answer, cases)


def __py_verify(cid, answer, cases):
    results = [False] * len(cases)
    with open('answer.py', 'w') as tempfile:
        tempfile.write(answer.decode())
    call('docker cp answer.py %s:/data/answer.py' % cid)
    call('rm answer.py')
    for i in range(len(cases)):
        args = ' '.join(cases[i].get('input', None))
        sp = Popen('docker exec -i %s python /data/answer.py %s' % (cid, args), stdout=PIPE)
        res_bytes, _ = sp.communicate()
        res = res_bytes.decode()[:-1]
        results[i] = (res == cases[i].get('output', None)) 
    call('docker kill %s' % cid)
    return results


def __cc_verify(cid, answer, cases):
    return True


def __js_verify(cid, answer, cases):
    return True


def __java_verify(cid, answer, cases):
    return True
