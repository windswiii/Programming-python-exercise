import math
import numpy as np

def random_walk(mu, x_0, sigmas, N):
    for i in range(N):
        x = mu + x_0 + np.random.normal(0, math.sqrt(sigmas), 1).item()
        yield x
        x_0 = x
        
walk_1 = random_walk(1, 0, 4, 10)
# for step in walk_1: print(step)
walk_2 = random_walk(2, 1, 1, 10)
walk_3 = random_walk(2, 0, 2, 10)
walk_4 = random_walk(1, 1, 2, 10) 

walk_zipped = zip(walk_1, walk_2, walk_3, walk_4)
for step in walk_zipped:
    print(step)