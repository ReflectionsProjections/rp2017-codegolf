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
    if sp.poll() or stdout != 'Running':
        raise RuntimeError('docker environment is not operational')
    if language not in SUPPORTED_LANGUAGES:
        logging.error('this language is not supported')
        return None

    sp = Popen('docker run -id code-golf-sandbox bash', stdout=PIPE)
    cid, _ = sp.communicate()
    if sp.poll():
        raise RuntimeError('verify_%s.sh failed' % language)
    if language == 'py': return __py_verify(cid, answer, cases)
    if language == 'cc': return __cc_verify(cid, answer, cases)
    if language == 'js': return __js_verify(cid, answer, cases)
    if language == 'java': return __java_verify(cid, answer, cases)


def __py_verify(cid, answer, cases):
    results = [False] * len(cases)
    call('docker cp %s %s:/data/answer.py' % (answer, cid))
    for i in range(len(cases)):
        args = ' '.join(case['args'])
        sp = Popen('docker exec -i python answer.py %s' % args, stdout=PIPE)
        results[i] = (sp.communicate()[0] == case['output'])
    call('docker kill %s' % cid)
    return results


def __cc_verify(cid, answer, cases):
    return True


def __js_verify(cid, answer, cases):
    return True


def __java_verify(cid, answer, cases):
    return True
