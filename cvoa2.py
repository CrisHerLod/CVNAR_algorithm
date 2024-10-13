from copy import deepcopy
import numpy as np
from numpy import mean
import sys as sys
import random as random
from individual import Individual
from sklearn.preprocessing import MinMaxScaler
import pandas as pd

class CVOA:
    MIN_SPREAD = 0
    MAX_SPREAD = 5
    MIN_SUPERSPREAD = 6
    MAX_SUPERSPREAD = 15
    SOCIAL_DISTANCING = 7
    P_ISOLATION = 0.7
    P_TRAVEL = 0.1
    P_REINFECTION = 0.001
    SUPERSPREADER_PERC = 0.1
    DEATH_PERC = 0.06 

    def __init__(self, max_time, data, n_solutions, objF):
        self.infected = []
        self.recovered = []
        self.deaths = []
        self.max_time = max_time
        self.data = data
        self.size = (len(data.columns))*2
        self.n_solutions = n_solutions
        self.bestSolutions = []
        self.bestSolutionEachIteration = []
        self.meanEachIteration = []
        self.stddevEachIteration = []
        self.avgBestFitnessDistance = []
        self.objF = objF
    
    def propagateDisease(self, time):
        new_infected_list = []
        # Step 1. Assess fitness for each individual.
        for x in self.infected:
            x.fitness = self.fitness(x.values,x.attributeType)
            # If x.fitness is NaN, move from infected list to deaths lists
            if np.isnan(x.fitness):
                self.deaths.append(x)
                self.infected.remove(x)
        
        # Step 2. Sort the infected list by fitness (descendent).
        self.infected = sorted(self.infected, key=lambda i: i.fitness, reverse=True)
        self.bestSolutionEachIteration.append(self.infected[0].fitness)
        total_fitness = sum(i.fitness for i in self.infected)
        mean_fitness = total_fitness / len(self.infected)
        self.meanEachIteration.append(mean_fitness)
        std_dev_fitness = np.std([i.fitness for i in self.infected])
        self.stddevEachIteration.append(std_dev_fitness)
        
        # Step 2.1 Add individuals to the bestSolutions until n_solutions is reached
        i=0
        while (len(self.bestSolutions)<self.n_solutions) and i<(len(self.infected)-1):
            if self.infected[i] not in self.bestSolutions:
                self.bestSolutions.append(deepcopy(self.infected[i]))
            i+=1
            
        self.bestSolutions = sorted(self.bestSolutions, key=lambda i: self.fitness(i.values,i.attributeType), reverse=True)
        # Step 3. Update best global solutions, if proceed.
        if self.n_solutions > 1:
            i=0
            while i < (len(self.bestSolutions)-1) and i < (len(self.infected)-1):
                for j in range(i,len(self.bestSolutions)):
                    if ((self.fitness(self.bestSolutions[j].values,self.bestSolutions[j].attributeType)==None) or (self.fitness(self.infected[i].values,self.infected[i].attributeType) > self.fitness(self.bestSolutions[j].values,self.bestSolutions[j].attributeType))) and self.infected[i] not in self.bestSolutions:
                        self.bestSolutions[j] = deepcopy(self.infected[i])
                        break
                i=j
        else:
            if self.fitness(self.bestSolutions[0].values,self.bestSolutions[0].attributeType)==None or self.fitness(self.infected[0].values,self.infected[0].attributeType) > self.fitness(self.bestSolutions[0].values,self.bestSolutions[0].attributeType):
                self.bestSolutions[0] = deepcopy(self.infected[0])
        # Step 3.1 Calculate distance between the best solutions
        self.avgBestFitnessDistance.append(self.avgBestFitnessDist())
        # Step 4. Assess indexes to point super-spreaders and deaths parts of the infected list.
        if len(self.infected)==1:
            idx_super_spreader=1
        else:
            idx_super_spreader = self.SUPERSPREADER_PERC * len(self.infected)
        if len(self.infected) == 1:
            idx_deaths = sys.maxsize
        else:
            idx_deaths = len(self.infected) - (self.DEATH_PERC * len(self.infected))
        
        # Step 5. Disease propagation.
        i = 0
        for x in self.infected:
            # Step 5.1 If the individual belongs to the death part, then die!
            if i >= idx_deaths:
                self.deaths.append(x)
                self.infected.remove(x)
            else:
                # Step 5.2 Determine the number of new infected individuals.
                if i < idx_super_spreader:  # This is the super-spreader!
                    ninfected = self.MIN_SUPERSPREAD + random.randint(0, self.MAX_SUPERSPREAD - self.MIN_SUPERSPREAD)
                else:
                    ninfected = random.randint(0, self.MAX_SPREAD)
                # Step 5.3 Determine whether the individual has traveled
                if random.random() < self.P_TRAVEL:
                    traveler = True
                else:
                    traveler = False
                # Step 5.4 Determine the travel distance, which indicates how many intervals of an individual will be infected.
                if traveler:
                    travel_distance = random.randint(1,self.size/2) 
                else:
                    travel_distance = 1 #The individual has not travel
                # Step 5.5 Infect!!
                for j in range(ninfected):
                    new_infected = x.infect(travel_distance=travel_distance)  # new_infected = infect(x, travel_distance)
                    # Propagate with no social distancing measures
                    if time < self.SOCIAL_DISTANCING:
                        if new_infected not in self.deaths and new_infected not in self.infected and new_infected not in new_infected_list and new_infected not in self.recovered:
                            new_infected_list.append(new_infected)
                        elif new_infected in self.recovered and new_infected not in new_infected_list:
                            if random.random() < self.P_REINFECTION:
                                new_infected_list.append(new_infected)
                                self.recovered.remove(new_infected)
                    else: # After SOCIAL_DISTANCING iterations, there is a P_ISOLATION of not being infected
                        if random.random() > self.P_ISOLATION:
                            if new_infected not in self.deaths and new_infected not in self.infected and new_infected not in new_infected_list and new_infected not in self.recovered:
                                new_infected_list.append(new_infected)
                            elif new_infected in self.recovered and new_infected not in new_infected_list:
                                if random.random() < self.P_REINFECTION:
                                    new_infected_list.append(new_infected)
                                    self.recovered.remove(new_infected)
                        else: # Those saved by social distancing are sent to the recovered list
                            if new_infected not in self.deaths and new_infected not in self.infected and new_infected not in new_infected_list and new_infected not in self.recovered:
                                self.recovered.append(new_infected)
            i+=1
            
        # Step 6. Add the current infected individuals to the recovered list.
        self.recovered.extend(self.infected)
        # Step 7. Update the infected list with the new infected individuals.
        self.infected = new_infected_list
    
    def run(self):
        epidemic = True
        time = 0

        # Step 1. Normalize the data
        '''min_max_scaler = MinMaxScaler()
        scaled_values = min_max_scaler.fit(self.data)
        print("Describe no scaled_values ", self.data.describe())
        print("No scaled_values ", self.data)
        scaled_data_values = min_max_scaler.transform(self.data)
        scaled_data_values_df = pd.DataFrame(scaled_data_values, columns=self.data.columns)
        self.data = scaled_data_values_df
        print("Describe Scaled_values ", self.data.describe())
        print("Scaled_values ", self.data)'''
        # Step 2. Infect to Patient Zero
        #pz = Individual.random(scaled_data_values_df)
        pz = Individual.random(self.data)
        while Individual.validateAttributeTypes(pz,pz.attributeType) == 0 or self.fitness(pz.values, pz.attributeType) == 0:
            #pz = Individual.random(scaled_data_values_df)
            pz = Individual.random(self.data)
        self.infected.append(pz)
        print("Patient Zero: " + str(pz) + "\n")
        print("Patient Zero attribute values: " + str(pz.values) + "\n")
        print("Patient Zero attribute type: " + str(pz.attributeType) + "\n")
        self.bestSolutions.append(deepcopy(pz))
        # Step 3. The main loop for the disease propagation
        while epidemic and time < self.max_time:
            self.propagateDisease(time)
            print("Iteration ", (time + 1))
            print("Best fitness so far: ",self.fitness(self.bestSolutions[0].values,self.bestSolutions[0].attributeType))
            print("Best individual: ", self.bestSolutions[0].kintegers)
            print("Infected: ", str(len(self.infected)), "; Recovered: ", str(len(self.recovered)), "; Deaths: ", str(len(self.deaths)))
            print("Recovered/Infected: " + str("{:.4f}".format(100 * ((len(self.recovered)) / (len(self.infected)+0.01))) + "%"))
            if not self.infected:
                epidemic = False
            time += 1
        return self.bestSolutions    
    
    def getBestFitnessEachIt(self):
        return self.bestSolutionEachIteration

    def getMeanFitnessEachIt(self):
        return self.meanEachIteration
    
    def getStdFitnessEachIt(self):
        return self.stddevEachIteration
    
    def fitness(self, individual_values, individual_attributeType):
        support_ant = 0
        support_cons = 0
        support_rule = 0
        # Iterate over instances
        for i in self.data.index:
            verifyAnt = []
            verifyCons = [] 
            # For each column verify if the value of that instance is in the range given by the individual
            for c in range(len(self.data.columns)):
                if (self.data.iloc[i,c] >= individual_values[c*2]) & (self.data.iloc[i,c] <= individual_values[c*2+1]):
                    if individual_attributeType[c*2] == 1:
                        verifyAnt.append(True)
                    elif individual_attributeType[c*2] == 2:
                        verifyCons.append(True)
                else:
                    if individual_attributeType[c*2] == 1:
                        verifyAnt.append(False)
                    elif individual_attributeType[c*2] == 2:
                        verifyCons.append(False)
            # When verifyAnt == True for all the columns, the support of the antecedent of the rule increases by 1
            if all(verifyAnt): 
                support_ant += 1
                # If verifyCons  == True for all the columns the rule support increases by 1
                if all(verifyCons):
                    support_rule += 1
            # For each instance, if verifyCons  == True for all the columns the consequent support increases by 1
            if all(verifyCons):
                support_cons += 1
        if support_ant !=0:
            conf = support_rule/support_ant # The confidence of the rule
        else:
            conf = 0
        #lift = conf*len(self.data.index)/support_cons # The lift metric
        if self.objF == '1':
            sumMetric = self.objectiveFunc1(support_ant,support_cons,support_rule,conf)
        else:
            sumMetric = self.objectiveFunc2(support_ant,support_cons,support_rule,conf)
        return sumMetric
    
    def objectiveFunc1(self,support_ant,support_cons,support_rule,conf):
        leverage = ((support_rule*len(self.data.index)) - (support_ant*support_cons)) / pow(len(self.data.index),2)
        #leverage_norm = (leverage + 0.25) / 0.5
        accuracy = (support_rule + (len(self.data.index)-(support_ant+support_cons-support_rule))) / len(self.data.index)
        metricResult = accuracy + conf + leverage
        return metricResult
    
    def objectiveFunc2(self,support_ant,support_cons,support_rule,conf):
        if support_ant !=0:
            if (conf > support_cons/len(self.data.index)):
                cf = ((support_rule*len(self.data.index)) - (support_ant*support_cons)) / ((len(self.data.index)-support_cons)*support_ant)
            else:
                if support_cons !=0:
                    cf = ((support_rule*len(self.data.index)) - (support_ant*support_cons)) / (support_ant*support_cons)
                else:
                    cf= 0 
        else:
            cf = 0
        support = support_rule / len(self.data.index)
        metricResult = cf + conf + support
        return metricResult
    
    def avgBestFitnessDist(self):
        distancias = []
        if len(self.bestSolutions) > 1:
            for i in range(len(self.bestSolutions)):
                for j in range(i + 1, len(self.bestSolutions)):
                    distancia = self.calcular_distancia(self.bestSolutions[i].values, self.bestSolutions[j].values)  # Usar Euclidiana o Hamming
                    distancias.append(distancia)

            promedio_distancia = sum(distancias) / len(distancias)
        else:
            promedio_distancia = 0
        return promedio_distancia
    
    def calcular_distancia(self, regla1, regla2):
        regla1 = np.array(regla1)
        regla2 = np.array(regla2)

        return np.linalg.norm(regla1 - regla2)
    
    def getAvgBestFitnessDist(self):
        return self.avgBestFitnessDistance
                    
    
