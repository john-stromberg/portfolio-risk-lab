"""
Portfolio model with allocation and rebalancing logic.
"""

class Portfolio:
    """Represents a portfolio of asset allocations."""

    def __init__(self, allocations, initial_value=1000000):
        """
        Initialize portfolio.

        Args:
            allocations: dict of {asset_name: percentage} (must sum to 100)
            initial_value: starting portfolio value in dollars
        """
        self.allocations = allocations
        self.initial_value = initial_value
        self.current_value = initial_value
        self.rebalance_frequency = 'annual'  # quarterly, semi-annual, annual, never

        # Validate allocations sum to 100%
        total = sum(allocations.values())
        if abs(total - 100) > 0.01:
            raise ValueError(f"Allocations must sum to 100%, got {total}")

    def get_allocation_values(self):
        """Get dollar value for each asset in the portfolio."""
        return {
            asset: self.current_value * (pct / 100)
            for asset, pct in self.allocations.items()
        }

    def update_value(self, new_value):
        """Update portfolio value (e.g., after simulation step)."""
        self.current_value = new_value

    def rebalance(self):
        """Return the portfolio to target allocations."""
        allocation_values = self.get_allocation_values()
        return allocation_values

    def set_rebalance_frequency(self, frequency):
        """Set rebalancing frequency: 'quarterly', 'semi-annual', 'annual', 'never'."""
        self.rebalance_frequency = frequency

    def to_dict(self):
        """Serialize portfolio for display/export."""
        return {
            'allocations': self.allocations,
            'initial_value': self.initial_value,
            'current_value': self.current_value,
            'rebalance_frequency': self.rebalance_frequency
        }
