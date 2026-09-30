"""
Monte Carlo simulation engine for portfolio projections.
Uses geometric Brownian motion with historical correlations.
"""

import numpy as np
import pandas as pd
from models.asset_classes import ASSET_CLASSES, CORRELATION_MATRIX


class MonteCarloSimulator:
    """Monte Carlo portfolio simulator."""

    def __init__(self, portfolio, asset_names, num_simulations=10000, num_years=30):
        """
        Initialize simulator.

        Args:
            portfolio: Portfolio object
            asset_names: list of asset class names in order
            num_simulations: number of simulation paths
            num_years: simulation horizon in years
        """
        self.portfolio = portfolio
        self.asset_names = asset_names
        self.num_simulations = num_simulations
        self.num_years = num_years
        self.num_periods = num_years * 12  # Monthly periods

        # Extract returns, volatilities, and correlation
        self.returns = np.array([
            ASSET_CLASSES[name]['annual_return'] for name in asset_names
        ])
        self.volatilities = np.array([
            ASSET_CLASSES[name]['volatility'] for name in asset_names
        ])

        # Build correlation matrix for the selected assets
        asset_indices = self._get_asset_indices()
        self.correlation_matrix = self._build_correlation_submatrix(asset_indices)

        # Cholesky decomposition for correlated returns
        self.chol = np.linalg.cholesky(self.correlation_matrix)

        # Storage for simulation results
        self.simulation_paths = None
        self.ending_values = None
        self.percentiles = None

    def _get_asset_indices(self):
        """Map asset names to indices in the full CORRELATION_MATRIX."""
        asset_class_keys = list(ASSET_CLASSES.keys())
        indices = []
        for name in self.asset_names:
            indices.append(asset_class_keys.index(name))
        return indices

    def _build_correlation_submatrix(self, indices):
        """Extract correlation submatrix for selected assets."""
        n = len(indices)
        corr = np.zeros((n, n))
        for i, idx_i in enumerate(indices):
            for j, idx_j in enumerate(indices):
                corr[i, j] = CORRELATION_MATRIX[idx_i][idx_j]
        return corr

    def run(self):
        """Execute Monte Carlo simulation."""
        n_assets = len(self.asset_names)
        allocations = np.array([
            self.portfolio.allocations[name] / 100 for name in self.asset_names
        ])

        # Paths: [num_simulations, num_periods + 1, n_assets]
        self.simulation_paths = np.zeros((self.num_simulations, self.num_periods + 1, n_assets))

        # Initial allocation values
        initial_values = self.portfolio.current_value * allocations
        self.simulation_paths[:, 0, :] = initial_values

        # Monthly returns and volatilities
        monthly_returns = self.returns / 12
        monthly_vols = self.volatilities / np.sqrt(12)

        # Run simulations
        for sim in range(self.num_simulations):
            for period in range(1, self.num_periods + 1):
                # Generate correlated random normal draws
                z = np.random.standard_normal(n_assets)
                corr_z = self.chol @ z

                # Geometric Brownian motion for each asset
                for asset in range(n_assets):
                    drift = monthly_returns[asset] - 0.5 * monthly_vols[asset] ** 2
                    diffusion = monthly_vols[asset] * corr_z[asset]
                    price_ratio = np.exp(drift + diffusion)

                    self.simulation_paths[sim, period, asset] = (
                        self.simulation_paths[sim, period - 1, asset] * price_ratio
                    )

        # Calculate portfolio values (sum across assets)
        portfolio_values = self.simulation_paths.sum(axis=2)  # [num_simulations, num_periods + 1]

        # Apply rebalancing if specified
        if self.portfolio.rebalance_frequency != 'never':
            portfolio_values = self._apply_rebalancing(portfolio_values)

        self.ending_values = portfolio_values[:, -1]

        # Calculate percentiles
        self.percentiles = {
            '10th': np.percentile(self.ending_values, 10),
            '25th': np.percentile(self.ending_values, 25),
            '50th': np.percentile(self.ending_values, 50),  # Median
            '75th': np.percentile(self.ending_values, 75),
            '90th': np.percentile(self.ending_values, 90),
        }

        return portfolio_values

    def _apply_rebalancing(self, portfolio_values):
        """Apply periodic rebalancing to portfolio paths."""
        rebalance_periods = {
            'quarterly': 3,
            'semi-annual': 6,
            'annual': 12
        }
        rebalance_period = rebalance_periods.get(self.portfolio.rebalance_frequency)

        if not rebalance_period:
            return portfolio_values

        # For simplicity, rebalance at specified intervals
        for period in range(rebalance_period, self.num_periods + 1, rebalance_period):
            # Rebalance proportionally to target allocations
            allocations = np.array([
                self.portfolio.allocations[name] / 100 for name in self.asset_names
            ])
            portfolio_values[:, period] = portfolio_values[:, period].sum() / len(self.asset_names)

        return portfolio_values

    def get_summary_stats(self):
        """Return summary statistics of simulation results."""
        if self.ending_values is None:
            raise RuntimeError("Run simulation first")

        return {
            'mean_ending_value': np.mean(self.ending_values),
            'median_ending_value': np.median(self.ending_values),
            'std_ending_value': np.std(self.ending_values),
            'min_ending_value': np.min(self.ending_values),
            'max_ending_value': np.max(self.ending_values),
            'percentiles': self.percentiles
        }

    def get_probability_of_success(self, target_value):
        """Calculate probability of reaching target value."""
        if self.ending_values is None:
            raise RuntimeError("Run simulation first")

        success_count = np.sum(self.ending_values >= target_value)
        return success_count / len(self.ending_values)

    def get_paths_dataframe(self):
        """Get simulation paths as DataFrame for visualization."""
        if self.simulation_paths is None:
            raise RuntimeError("Run simulation first")

        # For efficiency, return a subset of percentiles
        portfolio_values = self.simulation_paths.sum(axis=2)

        results = {}
        percentiles = [10, 25, 50, 75, 90]
        for p in percentiles:
            results[f'{p}th percentile'] = np.percentile(portfolio_values, p, axis=0)

        df = pd.DataFrame(results)
        df.index.name = 'Month'
        return df
