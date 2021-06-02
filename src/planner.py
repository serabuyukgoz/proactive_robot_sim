import os
import tempfile
import subprocess

import re

#off the shef planner,

def run_planning(domain, problem):
  fd, tmp_path = tempfile.mkstemp()
  f = open("shell.txt", "w") #temp shell
  try:
      subprocess.check_call(
          'python3.6 ~/Desktop/simulation_trial/DIRNAME/fast-downward.py --plan-file %s %s %s --search "astar(add())"'
              % (tmp_path, domain, problem),
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
