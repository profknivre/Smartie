from util import linreg
from collections import deque
import shelve

with shelve.open('/tmp/shelve') as db:
    if 'hum_hist' not in db:
        raise Exception('not found')
    else:
        dq = db['hum_hist']

    print(dq)
    a, b = linreg(range(len(dq)), dq)
    print(a)
    
