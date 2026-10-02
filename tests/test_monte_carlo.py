import numpy as np

from models.portfolio import Portfolio
from simulators.monte_carlo import MonteCarloSimulator


def test_rebalanced_simulation_preserves_target_weights():
    portfolio = Portfolio(
        {
            "US Large Cap Stocks": 60,
            "US Bonds (Aggregate)": 40,
        },
        initial_value=1_000_000,
    )
    portfolio.set_rebalance_frequency("annual")

    simulator = MonteCarloSimulator(
        portfolio,
        ["US Large Cap Stocks", "US Bonds (Aggregate)"],
        num_simulations=20,
        num_years=2,
    )

    paths = simulator.run()

    rebalanced = simulator.simulation_paths[:, 12, :]
    totals = rebalanced.sum(axis=1, keepdims=True)
    weights = rebalanced / totals

    assert paths.shape == (20, 25)
    assert np.allclose(weights[:, 0], 0.60)
    assert np.allclose(weights[:, 1], 0.40)
    assert simulator.ending_values.shape == (20,)
