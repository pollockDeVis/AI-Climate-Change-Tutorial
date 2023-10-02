# AI-Climate-Change-Tutorial

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/pollockDeVis/AI-Climate-Change-Tutorial/main?urlpath=https%3A%2F%2Fgithub.com%2FpollockDeVis%2FAI-Climate-Change-Tutorial%2Fblob%2Fmain%2Fai_tutorial.ipynb)

### Climate Policymaking : a decision-making problem about CO2 mitigation

[Adapted from EMA Workbench Lakeproblem Example](https://github.com/quaquel/EMAworkbench/blob/master/ema_workbench/examples/example_lake_model.py)

The Climate Change Problem forms a hypothetical scenario where the global community makes the decision on the amount of annual CO2 emissions to be released. The challenge is, if the CO2 concentration in the atmosphere surpasses a certain critical threshold or a "tipping point", it may cause irreversible and dangerous changes to the global climate system.

The Climate Change model has 4 **outcome indicators**:

1. **CO2_concentration**: The average concentration of CO2 in the atmosphere over a given timeframe, which we aim to minimize.

2. **economic_welfare**: The economic benefits derived from emitting CO2 minus the costs of having excessive CO2 in the atmosphere, which we aim to maximize.

3. **emission_inertia**: Inertia is maximized by setting an annual reduction limit on emissions, thereby preventing rapid declines in emissions that would require massive investments, and measured by the fraction of years where emission reductions stay below the set limit.

4. **reliability**: The fraction of years when the CO2 concentration in the atmosphere is below the critical threshold, which we aim to maximize to prevent triggering dangerous climate disruptions.

The Climate Change Problem is characterized by both stochastic uncertainty and **deep uncertainty**. The stochastic uncertainty arises from the natural emissions of CO2. In order to reduce this form of uncertainty, multiple replications are performed, and the average over these replications is taken. Deep uncertainty involves uncertainty about the mean and standard deviation of the log-normal distribution representing natural emissions, Earth's natural CO2 absorption rate, the natural emission rate of CO2, and the discount rate. Based on scientific understanding, ranges for these deeply uncertain factors can be established, as well as their best estimate or default values.

|Parameter	|Range	        |Default value| Description |
|-----------|--------------:|------------:|---------------------------:|
|$\mu$    	|0.01 – 0.05	|0.02         | Mean of the log-normal distribution representing the natural variability in CO2 emissions |
|$\sigma$	|0.001 – 0.005 	|0.0017       | Standard deviation of the log-normal distribution representing the natural variability in CO2 emissions |
|$b$      	|0.1 – 0.45	    |0.42         | Earth’s natural CO2 absorption rate, representing the rate at which CO2 is removed from the atmosphere |
|$q$	    |2 – 4.5	    |2            | Represents a decay rate in the concentration of CO2 in the atmosphere due to oceanic absorption |
|$\delta$	|0.93 – 0.99	|0.98         | Discount rate for the economic welfare calculation, indicating the decrease in future benefits compared to present benefits |

 We employ a **closed-loop** version of the model, which means that anthropogenic emissions, represented as $a_t$, is dependent on $X_t$ (the CO2 concentration in the atmosphere at time t). For instance, we can lower CO2 emissions when approaching the critical threshold. We achieve adaptive policy using "cubic radial basis functions", following the [EMODPS framework](https://doi.org/10.1061/(ASCE)WR.1943-5452.0000570)

