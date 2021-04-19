import math
import time

maped = {'one' : [1], 'two' : [],  'three' : [3,1], 'five' : [], 'test' : [1]}
maped_t = {}
for k in maped:
    if (len(maped[k]) == 0):
        maped_t[k] = math.inf
    else:
        maped_t[k] = len(maped[k])
print(maped)
print(maped_t)

minval = min(maped.values())
print(minval)
minval_t = min(maped_t.values())
print(minval_t)

intent_list = [k for k in maped_t if maped_t[k] == minval_t]
print(intent_list)

tt = {}
tt[time.time()] = intent_list
print(tt)
