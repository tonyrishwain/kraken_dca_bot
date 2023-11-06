# Kraken DCA Bot

## Features
- **Automated Buying**
- **Dollar Cost Averaging**
- **Email Notifications**
- **Custom Allocation**

### Prerequisites

- Python 3.6+
- Kraken Exchange Account
- Gmail Account with App Password enabled
- A way to run the script hourly, such as Windows Task Scheduler or crontab

### Installation

1. Clone the repository to your local machine.
2. Navigate to the cloned repository directory.
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
