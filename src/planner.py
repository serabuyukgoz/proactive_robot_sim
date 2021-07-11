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

def run_planning(domain, problem):
  fd, tmp_path = tempfile.mkstemp()
  f = open("shell.txt", "w") #temp shell
  path = '~/Desktop/simulation_trial/DIRNAME'
  search_method = "astar(add())"
  #path = '~/planner/fast_downward/downward'
  try:
      subprocess.check_call(
          'python3.6 %s/fast-downward.py --plan-file %s %s %s --search "%s"'
              % (path, tmp_path, domain, problem, search_method),
          stdout=f,
          stderr=subprocess.STDOUT,
          shell=True)
      with open(tmp_path, 'r') as tmp_file:
          a = tmp_file.read().partition(';')[0]
          fin = re.findall(r'\((.*?)\)', a)
          return fin

  finally:
      os.close(fd)
      try:
          os.remove(tmp_path)
      except Exception as e:
          print('Error removing %s: %s' % (tmp_path, e))
