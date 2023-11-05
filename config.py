# config.py

"""Configuration settings for cryptocurrency DCA script."""

# Trading configuration
MONTHLY_INVESTMENT_ALLOWANCE = 1000  # Amount in USD to invest monthly

# Cryptocurrency allocation details
CRYPTO_ALLOCATIONS = [
    ("LINK", "LINKUSD", 0.5),
    ("BTC", "XXBTZUSD", 0.25),
    ("ETH", "XETHZUSD", 0.25),
    # Add more as needed, check for market naming exceptions like in BTC and ETH above
]
