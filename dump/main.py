import numpy as np
from pprint import pprint
from parser import parse

path = 'instance1.txt'

num_positions = 20
vehicles, lanes = parse(path)
# pprint(vehicles)
# pprint(lanes)

# [1] Define free variable 
X = np.zeros((len(vehicles), len(lanes), num_positions))

d = lambda x_1, x_2: abs(x_1 - x_2)

error = 0

# Each value must be geater or equal 0
error += abs(np.sum(X * (X < 0)))

# Vehicle in exactly one lane
for v in vehicles.keys():
    error += d(np.sum(X[v,:,:]), 1)

# Lane/Position combo taken by max 1 vehicle
for l in lanes.keys():
    for p in range(num_positions):
        if not np.sum(X[:,l,p]) <= 1:
            error += d(np.sum(X[:,l,p]), 1)


print(error)
# [2] Find initial solution that satisfies constraints

# [3] Optimize it using genetic algorithm

