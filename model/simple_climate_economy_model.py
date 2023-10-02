import math

import numpy as np
from scipy.optimize import brentq

from ema_workbench import (
    Model,
    RealParameter,
    ScalarOutcome,
    Constant,
    ema_logging,
    MultiprocessingEvaluator,
    CategoricalParameter,
    Scenario,
)

from ema_workbench.em_framework.optimization import ArchiveLogger, EpsilonProgress


def get_emission_reduction(xt, c1, c2, r1, r2, w1):
    """
    Parameters
    ----------
    xt : float
         CO2 concentration in the atmosphere at time t
    c1 : float
         center rbf 1
    c2 : float
         center rbf 2
    r1 : float
         ratius rbf 1
    r2 : float
         ratius rbf 2
    w1 : float
         weight of rbf 1

    note:: w2 = 1 - w1
    """
    rule = w1 * (abs(xt - c1) / r1) ** 3 + (1 - w1) * (abs(xt - c2) / r2) ** 3
    at1 = max(rule, 0.01)
    at = min(at1, 0.1)

    return at


def climate_policy_model(
    b=0.42,  # Earth’s natural CO2 absorption rate
    q=2.0,  # Represents decay rate in CO2 concentration in the atmosphere due to oceanic absorption
    mean=0.02,  # Mean of natural CO2 emissions
    stdev=0.0017,  # Standard deviation of natural CO2 emissions
    delta=0.98,  # Discount rate for the economic welfare calculation
    alpha=0.4,  # Utility from pollution
    nsamples=100,  # Monte Carlo sampling of natural emissions
    myears=1,  # Model runtime
    c1=0.25,
    c2=0.25,
    r1=0.5,
    r2=0.5,
    w1=0.5,
):
    Ccrit = brentq(lambda x: x**q / (1 + x**q) - b * x, 0.01, 1.5)
    X = np.zeros((myears,))
    average_daily_C = np.zeros((myears,))
    reliability = 0.0
    inertia = 0
    economic_welfare = 0

    for _ in range(nsamples):
        X[0] = 0.0
        decision = 0.1

        decisions = np.zeros((myears,))
        decisions[0] = decision

        natural_emissions = np.random.lognormal(
            math.log(mean**2 / math.sqrt(stdev**2 + mean**2)),
            math.sqrt(math.log(1.0 + stdev**2 / mean**2)),
            size=myears,
        )

        for t in range(1, myears):
            # Apply decision rule
            decision = get_emission_reduction(X[t - 1], c1, c2, r1, r2, w1)
            decisions[t] = decision

            X[t] = (
                (1 - b) * X[t - 1]
                + X[t - 1] ** q / (1 + X[t - 1] ** q)
                + decision
                + natural_emissions[t - 1]
            )
            average_daily_C[t] += X[t] / nsamples

        reliability += np.sum(X < Ccrit) / (nsamples * myears)
        inertia += np.sum(np.absolute(np.diff(decisions) < 0.02)) / (nsamples * myears)
        economic_welfare += (
            np.sum(alpha * decisions * np.power(delta, np.arange(myears))) / nsamples
        )
    max_CO2 = np.max(average_daily_C)

    return max_CO2, economic_welfare, inertia, reliability


if __name__ == "__main__":
    ema_logging.log_to_stderr(ema_logging.INFO)

    # instantiate the model
    climate_model = Model("climatepolicymodel", function=climate_policy_model)

    # specify uncertainties
    climate_model.uncertainties = [
        RealParameter("b", 0.1, 0.45),
        RealParameter("q", 2.0, 4.5),
        RealParameter("mean", 0.01, 0.05),
        RealParameter("stdev", 0.001, 0.005),
        RealParameter("delta", 0.93, 0.99),
    ]

    # set levers
    climate_model.levers = [
        RealParameter("c1", -2, 2),
        RealParameter("c2", -2, 2),
        RealParameter("r1", 0, 2),
        RealParameter("r2", 0, 2),
        RealParameter("w1", 0, 1),
    ]

    # specify outcomes
    climate_model.outcomes = [
        ScalarOutcome("max_CO2", kind=ScalarOutcome.MINIMIZE),
        ScalarOutcome("economic_welfare", kind=ScalarOutcome.MAXIMIZE),
        ScalarOutcome("emission_inertia", kind=ScalarOutcome.MAXIMIZE),
        ScalarOutcome("reliability", kind=ScalarOutcome.MAXIMIZE),
    ]

    # override some of the defaults of the model
    climate_model.constants = [
        Constant("alpha", 0.4),
        Constant("nsamples", 100),
        Constant("myears", 100),
    ]

    # reference is optional, but can be used to implement search for
    # various user specified scenarios along the lines suggested by
    # Watson and Kasprzyk (2017)
    reference = Scenario("reference", b=0.4, q=2, mean=0.02, stdev=0.0017)

    convergence_metrics = [
        ArchiveLogger(
            "./data",
            [l.name for l in climate_model.levers],
            [o.name for o in climate_model.outcomes],
            base_filename="climate_model_dps_archive.tar.gz",
        ),
        EpsilonProgress(),
    ]

    with MultiprocessingEvaluator(climate_model) as evaluator:
        results, convergence = evaluator.optimize(
            searchover="levers",
            nfe=100000,
            epsilons=[0.1] * len(climate_model.outcomes),
            reference=reference,
            convergence=convergence_metrics,
        )
