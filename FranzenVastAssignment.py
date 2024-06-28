#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 2024

@author: Rebecca Franzen


Developing a simulation for a lunar Helium-3 space mining operation. 
This simulation will manage and track the efficiency of mining trucks 
and unload stations over a continuous 72-hour operation.

Key Components:
● Mining Trucks: These vehicles perform the actual mining tasks.
● Mining Sites: Locations on the moon where the trucks extract Helium-3. Assume
 an infinite number of sites, ensuring trucks always have access to mine 
 without waiting.
● Mining Unload Stations: Designated stations where trucks unload the mined 
Helium-3. Eachstation can handle one truck at a time.

Operation Details:
● There are (n) mining trucks and (m) mining unload stations.
● Mining trucks can spend a random duration between 1 to 5 hours mining at the 
sites.
● It takes a mining truck 30 minutes to travel between a mining site and an 
unload station.
○ Assume all trucks are empty at a mining site when the simulation starts.
● Unloading the mined Helium-3 at a station takes 5 minutes.
● Trucks are assigned to the first available unload station. If all stations 
are occupied, trucks queue at the station with the shortest wait time and 
remain in their chosen queue.

Simulation Requirements:
● The simulation must be configurable to accommodate various numbers of mining 
trucks (n) and unload stations (m).
● Calculate and report statistics for the performance and efficiency of each 
mining truck and unload station.
● The simulation represents 72 hours of non-stop mining and must execute faster
 than real-time to provide timely analysis.

