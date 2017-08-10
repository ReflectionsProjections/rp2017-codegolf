import xml.etree.ElementTree as et
import logging

class TaskManager:
  # Interface to tasks
  tree = None

  def __init__(self, filename):
    self.tree = et.parse(filename).getroot()
  
  def get_tasks(self):
    ret = []
    for tid in range(len(self.tree)):
      ret.append(self.get_task(tid))
    return ret

  def get_task(self, tid):
    try:
      task = self.tree[tid]
      return {
        'name': task.find('name').text,
        'desc': task.find('desc').text,
        'test_cases': self.get_test_cases(tid)
      }
    except IndexError:
      return None

  def get_test_cases(self, tid):
    try:
      cases = self.tree[tid].find('test_cases')
      ret = []
      for case in cases:
        args = [arg.text for arg in case.find('input')]
        ret.append({'args':tuple(args), 'output':case.find('output').text})
      return ret
    except IndexError:
      return None

  def get_test_case(self, tid, cid):
    try:
      case = self.tree[tid].find('test_cases')[cid]
      args = [arg.text for arg in case.find('input')]
      return {'args':tuple(args), 'output':case.find('output').text}
    except IndexError:
      return None
