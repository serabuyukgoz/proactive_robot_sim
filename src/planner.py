import os
import tempfile
import subprocess

import re

'''
    Connection file to the off the shelf planner
    Fast Downward planner used
    Before Start,
    Please download and compile planner from the following link
    http://www.fast-downward.org/ObtainingAndRunningFastDownwardur
    Update the path with your own path to planer
'''
class Planner():

    def __init__(self):
        self.path = '~/planner/fast_downward/downward'
        self.search_method = "astar(add())"
        self.python_version = "3"

    def set_path(self, path_of):
         self.path = path_of

    def set_python_version(self, version):
         self.python_version = version

    def set_search_method(self, method):
        self.search_method = method

    def error_codes(self, code):

        if (code == 1):
            return "SEARCH_PLAN_FOUND_AND_OUT_OF_MEMORY  : component ran out of memory. "
        elif (code == 2):
            return "SEARCH_PLAN_FOUND_AND_OUT_OF_TIME : component ran out of time. "
        elif (code == 3):
            return "SEARCH_PLAN_FOUND_AND_OUT_OF_MEMORY_AND_TIME : could not find a solution"
        elif (code == 12):
            return "SEARCH_UNSOLVED_INCOMPLETE : Search ended without finding a solution"
        elif (code == 30):
            return "TRANSLATE_CRITICAL_ERROR : Critical error: something went wrong (e.g. translator bug, but also malformed PDDL input) "
        else:
            error = str(code)
            return error

    def run_planning(self, domain, problem):
      fd, tmp_path = tempfile.mkstemp()
      f = open("shell.txt", "w") #temp shell

      try:
          subprocess.check_call(
              'python%s %s/fast-downward.py --plan-file %s %s %s --search "%s"'
                  % (self.python_version, self.path, tmp_path, domain, problem, self.search_method),
              stdout=f,
              stderr=f,
              shell=True)
          with open(tmp_path, 'r') as tmp_file:
              a = tmp_file.read().partition(';')[0]
              fin = re.findall(r'\((.*?)\)', a)
              return fin

      except subprocess.CalledProcessError as e:
          error = self.error_codes(e.returncode)
          logs = str()
          with open("shell.txt", 'r') as logs_file:
              logs = logs_file.read()
          raise Exception("Planner error \n %s \n Error code: %s" %(logs, error))

      finally:
          os.close(fd)
          try:
              os.remove(tmp_path)
          except Exception as e:
              print('Error removing %s: %s' % (tmp_path, e))