Language and programming paradigms:
Please implement this project in Python. Please leverage OOP where it is appropriate.
"""

#%%

import random as ran
import simpy
from enum import Enum
import matplotlib.pyplot as plt
import numpy as np

"""ALL TIME REFS ARE IN MINUTES"""

#%%

def randomMiningMinutes():
    return ((ran.random() * 4) + 1) * 60

#%%

class Location(Enum):
    UNKNOWN = 0
    MINING_SITE = 1
    TRAVELING = 2
    UNLOAD_QUEUE = 3
    UNLOAD_STATION = 4

class MiningTruck:
    timeSpentMining = 0
    timesMined = 0
    timeSpentTraveling = 0
    timesUnloaded = 0
    timeInQueue = 0
    timesQueued = 0
    currStep = Location.UNKNOWN
    def __init__(self, name):
        self.name = name
    def avgTimeMining(self):
        return self.timeSpentMining/self.timesMined
    def avgTimeQueued(self):
        return self.timeInQueue/self.timesQueued
    def printInfo(self):
        print(self.name + f': Time spent mining = {self.timeSpentMining} min, Times mined = {self.timesMined}, Times unloaded = {self.timesUnloaded}, Time spent traveling = {self.timeSpentTraveling} min, Time in Unload Station Queue = {self.timeInQueue} min, Current Location = {self.currStep.name}')
        print(f'tot time = {self.timeSpentMining + self.timeSpentTraveling + (self.timesUnloaded*5)}')
        if (self.timeSpentMining + self.timeSpentTraveling + (self.timesUnloaded*5) > 4320):
            print(f'\n\nTIME ERR -> {self.timeSpentMining + self.timeSpentTraveling + (self.timesUnloaded*5) + self.timeInQueue}\n\n')

#%%

#def miningTruck(env, unloadStation, miningSite, truck, log):
def miningTruck(env, unloadStation, miningSite, truck):
    """ 
    1. A mining truck arrives at the mining site and spends a random duration 
    between 1 to 5 hours mining. 
    2. Mining truck then drives 30 min driving to unloading station. 
    Trucks are assigned to the first available unload station. If all stations 
    are occupied, trucks queue at the station with the shortest wait time and 
    remain in their chosen queue.
    3.Unloading at a station takes 5 minutes. 
    4. Mining truck then drives 30 min to mining station. 
    Loop 1-4

    """
    #log truck name
    #name = truck.name
    #will continue in loop until environment stops running
    while True:
        #begin simulation at mining site
        
        #print(f'{env.now:6.1f} min: {name} arrived at mining site')
        #log.write(f'{env.now:6.1f} min: {name} arrived at mining site\n')
        
        with miningSite.request() as req1:
            """Find a mining station"""
            truck.currStep = Location.MINING_SITE # Update location
            yield req1 
            
            """1
            Truck spends a random duration between 1 to 5 hours mining."""
            randTime = randomMiningMinutes()
            
            #print(f'{env.now:6.1f} min: {name} will mine for {randTime} min')
            #log.write(f'{env.now:6.1f} min: {name} will mine for {randTime} min\n')
            
            yield env.timeout(randTime)
            truck.timeSpentMining += randTime
            truck.timesMined += 1
            
            #print(f'{env.now:6.1f} min: {name} mined for {randTime} min')
            #log.write(f'{env.now:6.1f} min: {name} mined for {randTime} min\n')
            
            """2
            Truck drives to unloading station (30 min)"""
            
            #print(f'{env.now:6.1f} min: {name} is traveling to unloading station')
            #log.write(f'{env.now:6.1f} min: {name} is traveling to unloading station\n')
            
            truck.currStep = Location.TRAVELING # Update location
            yield env.timeout(30)
            truck.timeSpentTraveling += 30
            
        #print(f'{env.now:6.1f} min: {name} arrived at unloading station')
        #log.write(f'{env.now:6.1f} min: {name} arrived at unloading station\n')
        
        with unloadStation.request() as req2:
            """Request to unload"""
            
            #print("Queue: ",len(unloadStation.queue))
            #log.write(f"Queue: {len(unloadStation.queue)} -> {unloadStation.queue}\n")
            
            timeQueued = env.now
            truck.timesQueued += 1
            truck.currStep = Location.UNLOAD_QUEUE # Update location
            yield req2
                
            """3
            The unloading process takes 5 min"""
            timeStarted = env.now
            truck.timeInQueue += (timeStarted - timeQueued) #Update tot time truck waited in line (minutes)
            truck.currStep = Location.UNLOAD_STATION # Update location
            yield env.timeout(5)
            truck.timesUnloaded += 1
            
            #print(f'{env.now:6.1f} min: {name} unloaded Helium-3')
            #log.write(f'{env.now:6.1f} min: {name} unloaded Helium-3\n')
            
            """4
            Truck drives to mining site (30 min)"""
            
            #print(f'{env.now:6.1f} min: {name} is traveling to mining site')
            #log.write(f'{env.now:6.1f} min: {name} is traveling to mining site\n')
            
            truck.currStep = Location.TRAVELING # Update location
            yield env.timeout(30)
            truck.timeSpentTraveling += 30

def simulateOperation(n = 10, m = 2, t = 4320): # 72hr * 60min/hr = 4320 min
    # check input types
    if (type(n) is not int) or (type(m) is not int) or (type(t) is not int):
        print("Invalid param type, must be integers")
        return 1
    # create log
    #log = open("vastLog.txt","w")
    # Create environment and start processes
    env = simpy.Environment()
    # Create m unloading stations
    unloadStation = simpy.Resource(env, capacity = m)
    # Create inf mining sites (this ensures trucks always have access to mine without waiting)
    miningSite = simpy.Resource(env, capacity = simpy.core.Infinity)
    # Store truck objs
    trucks = []
    # Create n mining trucks
    for i in range(n):
        trucks.append(MiningTruck(f'Mining Truck {i}'))
        #env.process(miningTruck(env, unloadStation, miningSite, trucks[i], log))
        env.process(miningTruck(env, unloadStation, miningSite, trucks[i]))
    
    # Execute
    env.run(until=t)
    # Closing log
    #log.close()
    return trucks, n, m

def simTruckStats(trucks, n, m):
    # check input types
    if (type(trucks) is not list) or (len(trucks) < 1)or (type(trucks[0]) is not MiningTruck):
        print('Invalid param type, must be a list of MiningTruck objects')
        return 1
    
    totMiningTime = 0
    totTimesMined = 0
    totQueueTime = 0
    totTimesQueued = 0
    truckMineTimes = []
    truckMineVisits = []
    avgMineTime = []
    truckQueueTimes = []
    avgQueueTimes = []
    
    for truck in trucks:
        # collect info
        totMiningTime += truck.timeSpentMining
        totTimesMined += truck.timesMined
        totQueueTime += truck.timeInQueue
        totTimesQueued += truck.timesQueued
        truckMineTimes.append(truck.timeSpentMining)
        truckMineVisits.append(truck.timesMined)
        avgMineTime.append(truck.avgTimeMining())
        truckQueueTimes.append(truck.timeInQueue)
        avgQueueTimes.append(truck.avgTimeQueued())
        
        # print indiv truck info
        print(truck.name)
        print(f'Total time spent mining = {truck.timeSpentMining: .2f} minutes')
        print(f'Completed mining sessions = {truck.timesMined}')
        print(f'Avg time spent mining = {truck.avgTimeMining(): .2f} minutes')
        print(f'Total time spent in Unloading Queue = {truck.timeInQueue: .2f} minutes')
        print(f'Avg time spent in Unloading Queue = {truck.avgTimeQueued(): .2f} minutes\n')
    
    # print operation info
    print('Operation Stats')
    print(f'Number of Mining Trucks = {n}, Number of Unloading Stations = {m}')
    print(f'Total time all trucks spent mining = {totMiningTime: .2f} minutes')
    print(f'Total of completed mining sessions = {totTimesMined}')
    print(f'Avg time each truck spent mining = {totMiningTime/totTimesMined: .2f} minutes')
    print(f'Total time all trucks spent in unload queue = {totQueueTime: .2f} minutes')
    print(f'Total number of times trucks were queued = {totTimesQueued}')
    print(f'Avg time each truck spent in unload queue = {totQueueTime/totTimesQueued: .2f} minutes')
    
    #create visual representations of data collected from indiv truck info if n <= 50 (stopping creating graphs here bc after this point they begin to be too messy to read. Easier to just read stats from above)
    if(len(trucks) <= 50):
        # Total Minutes Each Truck Spent Mining
        plt.barh(range(len(truckMineTimes)), truckMineTimes)
        plt.xlabel("Minutes Mined")
        plt.ylabel("Truck Number")
        plt.title("Total Minutes Each Truck Spent Mining")
        plt.xticks(range(0, int(np.ceil(np.max(truckMineTimes))), 200), rotation = 50)
        plt.yticks(range(0, len(trucks), 1))
        plt.show()
    
        # Number of Completed Mining Sessions per Truck
        plt.barh(range(len(truckMineVisits)), truckMineVisits, color = 'Green')
        plt.xlabel("Completed Mining sessions")
        plt.ylabel("Truck Number")
        plt.title("Number of Completed Mining Sessions per Truck")
        plt.xticks(range(0, int(np.ceil(np.max(truckMineVisits))), 1), rotation = 50)
        plt.yticks(range(0, len(trucks), 1))
        plt.show()
        
        # Average Minutes Each Truck Spent Mining
        plt.barh(range(len(avgMineTime)), avgMineTime, color = 'Orange')
        plt.xlabel("Avg Minutes Mined")
        plt.ylabel("Truck Number")
        plt.title("Average Minutes Each Truck Spent Mining")
        plt.xticks(range(0, int(np.ceil(np.max(avgMineTime))), 10), rotation = 50)
        plt.yticks(range(0, len(trucks), 1))
        plt.show()
        
        # Total Minutes Each Truck Spent in Unload Queue
        plt.barh(range(len(truckQueueTimes)), truckQueueTimes, color = 'Purple')
        plt.xlabel("Minutes in Queue")
        plt.ylabel("Truck Number")
        plt.title("Total Minutes Each Truck Spent in Unload Queue")
        plt.xticks(range(0, int(np.ceil(np.max(truckQueueTimes))), 10), rotation = 50)
        plt.yticks(range(0, len(trucks), 1))
        plt.show()
        
        # Average Minutes Each Truck Spent in Unload Queue
        plt.barh(range(len(avgQueueTimes)), avgQueueTimes, color = 'DeepPink')
        plt.xlabel("Minutes in Queue")
        plt.ylabel("Truck Number")
        plt.title("Average Minutes Each Truck Spent in Unload Queue")
        plt.xticks(range(0, int(np.ceil(np.max(avgQueueTimes))), 1), rotation = 50)
        plt.yticks(range(0, len(trucks), 1))
        plt.show()
    
#%%

def run():
    n = input("Enter number of mining trucks(n): ")
    #setting the max for n and m at 999 so the script can run quickly
    while (type(n) is not int) or (n < 0) or (n > 999):
        try:
            if(len(n) <= 3):
                n = int(n)
            else:
                raise Exception()
        except:
            n = input("Invalid entry. Please enter an integer (0 < n <= 9999): ")
    m = input("Enter number of unloading stations(m): ")
    while (type(m) is not int) or (m < 0) or (m > 999):
        try:
            if(len(m) <= 3):
                m = int(m)
            else:
                raise Exception()
        except:
            m = input("Invalid entry. Please enter an integer (0 < m <= 999): ")
    print("")
    trucks, numTr, numUnload = simulateOperation(n,m)
    simTruckStats(trucks, numTr, numUnload)

#%%
run()

""" If I had some more time to work on this, I would create an OperationStats class 
that would essentially store the info from simTruckStats. SimTruckStats could return 
an OperationStats object that could at some point be added to a list. I would then create 
another function called compareOps that would take a list of OperationStats objects as 
the parameter. I would have the compareOps function compare the performances between operations.
This could consist of comparing the total number of completed mining sessions of the operations as 
well as the avg minutes each truck spent in the unload station queue of the operations.

I also would have liked to work more with the location enum. I think it would be interesting 
to be able to select a timeframe and see where each of the mining trucks are located at some 
point in time. 

I was considering making an UnloadingStation class for this assignment, but decided against it 
based on the given deadline and that this is my first time using simpy. Simpy's resource class 
allows me to create m unloading stations by setting its capacity = m. Since the goal was to have 
trucks assigned to the first available unload station, simpy's resource class allows trucks to hold 
an unloading station then release it to the next in the queue once it is finished unloading. This 
works virtually the same as a truck choosing the shortest queue as the time spent unloading is 
the same for all trucks. Simpy's resource objects also gives access to its queue (queue of pending 
Request events) and count (Number of users currently using the resource), which could potenially be
useful in determining operation performance, and if I had some more time I would have liked to 
incorporate it into this assignment as well"""
