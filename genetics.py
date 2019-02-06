import math
from random import *
from parser import parse

file_path = 'instances/instance3.txt'

num_v, num_l, v_lengths, series, equipment, l_lengths, departures, schedule_types, blocked = parse(file_path)

#############read the file ########################


def transform_to_int(elem):
    if elem == '\n': #converting string elements to int
        return 0
    else:
        return int(elem)


def read_into_solution_list(paramList):
    for i in range(29):
        inp = f.readline()
        x = inp.split(' ') if inp[-1] != ' ' else inp[:-1].split(' ')

        newx = [] #creating empty lists in order to fill them with converted to int values from each row (lane)
        for j in x:
            tr = transform_to_int(j)
            if tr != 0:
                newx.append(tr)

        paramList.append(newx) #appending the lane inputs to the array of lanes

    return paramList


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
def canBePlacedOnTheLane(combLi):
    liSat = 1
    for li in range(len(combLi)):
        iSat = 1
        if len(combLi[li]) != 0:
            for i in combLi[li]:
                iSat * int(1 == equipment[i-1][li])

        liSat *= iSat
    return liSat == 1



#2. same series in one lane
def sameSeriesConstraint (CombLi):
    sat = True
    liSat = True
    for li in CombLi:
        iSat = True
        if len(li) > 1:
            for i in range(len(li)-1):
                if i < len(li)-1:
                    if series[li[i]-1] != series[li[i+1]-1]:
                        iSat = False
        liSat = liSat == iSat
    return sat == liSat



#3. length doesn't exceed
def lengthConstraint (CombLi):
    sat = True
    countSat = True
    for li in CombLi:
        liSat = True
        lengthLi = []
        if len(li)!=0:
            for i in li:
                lengthLi.append(v_lengths[i-1])
        if (sum(lengthLi)+0.5*(len(li)-1)) > l_lengths[CombLi.index(li)-1]:
            liSat = False
        countSat = countSat == liSat
    return sat==countSat


#4. sort by departure time
def departureTimeConstraint(CombLi):
    for li in CombLi:
        depLi = []
        if len(li)>1:
            for i in li:
                depLi.append(departures[i-1])
        sortedByDepartureTime = sorted(zip(li, depLi), key=lambda tup: tup[1])
        li = [i[0] for i in sortedByDepartureTime]
    return CombLi


#5. blocking lane departures
def blockLanesRightChecker(CombLi): #main blocked lanes checker
    sat = True
    for i in blocked:
        iSat = True
        blockedLanes = blocked[i]
        blcs = True  # blcs = blocking lanes constraint satisfaction
        if len(blockedLanes) != 0: #if there are some blockedLanes, we send each of them to find out whether the time of the blocking lane is smaller than of the one that is blocked
            for jindex in blockedLanes:
                blcs = (blcs == isAheadOfBlockedLane(InitSol[i], InitSol[jindex - 1]))
        iSat= iSat == blcs
    return sat == iSat

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
def fitness_function1(CombLi): #CombLi = list of lists i.e each sublist is a lane with vehicles on it, if a sublist is empty - no vehicle on a lane
    f1 = 0
    if len(CombLi[0]) != 0:
        SeriesNum = CombLi[0][0]
    else:
        SeriesNum = 0

    for li in CombLi:
        if len(li) != 0:
            if SeriesNum != series[li[0]-1]:
                f1 += 1
                SeriesNum = series[li[0]-1]
        else:
            if SeriesNum != 0:
                f1 += 1
                SeriesNum = 0
    return f1 /(len(CombLi)-1)


def fitness_function2(CombLi):
    f2 = 0
    for li in CombLi:
        if len(li) != 0:
            f2 += 1
    return f2/len(CombLi)


