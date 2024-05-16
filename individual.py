import random as random
from copy import deepcopy
import math
import numpy as np

class Individual:
    P_MUTATION_ATT = 0.25
    ATT_NUMBER = 2
    P_ANTECEDENT = 0.7

    def __init__(self, data):
        self.data = data
        self.length = (len(data.columns))*2
        self.kintegers = [0]*self.length
        self.values = [0]*self.length
        self.attributeType = [0]*self.length
        self.fitness = None
        self.n_instances = len(self.data.index) #number of instances
    
    def kToMinValue(self, c):
        column = self.data.iloc[:,c]
        column_sorted = sorted(column) # Sort the column
        minValue = column_sorted[self.kintegers[c*2]] # Select the k smallest value of the column
        return minValue
    
    def kToMaxValue(self, c):
        column = self.data.iloc[:,c]
        column_sorted = sorted(column) # Sort the column
        maxValue = column_sorted[len(column_sorted)-1-self.kintegers[c*2+1]] # Select the k biggest value of the column
        return maxValue
    
    def random(data):
        indv = Individual(data)
        # For each column of the dataset, ramdomly select the extremes of a range
        for c in range(len(indv.data.columns)):
            # Generate random value to determine if the attribute belongs to the antecedent (1), to the consequent (2) or does not belong to the rule (0)
            attributeType = random.randint(0, 2)
            # Even positions of the list values store the minimum of the range 
            indv.kintegers[c*2] = random.randint(0, indv.n_instances-2) # Select a random integer k between 0 and n_instances-2
            min_value = indv.kToMinValue(c)
            indv.values[c*2] = min_value # Store the value
            # Odd positions of the list values store the minimum of the range
            indv.kintegers[c*2+1] = random.randint(0, indv.n_instances-2-indv.kintegers[c*2]) # Select a random integer between 0 and the above k
            max_value = indv.kToMaxValue(c)
            indv.values[c*2+1] = max_value
            while(max_value <= min_value): # Repeat until max_value > min_value
                indv.kintegers[c*2] = random.randint(0, indv.n_instances-2)
                min_value = indv.kToMinValue(c)
                indv.values[c*2] = min_value
                indv.kintegers[c*2+1] = random.randint(0, indv.n_instances-2-indv.kintegers[c*2])
                max_value = indv.kToMaxValue(c)
                indv.values[c*2+1] = max_value       
            indv.attributeType[c*2] = attributeType
            indv.attributeType[c*2+1] = attributeType
        return indv   

    def __str__(self):
        return str(self.kintegers) 

    def infectInterval(self, idx_interval):
        # We infect an interval of the individual by increasing/decreasing it by a percentage 
        percentages=[0.25,0.5,0.75]
        interval=[self.kintegers[idx_interval*2],self.kintegers[idx_interval*2+1]]
        amplitude=self.n_instances-1-interval[1]-interval[0] 
        difference=round(amplitude*percentages[random.randint(0,2)]) #Difference between the old and new amplitudes
        #switch=0 increase amplitude
        #switch=1 reduce amplitude
        # If amplitude == 1 it can only be increased, if ampitude > 1, it is randomly increased/reduced
        if amplitude==1:
            switch=0
        else:
            switch=random.randint(0,1)
    
        if switch==0:
            # To increase the amplitude, half of the difference is substracted
            # If the extrems of the interval are < 0, they are assigned to 0
            if math.floor(interval[0]-difference/2) in np.arange(0,interval[0]):
                interval[0]=math.floor(interval[0]-difference/2)
            else:
                interval[0]=0
            if math.floor(interval[1]-difference/2) in np.arange(0,interval[1]):
                interval[1]=math.floor(interval[1]-difference/2)
            else:
                interval[1]=0
        else: #swithc=1
            if amplitude==1:
                pass
            else:
                # To decrease the amplitude, half of the difference is added
                # We use conditions to ensure that the minimum extreme is n_instances-2 at most
                if math.ceil(interval[0]+difference/2) in np.arange(0,self.n_instances-2):
                    interval[0]=math.ceil(interval[0]+difference/2)
                else:
                    interval[0]=self.n_instances-2
                    interval[1]=0
                # We ensure that the maximum extreme is superior than the minimum
                if math.ceil(interval[1]+difference/2) in np.arange(0,self.n_instances-2-interval[0]):
                    interval[1]=math.ceil(interval[1]+difference/2)
                else:
                    interval[1]=self.n_instances-2-interval[0]
        self.kintegers[idx_interval*2] = interval[0]
        self.values[idx_interval*2] = self.kToMinValue(idx_interval)
        self.kintegers[idx_interval*2+1] = interval[1]
        self.values[idx_interval*2+1] = self.kToMaxValue(idx_interval)
    
    def infectAttribute(self, idx_interval):
        attributeType = random.randint(0, 2)
        interval=[self.attributeType[idx_interval*2],self.attributeType[idx_interval*2+1]]
        self.attributeType[idx_interval*2] = attributeType
        self.attributeType[idx_interval*2+1] = attributeType
        while interval[0] == attributeType:
            attributeType = random.randint(0, 2)
            self.attributeType[idx_interval*2] = attributeType
            self.attributeType[idx_interval*2+1] = attributeType
    
    def infectAllAttributes(self):
        lengthAttributes = len(self.attributeType)
        for c in range((int(lengthAttributes / 2))):
            #Generate random value to determine if the attribute belongs to the antecedent (1), to the consequent (2) or does not belong to the rule (0)
            attributeType = random.randint(0, 2)
            self.attributeType[c*2] = attributeType
            self.attributeType[c*2+1] = attributeType

    def infect(self, travel_distance):
        mutated = deepcopy(self)
        total_size = mutated.length/2
        # Infect 'nmutated' random intervals of the individual 'mutated'.
        mutated_intervals = []
        mutated_intervals_attributes = []
        i = 0
        while i < travel_distance:
            interv = random.randint(0, total_size-1)
            interv_att = random.randint(0, total_size-1)
            if interv not in mutated_intervals:
                # Infect the interval in the position idx_interval of the individual.
                #if random.random() > self.P_MUTATION_ATT:
                mutated.infectInterval(idx_interval=interv)
                #else:
                mutated_intervals.append(interv)
            if interv_att not in mutated_intervals_attributes:
                mutated.infectAttribute(idx_interval=interv_att)
                if self.validateAttributeTypes(mutated.attributeType) == 0:
                    mutated.infectAllAttributes()
                    while self.validateAttributeTypes(mutated.attributeType) == 0:
                        mutated.infectAllAttributes()
                mutated_intervals_attributes.append(interv_att)
            i+=1
        return mutated
    
    def __eq__(self, other):
        return self.kintegers==other.kintegers
    
    def validateAttributeTypes(self, pzAttributeType): 
        existsAntCon = 0
        attributeCount = len(pzAttributeType) / 2
        antCount = pzAttributeType.count(1)
        consCount = pzAttributeType.count(2)
        if attributeCount > self.ATT_NUMBER:
            if 1 in pzAttributeType and 2 in pzAttributeType and antCount > consCount:
                existsAntCon = 1
        else:
            if 0 not in pzAttributeType:
                if 1 in pzAttributeType and 2 in pzAttributeType:
                    existsAntCon = 1                     
        return existsAntCon