# Kraken DCA Bot

Kraken DCA (Dollar Cost Averaging) Bot is an automated cryptocurrency trading bot that leverages the Kraken Exchange API to help users systematically invest in their chosen cryptocurrencies according to a predefined allocation strategy. This bot is designed to simplify the investment process, reduce the impact of volatility, and potentially lower the average cost of entry over time.

## Features

- **Automated Trading**: Set up your bot once, and it will trade automatically based on your investment schedule.
- **Dollar Cost Averaging**: Spread your investment over time to reduce the impact of volatility.
- **Email Notifications**: Receive email updates for every trade made, so you're always in the loop.
- **Custom Allocation**: Define your own asset allocation strategy for personalized portfolio management.
- **Security**: Uses environment variables and app passwords to keep your credentials secure.

## Getting Started

### Prerequisites

- Python 3.6+
- Kraken Exchange Account
- Gmail Account with App Password enabled
- A way to run the script hourly, such as Windows Task Scheduler or crontab

### Installation

1. Clone the repository to your local machine:
2. Navigate to the cloned repository directory:
3. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in the Kraken API credentials, Gmail credentials, and other configuration settings.

### Usage

1. Edit the `config.py` file to set your investment schedule, cryptocurrency allocations, and other preferences.
2. Run the following command every hour using some type of task scheduler:
   ```
   python main.py
   ```

## Disclaimer

This bot is provided as is, and it is meant to be used as a tool to assist with cryptocurrency trading. Cryptocurrency trading involves substantial risk of loss and is not suitable for every investor. The valuation of cryptocurrencies may fluctuate, and as a result, clients may lose more than their original investment.