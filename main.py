# main.py

"""Main module for cryptocurrency DCA script."""

import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import dotenv
import os

import krakenex
from pykrakenapi import KrakenAPI

from config import MONTHLY_INVESTMENT_ALLOWANCE, CRYPTO_ALLOCATIONS

# Kraken API credentials
API_KEY = os.environ.get('API_KEY')
API_SECRET = os.environ.get('API_SECRET')

# Use Gmail account with Google app password
EMAIL_RECIPIENT = os.environ.get('EMAIL_RECIPIENT')
EMAIL_SENDER = os.environ.get('EMAIL_SENDER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

# Initialize Kraken API client
kraken_api = krakenex.API(API_KEY, API_SECRET)
kraken_client = KrakenAPI(kraken_api)

# Constants for file paths
BALANCE_FILE = "balance.txt"
ALLOWANCE_FILE = "allowance.txt"
LOG_FILE = "trade_log.txt"

# Calculate the hourly allowance increment based on monthly allowance
HOURLY_ALLOWANCE_INCREMENT = MONTHLY_INVESTMENT_ALLOWANCE / (30 * 24)

# Initialize a dictionary to hold minimum trade sizes with default 0
MIN_TRADE_SIZES = {market: 0 for _, market, _ in CRYPTO_ALLOCATIONS}


# Function to read current balances and allowance from files
def read_balances_and_allowance():
    """Reads the balances and allowance from their respective files."""
    try:
        with open(BALANCE_FILE, "r") as f:
            lines = f.readlines()
            balances = {line.split(":")[0].strip(): float(line.split(":")[1].strip()) for line in lines}
        with open(ALLOWANCE_FILE, "r") as f:
            allowance = float(f.readline())
    except FileNotFoundError:
        # If files are not found, start with a balance of 0 for each crypto and allowance set to hourly increment
        balances = {crypto[0]: 0 for crypto in CRYPTO_ALLOCATIONS}
        allowance = HOURLY_ALLOWANCE_INCREMENT
        # Write the default balances to BALANCE_FILE
        with open(BALANCE_FILE, "w") as bf:
            for crypto, balance in balances.items():
                bf.write(f"{crypto}: {balance}\n")
        # Write the default allowance to ALLOWANCE_FILE
        with open(ALLOWANCE_FILE, "w") as af:
            af.write(str(allowance))
    return balances, allowance


# Function to write current balances and allowance to files
def write_balances_and_allowance(balances, allowance):
    """Writes the current balances and allowance to their respective files."""
    with open(BALANCE_FILE, "w") as f:
        for crypto, balance in balances.items():
            f.write(f"{crypto}: {balance}\n")
    with open(ALLOWANCE_FILE, "w") as f:
        f.write(str(allowance))


# Function to log trades with a timestamp
def log_trade(message):
    """Logs a trade message with a timestamp to the log file."""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{timestamp}: {message}\n")


# Function to send email notifications
def send_email(subject, body):
    """Sends an email with the given subject and body."""
    message = MIMEMultipart()
    message['From'] = EMAIL_SENDER
    message['To'] = EMAIL_RECIPIENT
    message['Subject'] = subject
    message.attach(MIMEText(body, 'html'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    server.send_message(message)
    server.quit()


# Function to get minimum order sizes from Kraken for all markets
def get_global_minimum_order_size():
    """Gets and sets the minimum order size for each market from the Kraken exchange."""
    tradable_asset_pairs = kraken_client.get_tradable_asset_pairs()
    global_min_order_size_usd = 0
    for _, market, _ in CRYPTO_ALLOCATIONS:
        min_order_size = float(tradable_asset_pairs.loc[market, 'ordermin'])
        price = float(kraken_client.get_ticker_information(market).loc[market, 'c'][0])
        min_order_size_usd = min_order_size * price
        MIN_TRADE_SIZES[market] = min_order_size
        global_min_order_size_usd = max(global_min_order_size_usd, min_order_size_usd)
    return global_min_order_size_usd


# Function to execute a trade on Kraken
def execute_trade(market, volume):
    """Executes a buy trade on the Kraken exchange for the given market and volume."""
    response = kraken_client.add_standard_order(pair=market,
                                                type='buy',
                                                ordertype='market',
                                                volume=str(volume),
                                                validate=False)
    return response


# Main function to execute the trading strategy
def main():
    """Main function to execute the trading strategy."""
    # Load current balances and allowance
    balances, current_allowance = read_balances_and_allowance()
    # Increment the allowance for the current hour
    current_allowance += HOURLY_ALLOWANCE_INCREMENT

    # Fetch the global minimum order size in USD
    global_min_order_size_usd = get_global_minimum_order_size()

    # Fetch current prices for each market
    prices = {}
    for _, market, _ in CRYPTO_ALLOCATIONS:
        ticker_info = kraken_client.get_ticker_information(market)
        prices[market] = float(ticker_info.loc[market, 'c'][0])

    # Calculate the total value of the portfolio
    total_portfolio_value = sum(balances[crypto] * prices[market] for crypto, market, _ in CRYPTO_ALLOCATIONS)

    # Trade logic: Buy zero balance coins first
    for crypto, market, alloc_percentage in CRYPTO_ALLOCATIONS:
        if balances[crypto] == 0 and current_allowance >= global_min_order_size_usd:
            volume = global_min_order_size_usd / prices[market]
            if volume < MIN_TRADE_SIZES[market]:
                volume = MIN_TRADE_SIZES[market]
            response = execute_trade(market, volume)

            # Check if the trade was successful
            if not response.get('error'):
                trade_cost = volume * prices[market]
                # Update allowance and balance
                current_allowance -= trade_cost
                balances[crypto] += volume
                # Log and notify the trade
                log_trade(f"Bought {volume} of {crypto} for a total of {trade_cost} USD")
                write_balances_and_allowance(balances, current_allowance)
                send_email(f"Trade Executed for {crypto}",
                           f"Bought {volume} of {crypto} at {prices[market]} USD for a total of {trade_cost} USD")
            else:
                log_trade(f"Trade error for {crypto}: {response['error']}")

            # Return early after handling a trade for a zero balance to prevent multiple trades in one execution
            return

    # Trade logic: Buy the most underrepresented coin
    underrepresented = []
    for crypto, market, alloc_percentage in CRYPTO_ALLOCATIONS:
        current_value = balances[crypto] * prices[market]
        current_percentage = current_value / total_portfolio_value if total_portfolio_value > 0 else 0
        if current_percentage < alloc_percentage:
            underrepresentation = alloc_percentage - current_percentage
            underrepresented.append((crypto, market, underrepresentation))

    # Sort coins by their degree of underrepresentation
    underrepresented.sort(key=lambda x: x[2], reverse=True)

    # Execute trade if any coin is significantly underrepresented
    if underrepresented and current_allowance >= global_min_order_size_usd:
        crypto_to_buy, market_to_buy, _ = underrepresented[0]
        price = prices[market_to_buy]
        volume = global_min_order_size_usd / price
        if volume < MIN_TRADE_SIZES[market_to_buy]:
            volume = MIN_TRADE_SIZES[market_to_buy]
        response = execute_trade(market_to_buy, volume)

        # Check if the trade was successful
        if not response.get('error'):
            trade_cost = volume * price
            # Update allowance and balance
            current_allowance -= trade_cost
            balances[crypto_to_buy] += volume
            # Log and notify the trade
            log_trade(f"Bought {volume} of {crypto_to_buy} for a total of {trade_cost} USD")
            send_email(f"Trade Executed for {crypto_to_buy}",
                       f"Bought {volume} of {crypto_to_buy} at {price} USD for a total of {trade_cost} USD")
        else:
            log_trade(f"Trade error for {crypto_to_buy}: {response['error']}")

    # Save the updated balances and allowance
    write_balances_and_allowance(balances, current_allowance)


# Entry point of the script
if __name__ == "__main__":
    main()
