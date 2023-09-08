import sys
import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from cvoa2 import CVOA
import time as time
from support_function import calcSupport
from calc_metric_function import calcMetric

if len(sys.argv) < 3:
    print("Error: the argument number must be three")
    sys.exit()

data = pd.read_csv(sys.argv[1], sep = ';')
objF = sys.argv[2]

epochs=[]
best_solutions=[]
best_values=[]
best_attributeType=[]
best_fitness=[]
ant_support=[]
cons_support=[]
rule_support=[]
conf_metric=[]
lift_metric=[]
leverage_metric=[]
accuracy_metric=[]
support_metric=[] 
cf_metric=[]
cf2_metric=[]
leverage2_metric=[]
accuracy2_metric=[]

cvoa = CVOA(max_time = 20, data = data, n_solutions=10, objF = objF)

time1 = int(round(time.time() * 1000))
solutions = cvoa.run() 
time2 = int(round(time.time() * 1000)) - time1

for n in range(len(solutions)):
    epochs.append(n)
    best_solutions.append(solutions[n].kintegers)
    best_values.append(solutions[n].values)
    best_attributeType.append(solutions[n].attributeType)
    best_fitness.append(cvoa.fitness(solutions[n].values,solutions[n].attributeType))
    calculateSupports = calcSupport(data, solutions[n].values,solutions[n].attributeType)
    ant_support.append(calculateSupports[0])
    cons_support.append(calculateSupports[1])
    rule_support.append(calculateSupports[2])
    calculateMetrics = calcMetric(data,calculateSupports)
    conf_metric.append(calculateMetrics[0])
    lift_metric.append(calculateMetrics[1])
    leverage_metric.append(calculateMetrics[2])
    accuracy_metric.append(calculateMetrics[3])
    support_metric.append(calculateMetrics[4])
    cf_metric.append(calculateMetrics[5])
    cf2_metric.append(calculateMetrics[6])
    leverage2_metric.append(calculateMetrics[7])
    accuracy2_metric.append(calculateMetrics[8])

print("Execution time: " + str(time2 / 60000) + " mins")
print("Best solutions: " + str(best_solutions))
print("Intervals values: " + str(best_values))
print("Attribute type values: " + str(best_attributeType))
print("Best fitness: " + str(best_fitness))
print("Ant support: " + str(ant_support))
print("Cons support: " + str(cons_support))
print("Rules support: " + str(rule_support))
print("Confidence metric: " + str(conf_metric))
print("Lift metric: " + str(lift_metric))
print("Leverage metric: " + str(leverage_metric))
print("Leverage metric 2: " + str(leverage2_metric))
print("Accuracy metric: " + str(accuracy_metric))
print("Accuracy metric 2: " + str(accuracy2_metric))
print("Support metric: " + str(support_metric))
print("Certainty Factor metric: " + str(cf_metric))
print("Certainty Factor metric 2: " + str(cf2_metric))

fig, ax = plt.subplots()
ax.set_ylabel('Fitness')
ax.set_title('Iteration')
plt.plot(epochs, best_fitness)
plt.savefig('./fitness_function.png')
