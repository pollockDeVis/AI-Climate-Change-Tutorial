from ema_workbench import (Model, RealParameter, ScalarOutcome)
import pandas as pd
from model import dps_lake_model

model = Model('lakeproblem', function=dps_lake_model)

#specify uncertainties
model.uncertainties = [RealParameter('b', 0.1, 0.45),
                       RealParameter('q', 2.0, 4.5),
                       RealParameter('mean', 0.01, 0.05),
                       RealParameter('stdev', 0.001, 0.005),
                       RealParameter('delta', 0.93, 0.99)]

# set levers
model.levers = [RealParameter("c1", -2, 2),
                RealParameter("c2", -2, 2),
                RealParameter("r1", 0, 2),
                RealParameter("r2", 0, 2),
                RealParameter("w1", 0, 1)]

#specify outcomes
# note how we need to explicitely indicate the direction
model.outcomes = [ScalarOutcome('max_P', kind=ScalarOutcome.MINIMIZE),
                  ScalarOutcome('utility', kind=ScalarOutcome.MAXIMIZE),
                  ScalarOutcome('inertia', kind=ScalarOutcome.MAXIMIZE),
                  ScalarOutcome('reliability', kind=ScalarOutcome.MAXIMIZE)]




#do the optimization-simulation
from ema_workbench import MultiprocessingEvaluator, ema_logging
from ema_workbench.em_framework.evaluators import BaseEvaluator

ema_logging.log_to_stderr(ema_logging.INFO)

with MultiprocessingEvaluator(model) as evaluator:
    results1 = evaluator.optimize(nfe=5e5, searchover='levers',
                                 epsilons=[0.1,]*len(model.outcomes))
    

#save the results - only objective values
results1.to_csv('results.csv')

#get the policies - values of parameters for each of the rbfs
policies = results1.iloc[:, :5]



from model.dps_lake_model import get_antropogenic_release
import numpy as np
import math



#create empty data frame fro the time series of release decisions
release_decisions = pd.DataFrame()



#for each policy, simulate the decisions over time
for policy in range(len(policies)):
    c1 = policies.iloc[policy, 0]
    c2 = policies.iloc[policy, 1]
    r1 = policies.iloc[policy, 2]
    r2 = policies.iloc[policy, 3]
    w1 = policies.iloc[policy, 4]

    myears = 100

    b=0.42
    q=2.0
    mean=0.02
    stdev=0.001
    delta=0.98
    alpha=0.4
    nsamples=100
    myears=100
    X = np.zeros((myears,))

    X[0] = 0.0
    decision = 0.1
    decisions = np.zeros(myears,)
    decisions[0] = decision
    natural_inflows = np.random.lognormal(
                math.log(mean**2 / math.sqrt(stdev**2 + mean**2)),
                math.sqrt(math.log(1.0 + stdev**2 / mean**2)),
                size=myears)

    for t in range(1, myears):

        # here we use the decision rule
        decision = get_antropogenic_release(X[t-1], c1, c2, r1, r2, w1)
        decisions[t] = decision

        X[t] = (1-b)*X[t-1] + X[t-1]**q/(1+X[t-1]**q) + decision +\
            natural_inflows[t-1]
        
    release_decisions[str(policy)] = pd.DataFrame(decisions)


#save release decisions as time series for each of the policy
release_decisions.to_csv('release_decisions.csv')
        
