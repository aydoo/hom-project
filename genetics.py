import math
from random import *
from parser import parse

#############read the file ########################
def read_into_solution_list(path):
    with open(path) as f:
        return [list(map(int, line.split(' ')[:-1])) for line in f.read().splitlines()]

####################check the constraints##################
def allKillConstraintCheck(InitialList):
    InitialList = departureTimeConstraint(InitialList)
    allKillSat = []
    allKillSat.append(int(True == sameSeriesConstraint(InitialList)))
    allKillSat.append(int(True == lengthConstraint(InitialList)))
    allKillSat.append(int(True == blockLanesRightChecker(InitialList)))
    allKillSat.append(int(True == canBePlacedOnTheLane(InitialList)))
    return sum(allKillSat) == 4


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
    sat = True
    countSat = True
    for li in sol:
        liSat = True
        lengthLi = []
        if len(li)!=0:
            for i in li:
                lengthLi.append(vehicle_lengths[i-1])
        if (sum(lengthLi)+0.5*(len(li)-1)) > lane_lengths[sol.index(li)-1]:
            liSat = False
        countSat = countSat == liSat
    return sat==countSat


#4. sort by departure time
def departureTimeConstraint(sol):
    for li in sol:
        depLi = []
        if len(li)>1:
            for i in li:
                depLi.append(departures[i-1])
        sortedByDepartureTime = sorted(zip(li, depLi), key=lambda tup: tup[1])
        li = [i[0] for i in sortedByDepartureTime]
    return sol


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

def isAheadOfBlockedLane(li1, li2): #help function
    sat = True
    if len(li1) != 0:
        if len(li2) != 0:
            if departures[li1[-1]-1] < departures[li2[0]-1]:
                sat = True
            else:
                sat = False

    return sat


#FITNESS FUNCTIONs

# AYDIN PLEASE LOOK INTO fitness_function1, IT WORKS WRONG, I checked it and it seemed right but apparently it's not
def fitness_function1(sol): #sol = list of lists i.e each sublist is a lane with vehicles on it, if a sublist is empty - no vehicle on a lane
    f1 = 0
    if len(sol[0]) != 0:
        SeriesNum = sol[0][0]
    else:
        SeriesNum = 0

    for li in sol:
        if len(li) != 0:
            if SeriesNum != series[li[0]-1]:
                f1 += 1
                SeriesNum = series[li[0]-1]
        else:
            if SeriesNum != 0:
                f1 += 1
                SeriesNum = 0
    return f1 /(len(sol)-1)


def fitness_function2(sol):
    f2 = 0
    for li in sol:
        if len(li) != 0:
            f2 += 1
    return f2/len(sol)


#AND ALSO LOOK INTO fitness function 3
def fitness_function3(sol):
    remainCapacity = 0

    for li in sol:

        if len(li) == 0:
            remainCapacity += lane_lengths[sol.index(li)]
        else:
            vhs = lane_lengths[sol.index(li)] #vhs = sum of all lengths of vehicles on a lane
            for i in li:
                vhs -= vehicle_lengths[i-1]

            remainCapacity += vhs - 0.5*(len(li) - 1)

    return remainCapacity/(sum(lane_lengths) - sum(vehicle_lengths))


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
    print("Initial set:\n All constraints are satisfied: " + str(allKillConstraintCheck(sol)))
    original_fitness = obj_1(cur_sol)
    oldFitness = original_fitness
    print("The fitness function = " + str(oldFitness))

    T = 50 #T = temperature
    coolrate = 0.08 #cooling rate

    #main loop with temperature decreasing
    attemptsList = []  # it is a list of attempts to generate new set of lanes for each simulated annealing cycle
    while (T >= 5):
        combinationTry = 1
        oldFitness = obj_1(cur_sol)
        newSolution = insertRandomVehicle(cur_sol)
        #loop with creating a new random solution that satisfies the constraints
        while (allKillConstraintCheck(newSolution) != True):
            newSolution = insertRandomVehicle(cur_sol) #generating the new set of lanes with vehicles
            combinationTry += 1 #i just want to know how much tries it takes to generate a new list

        attemptsList.append(combinationTry)

        newFitness = obj_1(newSolution)

        delta = newFitness - oldFitness
        if delta < 0:
            cur_sol = newSolution
            print(f"Taking improving solution with fitness: {newFitness}")
        else:
            selectProbability = 1/(1 + math.e ** (delta/T)) #calculating the probability of changing the solution
            z = random()
            if z < selectProbability:
                print(f"Taking non-improving solution with fitness: {newFitness}")
                cur_sol = newSolution

        T = T * (1 - coolrate) #changing the temperature

    print("Final solution fitness: " + str(obj_1(cur_sol)) + f" (original: {original_fitness})")
    return cur_sol
#**************************************************************************
#***************************MAIN BODY**************************************
#**************************************************************************

file_path = 'instances/instance3.txt'

num_vehicles, num_lanes, vehicle_lengths, series, equipment, lane_lengths, departures, schedule_types, blocked = parse(file_path)

sol_path = 'instances/instance3.txt_solution_num_p_3.txt'

init_sol = read_into_solution_list(sol_path)
improved_sol = simulatedAnnealing(init_sol.copy())

#Write to file
improved_sol_path = sol_path + "_improved.txt"
with open(improved_sol_path, 'w') as f:
    for lane in improved_sol:
        if len(lane) > 0:
            for v in lane:
                f.write(str(v) + " ")
        f.write('\n')
print('Saved solution matrix.')

