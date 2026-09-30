"""
Portfolio Risk Lab - Monte Carlo Simulation Tool
Interactive Streamlit app for portfolio risk analysis and Monte Carlo projections.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from simulators.monte_carlo import MonteCarloSimulator
from calculators.risk_metrics import RiskMetricsCalculator
from models.portfolio import Portfolio
from models.asset_classes import get_all_asset_classes

# Page config
st.set_page_config(
    page_title="Portfolio Risk Lab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Portfolio Risk Lab - Monte Carlo Analysis")
st.markdown("Simulate portfolio performance and analyze downside risk with Monte Carlo methods.")

# Sidebar configuration
st.sidebar.header("Portfolio Configuration")

# Asset allocation
st.sidebar.subheader("Asset Allocation")
available_assets = list(get_all_asset_classes().keys())

# Remove cash from default to simplify
default_assets = {
    'US Large Cap Stocks': 40,
    'International Developed': 20,
    'US Bonds (Aggregate)': 35,
    'Real Estate (REITs)': 5
}

allocations = {}
total_allocation = 0
for asset in default_assets.keys():
    pct = st.sidebar.slider(
        f"{asset}",
        min_value=0,
        max_value=100,
        value=default_assets[asset],
        step=1
    )
    allocations[asset] = pct
    total_allocation += pct

# Show total allocation
allocation_col = st.sidebar.container()
if total_allocation != 100:
    allocation_col.warning(f"⚠️ Total allocation: {total_allocation}% (must be 100%)")
else:
    allocation_col.success(f"✓ Total allocation: {total_allocation}%")

# Portfolio parameters
st.sidebar.subheader("Portfolio Parameters")
initial_value = st.sidebar.number_input(
    "Initial Portfolio Value ($)",
    min_value=100000,
    max_value=10000000,
    value=1000000,
    step=100000
)

rebalance_freq = st.sidebar.selectbox(
    "Rebalancing Frequency",
    ['quarterly', 'semi-annual', 'annual', 'never'],
    index=2
)

# Simulation parameters
st.sidebar.subheader("Simulation Parameters")
num_simulations = st.sidebar.slider(
    "Number of Simulations",
    min_value=1000,
    max_value=50000,
    value=10000,
    step=1000
)

num_years = st.sidebar.slider(
    "Projection Period (Years)",
    min_value=1,
    max_value=40,
    value=30,
    step=1
)

# Run simulation button
if st.sidebar.button("🚀 Run Simulation", use_container_width=True):
    if total_allocation == 100:
        # Create portfolio
        portfolio = Portfolio(allocations, initial_value)
        portfolio.set_rebalance_frequency(rebalance_freq)

        # Run simulator
        with st.spinner("Running Monte Carlo simulation..."):
            simulator = MonteCarloSimulator(
                portfolio,
                list(allocations.keys()),
                num_simulations=num_simulations,
                num_years=num_years
            )
            portfolio_paths = simulator.run()

            # Store in session state
            st.session_state.simulator = simulator
            st.session_state.portfolio_paths = portfolio_paths
            st.session_state.portfolio = portfolio

        st.success("✓ Simulation complete!")
    else:
        st.error("Portfolio allocation must sum to 100%")

# Display results if simulation has been run
if 'simulator' in st.session_state:
    simulator = st.session_state.simulator
    portfolio_paths = st.session_state.portfolio_paths
    portfolio = st.session_state.portfolio

    # Summary statistics
    st.header("Simulation Results")

    col1, col2, col3, col4 = st.columns(4)

    summary = simulator.get_summary_stats()

    with col1:
        st.metric(
            "Initial Portfolio",
            f"${portfolio.initial_value:,.0f}"
        )

    with col2:
        st.metric(
            "Median Ending Value",
            f"${summary['median_ending_value']:,.0f}",
            f"+{((summary['median_ending_value'] / portfolio.initial_value - 1) * 100):.1f}%"
        )

    with col3:
        st.metric(
            "10th Percentile",
            f"${summary['percentiles']['10th']:,.0f}",
            f"{((summary['percentiles']['10th'] / portfolio.initial_value - 1) * 100):.1f}%"
        )

    with col4:
        st.metric(
            "90th Percentile",
            f"${summary['percentiles']['90th']:,.0f}",
            f"+{((summary['percentiles']['90th'] / portfolio.initial_value - 1) * 100):.1f}%"
        )

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📈 Projected Paths", "📊 Distribution", "⚠️ Risk Analysis", "🎯 Success Analysis"]
    )

    # Tab 1: Projected paths
    with tab1:
        st.subheader("Portfolio Value Projections")

        paths_df = simulator.get_paths_dataframe()

        fig = go.Figure()

        for col in paths_df.columns:
            fig.add_trace(go.Scatter(
                y=paths_df[col],
                mode='lines',
                name=col,
                line=dict(width=2)
            ))

        fig.update_layout(
            title="Portfolio Value Over Time (Selected Percentiles)",
            xaxis_title="Months",
            yaxis_title="Portfolio Value ($)",
            hovermode='x unified',
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

    # Tab 2: Distribution of ending values
    with tab2:
        st.subheader("Distribution of Ending Portfolio Values")

        ending_values = simulator.ending_values

        fig = go.Figure()

        fig.add_trace(go.Histogram(
            x=ending_values,
            nbinsx=50,
            name='Outcomes',
            marker=dict(color='rgba(0, 100, 200, 0.7)')
        ))

        # Add percentile lines
        for pct, val in simulator.percentiles.items():
            fig.add_vline(
                x=val,
                line_dash="dash",
                line_color="red" if pct in ['10th', '25th'] else "green",
                annotation_text=pct,
                annotation_position="top"
            )

        fig.update_layout(
            title="Distribution of Portfolio Values After 30 Years",
            xaxis_title="Ending Portfolio Value ($)",
            yaxis_title="Frequency",
            height=450
        )

        st.plotly_chart(fig, use_container_width=True)

        # Distribution statistics
        dist_summary = RiskMetricsCalculator(portfolio_paths).distribution_summary()

        dist_df = pd.DataFrame({
            'Metric': list(dist_summary.keys()),
            'Value': [f"${v:,.0f}" if isinstance(v, (int, float)) and v > 100 else f"{v:.2f}" 
                      for v in dist_summary.values()]
        })

        st.dataframe(dist_df, use_container_width=True)

    # Tab 3: Risk metrics
    with tab3:
        st.subheader("Risk Analysis")

        risk_calc = RiskMetricsCalculator(portfolio_paths)

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Value at Risk (VaR)**")
            var_95 = risk_calc.value_at_risk(0.95)
            st.write(f"95% VaR: ${var_95['var_value']:,.0f} (Loss: ${var_95['var_loss']:,.0f}, {var_95['var_pct']:.1f}%)")

            var_90 = risk_calc.value_at_risk(0.90)
            st.write(f"90% VaR: ${var_90['var_value']:,.0f} (Loss: ${var_90['var_loss']:,.0f}, {var_90['var_pct']:.1f}%)")

        with col2:
            st.write("**Conditional Value at Risk (CVaR)**")
            cvar_95 = risk_calc.conditional_value_at_risk(0.95)
            st.write(f"95% CVaR: ${cvar_95['cvar_value']:,.0f} (Loss: ${cvar_95['cvar_loss']:,.0f}, {cvar_95['cvar_pct']:.1f}%)")

            cvar_90 = risk_calc.conditional_value_at_risk(0.90)
            st.write(f"90% CVaR: ${cvar_90['cvar_value']:,.0f} (Loss: ${cvar_90['cvar_loss']:,.0f}, {cvar_90['cvar_pct']:.1f}%)")

        st.divider()

        st.write("**Maximum Drawdown**")
        dd = risk_calc.maximum_drawdown()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Worst Case", f"{dd['worst_case_drawdown']:.1f}%")
        with col2:
            st.metric("Average Case", f"{dd['average_drawdown']:.1f}%")
        with col3:
            st.metric("90th Percentile", f"{dd['percentile_90_drawdown']:.1f}%")

        st.divider()

        st.write("**Return Analysis**")
        ret = risk_calc.return_analysis()
        ret_df = pd.DataFrame({
            'Metric': [
                'Median Total Return',
                'Median Annualized Return',
                'Return Volatility',
                'Best Case Total Return',
                'Worst Case Total Return'
            ],
            'Value': [
                f"{ret['median_total_return']*100:.1f}%",
                f"{ret['median_annualized_return']*100:.2f}%",
                f"{ret['annualized_return_volatility']*100:.2f}%",
                f"{ret['best_case_return']*100:.1f}%",
                f"{ret['worst_case_return']*100:.1f}%"
            ]
        })
        st.dataframe(ret_df, use_container_width=True)

    # Tab 4: Success analysis
    with tab4:
        st.subheader("Success Probability Analysis")

        col1, col2 = st.columns(2)

        with col1:
            target_value = st.number_input(
                "Target Ending Value ($)",
                min_value=portfolio.initial_value,
                max_value=int(np.max(simulator.ending_values)) + 1000000,
                value=int(portfolio.initial_value * 2),
                step=100000
            )

        with col2:
            min_return = st.number_input(
                "Minimum Acceptable Annual Return (%)",
                min_value=-10.0,
                max_value=20.0,
                value=3.0,
                step=0.5
            ) / 100

        risk_calc = RiskMetricsCalculator(portfolio_paths)

        prob_metrics = risk_calc.probability_metrics(target_value, min_return)

        col1, col2 = st.columns(2)

        with col1:
            prob_target = prob_metrics['prob_achieve_target']
            st.metric(
                f"Probability of Reaching ${target_value:,.0f}",
                f"{prob_target*100:.1f}%"
            )

        with col2:
            prob_min = prob_metrics['prob_minimum_return']
            st.metric(
                f"Probability of {min_return*100:.1f}% Annual Return",
                f"{prob_min*100:.1f}%"
            )

else:
    st.info(
        "👈 Configure your portfolio in the sidebar and click **Run Simulation** to begin analysis."
    )

# Footer
st.divider()
st.markdown(
    """
    **Portfolio Risk Lab** uses Monte Carlo simulation with historical returns and correlations.
    Results are for illustrative purposes and should not be considered as investment advice.
    """
)
