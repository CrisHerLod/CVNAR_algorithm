# Función soporte regla

def calcSupport(data, individual_values, individual_attribute_types):
    support_ant = 0
    support_cons = 0
    support_rule = 0
    support = []
    # Iterate over instances
    for i in data.index:
        verifyAnt = [] 
        verifyCons = [] 
        # For each column verify if the value of that instance is in the range given by the individual
        for c in range(len(data.columns)):
            if (data.iloc[i,c] >= individual_values[c*2]) & (data.iloc[i,c] <= individual_values[c*2+1]):
                if individual_attribute_types[c*2] == 1:
                    verifyAnt.append(True)
                elif individual_attribute_types[c*2] == 2:
                    verifyCons.append(True)
            else:
                if individual_attribute_types[c*2] == 1:
                    verifyAnt.append(False)
                elif individual_attribute_types[c*2] == 2:
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
    support.append(support_ant)
    support.append(support_cons)
    support.append(support_rule)
    return support

