#This is an alternative attempt at implementing a TSP algorithm using a genetic algorithm
#While it functions, it is often bogged down in local minima/premature convergence, and hence
#was not chosen as the tournament TSP algorithm for our team
import random
import math
import sys

#reads cities from text file
def ReadCities():
    f = open(filename, 'r')
    cities = []
    for line in f:

        intList = list(map(int, line.split()))
        cities.append(intList)

    f.close()
    return cities

#generates a randomized tour
def RandomTour(cities):
    tempCities = list(cities)
    random.shuffle(tempCities)
    return tempCities

#calculates distance between two cities
def CalcDistances(cities):
    total = 0
    #calculate and add distance of first to last city
    for i in range(0, len(cities) - 1):
        total += int(round(math.sqrt(math.pow(cities[i][1] - cities[i+1][1],2) + math.pow(cities[i][2] - cities[i+1][2],2))))

    #add distance from first to last city
    total += int(round(math.sqrt(math.pow(cities[0][1] - cities[len(cities) - 1][1], 2) + math.pow(cities[0][2] - cities[len(cities) - 1][2], 2))))

    return total

class Population(object):

    def __init__(self, cityList=None):
        self.baseCityList = cityList
        self.mutationRate = 10
        self.populationSize = 800 #s/b 100,000
        self.groupSize = 10 #must be >= 5
        self.entirePopulation = []
        self.minDistance = None
        self.minIndex = None

        for i in range(0,self.populationSize):
            tempCityList = list(self.baseCityList.getCities())
            random.shuffle(tempCityList)
            self.entirePopulation.append(Tour(tempCityList))

        for i in range(0, len(self.entirePopulation)):
            self.entirePopulation[i].calcDistance()

    def printPopulation(self):
        for i in range(0, len(self.entirePopulation)):
            print(self.entirePopulation[i].getCities())

    def printOptimalTour(self, outputFileName):
        out = open(outputFileName, 'w')
        out.write(str(self.minDistance) + "\n")
        minTour = list(self.entirePopulation[self.minIndex].getCities())

        for i in range(0, len(minTour)):
            out.write(str(minTour[i][0]) + "\n")

    def printDistances(self):
        for i in range(0, len(self.entirePopulation)):
            print(self.entirePopulation[i].getDistance())

    def nextGeneration(self):
        crossoverGroup = []
        for i in range(0, self.groupSize):
            crossoverTour = []
            crossoverTour.append(random.randrange(0, self.populationSize))
            crossoverTour.append(self.entirePopulation[crossoverTour[0]])
            crossoverGroup.append(crossoverTour)

        self.sortCrossoverGroup(crossoverGroup)

        parentSelect = self.determineParents(crossoverGroup)
        children = self.crossover(crossoverGroup[parentSelect[0]][1], crossoverGroup[parentSelect[1]][1])

        child1Index = crossoverGroup[self.groupSize - 2][0]
        child2Index = crossoverGroup[self.groupSize - 1][0]

        #set the lowest two tours to the crossovered children
        self.entirePopulation[child1Index] = Tour(children[0])
        self.entirePopulation[child2Index] = Tour(children[1])

        #attempt to mutate the children
        self.entirePopulation[child1Index].mutate(self.mutationRate)
        self.entirePopulation[child2Index].mutate(self.mutationRate)

        #update the distance of the children
        self.updateDistance(child1Index)
        self.updateDistance(child2Index)

    #determine parents based on a group size of 5 or more
    #creates crossover from at least 1 of the two shortest distance tours
    #attempts to maintain diversity somewhat by ocassionaly incorporating lower-quality parents for crossover,
    #though at a less frequent level
    def determineParents(self, crossoverGroup):
        parentRandom = random.randrange(0,100)

        if(parentRandom <= 40):
            return 0, 1
        elif(parentRandom <=60):
            return 0, 2
        elif(parentRandom <= 70):
            return 0, self.groupSize - 2
        elif(parentRandom <= 80):
            return 0, self.groupSize - 1
        elif(parentRandom <= 90):
            return 1, 2
        elif(parentRandom <= 95):
            return 1, self.groupSize - 2
        elif(parentRandom < 100):
            return 1, self.groupSize - 1

    def updateDistance(self, tourIndex):
        self.entirePopulation[tourIndex].calcDistance()

        distance = self.entirePopulation[tourIndex].getDistance()

        if(self.minDistance == None or self.minDistance > distance):
            self.minDistance = distance
            self.minIndex = tourIndex

    #insertion sort crossover group
    def sortCrossoverGroup(self, crossoverGroup):
        for i in range(0, len(crossoverGroup) - 1):
            for j in range(0, len(crossoverGroup) - 1):
                if(crossoverGroup[j][1].getDistance() > crossoverGroup[j+1][1].getDistance()):
                    crossoverGroup[j], crossoverGroup[j+1] = crossoverGroup[j+1], crossoverGroup[j]


        return crossoverGroup

    #Using Partially Mapped Crossover
    def crossover(self, parent1, parent2):
        # create two crossover points
        tourLength = len(parent1.getCities())
        a = random.randrange(0, tourLength - 1)
        b = random.randrange(a, tourLength)
        # create two empty lists for the children
        child1 = [None] * tourLength
        child2 = [None] * tourLength

        # copy the crossover elements
        for i in range(a, b):
            child1[i] = parent2.cities[i]
            child2[i] = parent1.cities[i]

        for i in range(0, tourLength):
            if (child1[i] == None and parent1.cities[i] not in child1):
                child1[i] = parent1.cities[i]
            if (child2[i] == None and parent2.cities[i] not in child2):
                child2[i] = parent2.cities[i]
        parent1Curr = a
        parent2Curr = a

        # fills the empty spaces with any non-duplicates from the cities that were crossed over
        for i in range(0, tourLength):
            if (child1[i] == None):
                while (child1[i] == None and parent1Curr < b):
                    if (parent1.cities[parent1Curr] not in child1):
                        child1[i] = parent1.cities[parent1Curr]

                    parent1Curr += 1
            if (child2[i] == None):
                while (child2[i] == None and parent2Curr < b):
                    if (parent2.cities[parent2Curr] not in child2):
                        child2[i] = parent2.cities[parent2Curr]

                    parent2Curr += 1

        return child1, child2


