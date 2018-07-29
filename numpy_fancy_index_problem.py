import numpy as np
a = np.arange(12)
a.shape = (3,4)
a1 = a.copy()
c = a>5
#case 1
a1[c] += 5
print('a1 = ', a1)
#case2
e = a1[c]
e += 5
print('a1 = ', a1)
