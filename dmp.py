from collections import deque
import pickle

fname = '/tmp/histogram'

def linreg(X, Y):
    """
    return a,b in solution to y = ax + b such that root mean square distance between trend line and original points is minimized
    """
    N = len(X)
    Sx = Sy = Sxx = Syy = Sxy = 0.0
    for x, y in zip(X, Y):
        Sx = Sx + x
        Sy = Sy + y
        Sxx = Sxx + x*x
        Syy = Syy + y*y
        Sxy = Sxy + x*y
    det = Sxx * N - Sx * Sx
    return (Sxy * N - Sy * Sx)/det, (Sxx * Sy - Sx * Sxy)/det


try:
    with open(fname,'rb') as f:
        humtab = pickle.loads(f.read())

except:
    humtab = deque(maxlen=10)
 
    
humlst = list(humtab)
a,b = linreg(range(len(humlst)),humlst)

print(humlst)
print(a)



    
    