class Tour(object):

    def __init__(self, cities=None,distance=None):
        self.cities = cities
        self.distance = distance

    def calcDistance(self):
        total = 0
        # calculate and add distance of first to last city
        for i in range(0, len(self.cities) - 1):
            total += int(round(
                math.sqrt(math.pow(self.cities[i][1] - self.cities[i + 1][1], 2) + math.pow(self.cities[i][2] - self.cities[i + 1][2], 2))))

        # add distance from first to last city
        total += int(round(math.sqrt(
            math.pow(self.cities[0][1] - self.cities[len(self.cities) - 1][1], 2) + math.pow(self.cities[0][2] - self.cities[len(self.cities) - 1][2], 2))))

        self.distance = total

    def mutate(self, mutationRate):
        if(random.randrange(0,100) < mutationRate):

            a = random.randrange(0, len(self.cities))
            b = random.randrange(0, len(self.cities))

            self.cities[a], self.cities[b] = self.cities[b], self.cities[a]


        return self.cities

    def getCities(self):
        return self.cities

    def getDistance(self):
        if(self.distance == None):
            self.calcDistance()
        return self.distance


filename="tsp_example_1.txt"
filename=sys.argv[1]
outputFileName = sys.argv[1] + ".tour"

random.seed()
cityList = ReadCities()
bigCityList = Tour(cityList)
TestGeneration = Population(bigCityList)

#local minimum usually hit within 300,000 generations
for i in range(0,300000):
    TestGeneration.nextGeneration()

TestGeneration.printOptimalTour(outputFileName)


