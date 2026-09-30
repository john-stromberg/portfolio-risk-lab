"""
Asset class models with historical return, volatility, and correlation data.
Based on 20-year historical averages.
"""

ASSET_CLASSES = {
    'US Large Cap Stocks': {
        'symbol': 'STOCKS_US_LC',
        'annual_return': 0.10,
        'volatility': 0.15,
        'category': 'Equities'
    },
    'US Small Cap Stocks': {
        'symbol': 'STOCKS_US_SC',
        'annual_return': 0.11,
        'volatility': 0.20,
        'category': 'Equities'
    },
    'International Developed': {
        'symbol': 'STOCKS_INTL_DEV',
        'annual_return': 0.08,
        'volatility': 0.18,
        'category': 'Equities'
    },
    'Emerging Markets': {
        'symbol': 'STOCKS_EM',
        'annual_return': 0.10,
        'volatility': 0.25,
        'category': 'Equities'
    },
    'US Bonds (Aggregate)': {
        'symbol': 'BONDS_US_AGG',
        'annual_return': 0.04,
        'volatility': 0.05,
        'category': 'Fixed Income'
    },
    'High Yield Bonds': {
        'symbol': 'BONDS_HY',
        'annual_return': 0.06,
        'volatility': 0.10,
        'category': 'Fixed Income'
    },
    'Real Estate (REITs)': {
        'symbol': 'REITS',
        'annual_return': 0.09,
        'volatility': 0.16,
        'category': 'Alternatives'
    },
    'Commodities': {
        'symbol': 'COMMODITIES',
        'annual_return': 0.05,
        'volatility': 0.15,
        'category': 'Alternatives'
    },
    'Cash/Money Market': {
        'symbol': 'CASH',
        'annual_return': 0.04,
        'volatility': 0.01,
        'category': 'Fixed Income'
    }
}

# Correlation matrix (simplified 20-year historical)
# Rows/Cols: US_LC, US_SC, INTL_DEV, EM, AGG, HY, REITS, COMM, CASH
CORRELATION_MATRIX = [
    [1.00,  0.85,  0.82,  0.75,  -0.15, 0.10,  0.60,  0.20,  0.00],  # US LC
    [0.85,  1.00,  0.75,  0.80,  -0.10, 0.15,  0.65,  0.25,  0.00],  # US SC
    [0.82,  0.75,  1.00,  0.85,  -0.12, 0.08,  0.55,  0.15,  0.00],  # Intl Dev
    [0.75,  0.80,  0.85,  1.00,  -0.08, 0.20,  0.50,  0.30,  0.00],  # EM
    [-0.15, -0.10, -0.12, -0.08, 1.00,  0.65,  -0.05, -0.10, 0.10],  # Bonds
    [0.10,  0.15,  0.08,  0.20,  0.65,  1.00,  0.30,  0.10,  0.05],  # HY Bonds
    [0.60,  0.65,  0.55,  0.50,  -0.05, 0.30,  1.00,  0.40,  0.00],  # REITs
    [0.20,  0.25,  0.15,  0.30,  -0.10, 0.10,  0.40,  1.00,  0.00],  # Commodities
    [0.00,  0.00,  0.00,  0.00,  0.10,  0.05,  0.00,  0.00,  1.00]   # Cash
]

def get_asset_class(name):
    """Get asset class data by name."""
    return ASSET_CLASSES.get(name)

def get_all_asset_classes():
    """Get all available asset classes."""
    return ASSET_CLASSES

def get_correlation(asset1_idx, asset2_idx):
    """Get correlation between two assets by index."""
    if 0 <= asset1_idx < len(CORRELATION_MATRIX) and 0 <= asset2_idx < len(CORRELATION_MATRIX[asset1_idx]):
        return CORRELATION_MATRIX[asset1_idx][asset2_idx]
    return 0.0