#AND ALSO LOOK INTO fitness function 3
def fitness_function3(CombLi):
    remainCapacity = 0

    for li in CombLi:

        if len(li) == 0:
            remainCapacity += l_lengths[CombLi.index(li)]
        else:
            vhs = l_lengths[CombLi.index(li)] #vhs = sum of all lengths of vehicles on a lane
            for i in li:
                vhs -= v_lengths[i-1]

            remainCapacity += vhs - 0.5*(len(li) - 1)

    return remainCapacity/(sum(l_lengths) - sum(v_lengths))


def calculate_fitness(CombLi):
    return fitness_function1(CombLi)+fitness_function2(CombLi)+fitness_function3(CombLi)


def insertRandomVehicle(combLi):  # moveV = number of vehicle to be moved, moveToL = number of lane where we put our vehicle
    # for li in combLi:
    #     try:
    #         indexOfVehicle = combLi.index(moveV)
    #         indexOfLane = combLi.index(li)
    #     except ValueError:
    #         continue
    moveVehicle = randint(1, 10)  # a random vehicle that is gonna be taken out of a lane and put on another lane
    moveToLane = randint(0, len(combLi))  # a random lane where we will put our vehicle
    print(f"moveVehicle: {moveVehicle}")
    print(f"moveToLane: {moveToLane}")
    for li in combLi:
        if moveVehicle in li:
            indexOfLane = combLi.index(li)
    combLi[indexOfLane].remove(moveVehicle)

    while len(combLi[moveToLane]) == 3:
        moveToLane = randint(0, len(combLi))
        print(moveToLane)

    combLi[moveToLane].append(moveVehicle)

    return combLi


#**************************SIMULATED ANNEALING ************************
#**********************************************************************

def simulatedAnnealing(inputList):

    currentSollution = inputList
    print("Initial set\n: All constraints are satisfied: " + str(allKillConstraintCheck(inputList)))
    oldFitness = calculate_fitness(currentSollution)
    print("\nThe fitness function = " + str(oldFitness))

    T = 50 #T = temperature
    coolrate = 0.08 #cooling rate

    #main loop with temperature decreasing
    while (T >= 5):

        attemptsList = [] #it is a list of attempts to generate new set of lanes for each simulated annealing cycle
        combinationTry = 1

        newSolution = insertRandomVehicle(currentSollution)
        #loop with creating a new random solution that satisfies the constraints
        while (allKillConstraintCheck(newSolution) != True):
            newSolution = insertRandomVehicle(currentSollution) #generating the new set of lanes with vehicles
            combinationTry += 1 #i just want to know how much tries it takes to generate a new list

        attemptsList.append(combinationTry)

        newFitness = calculate_fitness(newSolution)

        delta = newFitness - oldFitness
        if delta < 0:
            currentSollution = newSolution
        else:
            selectProbability = 1/(1 + math.e ** (delta/T)) #calculating the probability of changing the solution
            z = random()
            if z < selectProbability:
                currentSollution = newSolution

        T = T * (1 - coolrate) #changing the temperature

    print("The solution was changed " + str(len(attemptsList)))
    return currentSollution
#**************************************************************************
#***************************MAIN BODY**************************************
#**************************************************************************

InitSol = []
f = open("instances/instance1.txt_solution_num_p_3.txt", "r")
read_into_solution_list(InitSol)

#***************APPLYING HEURISTICS***************************

print(simulatedAnnealing(InitSol))

######### Old algorithm ##################

# successfulRecombination = False
# attempt = 1
# newSol = InitSol
#
# while successfulRecombination != True:
#     print("Attempt " + str(attempt))
#     lane1 = randint(0, 28)
#     lane2 = randint(0, 28)
#     print(str(lane1) + " " + str(lane2))
#     newSol[lane1], newSol[lane2] = newSol[lane2], newSol[lane1]
#     successfulRecombination = allKillConstraintCheck(newSol)
#     attempt += 1
#
# print(newSol)
# out = open("instances/newrandalg.txt", "a")
# out.write("\n***********Array***************\n")
# out.write(str(newSol))
# out.write(str(calculate_fitness(newSol)))
# print(calculate_fitness(newSol))
