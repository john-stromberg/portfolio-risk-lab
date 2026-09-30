"""
Risk metrics and analytics from simulation results.
Includes VaR, CVaR, Sharpe ratio, and drawdown analysis.
"""

import numpy as np
import pandas as pd


class RiskMetricsCalculator:
    """Calculate risk metrics from Monte Carlo simulation."""

    def __init__(self, simulation_results, risk_free_rate=0.04):
        """
        Initialize calculator.

        Args:
            simulation_results: portfolio value paths from simulator [num_sims, num_periods]
            risk_free_rate: annual risk-free rate for Sharpe calculation
        """
        self.simulation_results = simulation_results
        self.risk_free_rate = risk_free_rate

    def value_at_risk(self, confidence_level=0.95):
        """
        Calculate Value at Risk (VaR).

        Args:
            confidence_level: confidence level (0.95 = 95% confidence)

        Returns:
            VaR in dollars and percentage
        """
        ending_values = self.simulation_results[:, -1]
        initial_value = self.simulation_results[0, 0]

        var_percentile = (1 - confidence_level) * 100
        var_value = np.percentile(ending_values, var_percentile)
        var_loss = initial_value - var_value
        var_pct = (var_loss / initial_value) * 100

        return {
            'var_value': var_value,
            'var_loss': var_loss,
            'var_pct': var_pct,
            'confidence_level': confidence_level
        }

    def conditional_value_at_risk(self, confidence_level=0.95):
        """
        Calculate Conditional Value at Risk (CVaR) / Expected Shortfall.
        Average loss in worst (1-confidence_level)% of scenarios.
        """
        ending_values = self.simulation_results[:, -1]
        initial_value = self.simulation_results[0, 0]

        var_percentile = (1 - confidence_level) * 100
        var_threshold = np.percentile(ending_values, var_percentile)

        worst_scenarios = ending_values[ending_values <= var_threshold]
        cvar_value = np.mean(worst_scenarios)
        cvar_loss = initial_value - cvar_value
        cvar_pct = (cvar_loss / initial_value) * 100

        return {
            'cvar_value': cvar_value,
            'cvar_loss': cvar_loss,
            'cvar_pct': cvar_pct,
            'confidence_level': confidence_level
        }

    def maximum_drawdown(self):
        """
        Calculate maximum drawdown across all simulation paths.

        Returns:
            Maximum drawdown percentage (worst case)
        """
        max_drawdowns = []

        for sim_path in self.simulation_results:
            running_max = np.maximum.accumulate(sim_path)
            drawdown = (sim_path - running_max) / running_max * 100
            max_drawdown = np.min(drawdown)
            max_drawdowns.append(max_drawdown)

        return {
            'worst_case_drawdown': np.min(max_drawdowns),
            'average_drawdown': np.mean(max_drawdowns),
            'percentile_90_drawdown': np.percentile(max_drawdowns, 90)
        }

    def return_analysis(self):
        """Analyze returns and volatility."""
        ending_values = self.simulation_results[:, -1]
        initial_value = self.simulation_results[0, 0]
        num_years = (self.simulation_results.shape[1] - 1) / 12

        total_returns = (ending_values - initial_value) / initial_value
        annualized_returns = (1 + total_returns) ** (1 / num_years) - 1

        # Volatility of returns
        return_volatility = np.std(annualized_returns)

        return {
            'median_total_return': np.median(total_returns),
            'median_annualized_return': np.median(annualized_returns),
            'annualized_return_volatility': return_volatility,
            'best_case_return': np.max(total_returns),
            'worst_case_return': np.min(total_returns)
        }

    def probability_metrics(self, target_value, minimum_acceptable_return=0.0):
        """
        Calculate probability-based metrics.

        Args:
            target_value: target ending portfolio value
            minimum_acceptable_return: minimum acceptable annual return

        Returns:
            Probability of success metrics
        """
        ending_values = self.simulation_results[:, -1]
        initial_value = self.simulation_results[0, 0]
        num_years = (self.simulation_results.shape[1] - 1) / 12

        prob_target = np.sum(ending_values >= target_value) / len(ending_values)

        # Probability of achieving minimum return
        required_terminal_value = initial_value * (1 + minimum_acceptable_return) ** num_years
        prob_min_return = np.sum(ending_values >= required_terminal_value) / len(ending_values)

        return {
            'prob_achieve_target': prob_target,
            'prob_minimum_return': prob_min_return,
            'target_value': target_value,
            'minimum_acceptable_return': minimum_acceptable_return
        }

    def distribution_summary(self):
        """Summarize distribution of ending values."""
        ending_values = self.simulation_results[:, -1]

        return {
            'percentile_10': np.percentile(ending_values, 10),
            'percentile_25': np.percentile(ending_values, 25),
            'median': np.percentile(ending_values, 50),
            'percentile_75': np.percentile(ending_values, 75),
            'percentile_90': np.percentile(ending_values, 90),
            'mean': np.mean(ending_values),
            'std': np.std(ending_values),
            'skewness': pd.Series(ending_values).skew(),
            'kurtosis': pd.Series(ending_values).kurtosis()
        }
