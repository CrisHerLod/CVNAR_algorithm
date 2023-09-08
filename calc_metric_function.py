def calcMetric(data,supports):
    metrics = []
    support_ant=supports[0]
    support_cons=supports[1]
    support_rule=supports[2]
    if support_ant !=0:
        conf = support_rule/support_ant # The confidence of the rule
        if (conf > support_cons/len(data.index)):
            cf = ((support_rule*len(data.index)) - (support_ant*support_cons)) / ((len(data.index)-support_cons)*support_ant)
            cf2 = (conf - (support_cons/len(data.index))) / (1-(support_cons/len(data.index)))
        else:
            if support_cons !=0:
                cf = ((support_rule*len(data.index)) - (support_ant*support_cons)) / (support_ant*support_cons)
                cf2 = (conf - (support_cons/len(data.index))) / (support_cons/len(data.index))
            else:
                cf = 0
                cf2 = 0
    else:
        conf = 0
        cf = 0
        cf2 = 0
    if support_cons !=0:
        lift = conf*len(data.index)/support_cons
    else:
        lift = 0
    leverage = ((support_rule*len(data.index)) - (support_ant*support_cons)) / pow(len(data.index),2)
    leverage_norm = (leverage + 0.25) / 0.5
    leverage_norm2 = (support_rule/len(data.index)) - ((support_ant/len(data.index))*(support_cons/len(data.index)))
    accuracy = (support_rule + (len(data.index)-(support_ant+support_cons-support_rule))) / len(data.index)
    accuracy2 = (support_rule/len(data.index)) + (1-((support_ant/len(data.index))+(support_cons/len(data.index))-(support_rule/len(data.index))))
    support = support_rule / len(data.index)
    metrics.append(conf)
    metrics.append(lift)
    metrics.append(leverage_norm)
    metrics.append(accuracy)
    metrics.append(support)
    metrics.append(cf)
    metrics.append(cf2)
    metrics.append(leverage_norm2)
    metrics.append(accuracy2)

    return metrics
