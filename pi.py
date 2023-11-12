import os

itr=1000
if 'PI_STEPS' in os.environ:
  itr=int(os.environ['PI_STEPS'])


# compute pi
k = 1
pi = 0

print("Computing pi using %i steps"%itr)
for i in range(itr):
    pi += (1 if ((i % 2)==0) else -1) * 4/k
    k += 2
     
print(pi)
