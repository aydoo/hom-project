import math
from random import *
from parser import parse

#############read the file ########################
def read_into_solution_list(path):
    with open(path) as f:
        return [list(map(int, line.split(' ')[:-1])) for line in f.read().splitlines()]

####################check the constraints##################
def check_constraints(sol):
    return departureTimeConstraint(sol) and \
           sameSeriesConstraint(sol) and \
           lengthConstraint(sol) and \
           blockLanesRightChecker(sol) and \
           canBePlacedOnTheLane(sol)


#1. if the vehicle can be placed on the lane
def canBePlacedOnTheLane(sol):
    for l in range(num_lanes):
        if len(sol[l]) != 0:
            for v in sol[l]:
                if equipment[v-1][l] == 0:
                    return False
    return True



#2. same series in one lane
def sameSeriesConstraint (sol):
    for l in range(num_lanes):
        if len(sol[l]) != 0:
            for v_1 in sol[l]:
                for v_2 in sol[l]:
                    if series[v_1-1] != series[v_2-1]:
                        return False
    return True

#3. length doesn't exceed
def lengthConstraint (sol):
    for l in range(num_lanes):
        if len(sol[l]) != 0:
            total_length = sum([vehicle_lengths[v-1] for v in sol[l]])+ (len(sol[l])-1)*0.5
            if total_length > lane_lengths[l]:
                return False
    return True


#4. sort by departure time
def departureTimeConstraint(sol):
    for l in range(num_lanes):
        if len(sol[l]) != 0:
            for v_index in range(len(sol[l])-1):
                if departures[sol[l][v_index]-1] > departures[sol[l][v_index+1]-1]:
                    return False
    return True


#5. blocking lane departures
def blockLanesRightChecker(sol): #main blocked lanes checker
    for blocking_lane in blocked:
        blocked_lanes = blocked[blocking_lane]
        for blocked_lane in blocked_lanes:
            lane_i = sol[blocking_lane-1]
            lane_j = sol[blocked_lane-1]
            for i in lane_i:
                for j in lane_j:
                    if departures[i-1] >= departures[j-1]:
                        return False
    return True

#FITNESS FUNCTIONs

# AYDIN PLEASE LOOK INTO fitness_function1, IT WORKS WRONG, I checked it and it seemed right but apparently it's not
def fitness_function1(sol): #sol = list of lists i.e each sublist is a lane with vehicles on it, if a sublist is empty - no vehicle on a lane
    result = 0
    l = 0
    while l < num_lanes:
        if len(sol[l]) != 0:
            cur_series = series[sol[l][0]-1]
            l = l+1
            while l < num_lanes and (len(sol[l]) == 0 or series[sol[l][0]-1] == cur_series):
                l = l+1
            result +=1
    return result / (num_lanes-1)

def fitness_function2(sol):
    f2 = 0
    for li in sol:
        if len(li) != 0:
            f2 += 1
    return f2/len(sol)


#AND ALSO LOOK INTO fitness function 3
def fitness_function3(sol):
    result = 0
    for l in range(num_lanes):
        if len(sol[l]) != 0:
            total_length = sum([vehicle_lengths[v-1] for v in sol[l]])+ (len(sol[l])-1)*0.5
            result = result +  (lane_lengths[l]-total_length)
    return result/(sum(lane_lengths) - sum(vehicle_lengths))

def obj_1(sol):
    return fitness_function1(sol)+fitness_function2(sol)+fitness_function3(sol)


def insertRandomVehicle(sol):  # moveV = number of vehicle to be moved, moveToL = number of lane where we put our vehicle
    # for li in sol:
    #     try:
    #         indexOfVehicle = sol.index(moveV)
    #         indexOfLane = sol.index(li)
    #     except ValueError:
    #         continue

    moveVehicle = randint(1, 10)  # a random vehicle that is gonna be taken out of a lane and put on another lane
    moveToLane = randint(0, len(sol)-1)  # a random lane where we will put our vehicle
#    print("moving a random vehicle No" + str(moveVehicle))
#    print("moving to a random lane No" + str(moveToLane+1))
    for li in sol:
        if moveVehicle in li:
            indexOfLane = sol.index(li)
    sol[indexOfLane].remove(moveVehicle)

    while len(sol[moveToLane]) == 3:
        moveToLane = randint(0, len(sol)-1)
       # print("new random lane = " + str(moveToLane))

    sol[moveToLane].append(moveVehicle)

    return sol


#**************************SIMULATED ANNEALING ************************
#**********************************************************************

def simulatedAnnealing(sol):
    cur_sol = sol
    print("Initial set:\n All constraints are satisfied: " + str(check_constraints(sol)))
    original_fitness = obj_1(cur_sol)
    oldFitness = original_fitness
    print("The fitness function = " + str(oldFitness))

    sol_tracker = []

    T = 100 #T = temperature
    coolrate = 0.08 #cooling rate

    #main loop with temperature decreasing
    attemptsList = []  # it is a list of attempts to generate new set of lanes for each simulated annealing cycle
    while (T > 0.01):
        combinationTry = 1
        oldFitness = obj_1(cur_sol)
        newSolution = insertRandomVehicle(cur_sol)
        #loop with creating a new random solution that satisfies the constraints
        while (check_constraints(newSolution) != True):
            newSolution = insertRandomVehicle(cur_sol) #generating the new set of lanes with vehicles
            combinationTry += 1 #i just want to know how much tries it takes to generate a new list

        attemptsList.append(combinationTry)

        newFitness = obj_1(newSolution)

        delta = newFitness - oldFitness
        if delta < 0:
            cur_sol = newSolution
            print(f"Taking improving solution with fitness: {newFitness}")
        else:
            selectProbability =  math.e ** (-delta/T) #calculating the probability of changing the solution
            z = random()
            if z < selectProbability:
                print(f"Taking non-improving solution with fitness: {newFitness}")
                cur_sol = newSolution

        sol_tracker.append(newSolution)
        T = T * (1 - coolrate) #changing the temperature

    print("Final solution fitness: " + str(obj_1(cur_sol)) + f" (original: {original_fitness})")
    return cur_sol, sol_tracker
#**************************************************************************
#***************************MAIN BODY**************************************
#**************************************************************************

file_path = 'instances/instance3.txt'

num_vehicles, num_lanes, vehicle_lengths, series, equipment, lane_lengths, departures, schedule_types, blocked = parse(file_path)

sol_path = 'instances/instance3.txt_solution_num_p_3.txt'

init_sol = read_into_solution_list(sol_path)
improved_sol, sol_list = simulatedAnnealing(init_sol.copy())

#Write to file
for cur_sol in sol_list:
    with open(sol_path + "_improved_"+str(obj_1(cur_sol))+".txt" , 'w') as f:
        for lane in cur_sol:
            if len(lane) > 0:
                for v in lane:
                    f.write(str(v) + " ")
            f.write('\n')
    print('Saved solution matrix.')

