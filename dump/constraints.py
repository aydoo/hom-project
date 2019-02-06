import numpy as np
from parser import parse

# 1. a vehicle is assigned to exactly one lane.
def vehicle_assigned_one_lane(x):
    result = []
    for v in range(num_v):
        result.append(sum([x[(v,l,p)] for l in range(num_l)
                                      for p in range(num_p)]) == 1)
    print()
    return result

# 2. a lane is occupied by exactly one series - vehicle series in the instance (e.g., only tramways or only trolleybuses).
def lane_assigned_max_one_series(x,y):
    result_1 = []
    result_2 = []
    for l in range(num_l):
        for s in np.unique(series):
            result_1.append(sum([x[(v,l,p)] * (series[v] == s) for v in range(num_v)
                                                               for p in range(num_p)]) <= num_v*y[(l,s)])
        result_2.append(sum([y[(l,s)] for s in np.unique(series)]) <= 1)
    return result_1 + result_2

# 3. a vehicle can be placed only on a lane with the necessary equipment constraints related to lane equipment (e.g., tramways can be parked on lanes with rails, buses on any lane).
def vehicle_lane_equipment(x):
    result = []
    for v in range(num_v):
        for l in range(num_l):
            result.append(sum([x[(v,l,p)] for p in range(num_p)]) <= int(equipment[v][l]))
    return result

# 4. the sum of vehicle lengths on a lane cannot exceed the lane capacity, while including the distance of 0.5 between vehicles in a lane.
def lane_capacity(x):
    result = []
    for l in range(num_l):
        result.append(sum([x[(v,l,p)] * (v_lengths[v] + 0.5)
                                 for v in range(num_v)
                                 for p in range(num_p)]) - 0.5<= l_lengths[l])
    return result

# 5. a vehicle is assigned to exactly one position (number of a vehicle in a lane).
# implied by 1

# 6. a position is occupied by exactly one vehicle.
def postion_assigned_max_one_vehicle(x):
    result = []
    for l in range(num_l):
        for p in range(num_p):
            result.append(sum([x[(v,l,p)] for v in range(num_v)]) <= 1)
    return result

# 7. the departure time of any vehicle must be prior to the vehicle following it - departure time in the instance.
def vehicle_departure_time(x):
    result = []
    for l in range(num_l):
        for p in range(num_p-1): #-1 because we don't care about the last
            result.append(sum([(int(x[(v,l,p)])-int(x[(v,l,p+1)])) * departures[v] + x[(v,l,p+1)] * max_departures for v in range(num_v)]) <= max_departures)
    return result

# 8. the departure of all the vehicles in a blocking lane must be prior to the departure of any vehicle in blocked lanes - blocked lanes.
def blocking_lanes(x):
    result = []
    for l in blocked:
        for b in blocked[l]:
            for p in range(num_p-1): #-1 because we don't care about the last
                result.append(sum([(int(x[(v,l,p)])-int(x[(v,b,0)])) * departures[v] + x[(v,b,0)] * max_departures for v in range(num_v)]) <= max_departures)
    return result

# 9. Positions are taken in order, i.e. position x+1 is only taken if x is taken
def position_ordered(x):
    result = []
    for l in range(num_l):
        for p in range(num_p-1): #-1 because we don't care about the last
            result.append(sum([int(x[(v,l,p+1)])-int(x[(v,l,p)]) for v in range(num_v)]) <= 0)
    return result

######################################################################################
######################################################################################
######################################################################################

num_v, num_l, v_lengths, series, equipment, l_lengths, departures, schedule_types, blocked = parse('instance1.txt')

num_p = 20 # number of positions (should be calculated and held as small as possible)
max_departures = max(departures) # latest departure time, we need this for some conditions

print(f"num variables: {len(v_lengths)*len(l_lengths)*num_p}")

#x = np.zeros((num_v, num_l, num_p), dtype='bool')
x = np.random.choice(a=[True, False], size=(num_v, num_l, num_p), p=[0.1, 0.9])
y = np.zeros((num_l, np.max(series)+1), dtype='bool')

constraint_results = []
constraint_results.append(vehicle_assigned_one_lane(x))
constraint_results.append(lane_assigned_max_one_series(x,y))
constraint_results.append(vehicle_lane_equipment(x))
constraint_results.append(lane_capacity(x))
constraint_results.append(postion_assigned_max_one_vehicle(x))
constraint_results.append(vehicle_departure_time(x))
constraint_results.append(blocking_lanes(x))
constraint_results.append(position_ordered(x))

for i,r in enumerate(constraint_results):
    total = len(r)
    satisfied = sum(r)
    print(f'[{i+1}] satisfied constraints: {satisfied}/{total}')
