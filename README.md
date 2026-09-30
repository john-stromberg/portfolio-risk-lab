# Portfolio Risk Lab - Monte Carlo Analysis

**Professional wealth advisor tool for portfolio risk analysis using Monte Carlo simulation.**

Simulate portfolio performance across multiple market scenarios to understand downside risk, probability of success, and distribution of outcomes. Includes Value at Risk (VaR), Conditional Value at Risk (CVaR), maximum drawdown analysis, and customizable rebalancing strategies.

## Features

- **Monte Carlo Simulation**: Geometric Brownian motion with historical correlations
- **Risk Metrics**:
  - Value at Risk (VaR) at 90% and 95% confidence levels
  - Conditional Value at Risk (CVaR) / Expected Shortfall
  - Maximum drawdown analysis
  - Return volatility and distribution metrics
- **Customizable Portfolio**:
  - Asset allocation across 9 asset classes
  - Rebalancing strategies (quarterly, semi-annual, annual, or never)
  - Configurable initial portfolio value and projection period
- **Interactive Visualization**:
  - Portfolio value projections over time
  - Distribution of ending values
  - Risk and return analysis
  - Success probability calculator

## Asset Classes

The simulator includes:
- US Large Cap Stocks
- US Small Cap Stocks
- International Developed
- Emerging Markets
- US Bonds (Aggregate)
- High Yield Bonds
- Real Estate (REITs)
- Commodities
- Cash/Money Market

Returns and volatilities are based on 20-year historical averages with realistic correlations.

## Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
git clone https://github.com/john-stromberg/portfolio-risk-lab.git
cd portfolio-risk-lab
pip install -r requirements.txt
```

### Running the App

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501`

## Usage

1. **Configure Portfolio**: Use the sidebar to adjust asset allocation, initial value, and rebalancing strategy
2. **Set Simulation Parameters**: Choose number of simulations and projection period
3. **Run Simulation**: Click "Run Simulation"
4. **Analyze Results**:
   - **Projected Paths**: View percentile trajectories
   - **Distribution**: See ending value distribution
   - **Risk Analysis**: Review VaR, CVaR, and drawdown metrics
   - **Success Analysis**: Calculate probability of reaching goals

## Project Structure

```
portfolio-risk-lab/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── simulators/
│   └── monte_carlo.py         # Monte Carlo simulation engine
├── calculators/
│   └── risk_metrics.py        # Risk analysis calculations
└── models/
	├── asset_classes.py       # Asset class definitions and correlations
	└── portfolio.py           # Portfolio model
```

## Technical Details

### Monte Carlo Method

Uses geometric Brownian motion with:
- Historical annual returns per asset class
- Historical volatility per asset class
- Realistic correlation matrix between assets
- Cholesky decomposition for generating correlated returns
- Monthly compounding over projection period

### Risk Metrics

- **VaR (Value at Risk)**: Estimated maximum loss at given confidence level
- **CVaR (Conditional VaR)**: Average loss in worst-case scenarios
- **Maximum Drawdown**: Peak-to-trough decline across all paths
- **Return Volatility**: Standard deviation of annualized returns

## Limitations

- Assumes historical return/volatility patterns continue
- Correlations are simplified historical averages
- Does not account for major macroeconomic regime shifts
- Results are for illustrative purposes only

## Future Enhancements

- Regime-switching models for different market conditions
- Stress testing scenarios
- Tax-aware analysis
- Multi-objective portfolio optimization
- Export to PDF reports
- Integration with wealth planning workflows

## License

MIT License - see LICENSE file for details

## Contact

Built as part of the advisory workflow suite. For integration or questions, contact the development team.
