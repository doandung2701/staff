import os
for r, d, f in os.walk('.'):
    for file in f:
        print(os.path.join(r, file))
