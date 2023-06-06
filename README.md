# NavyWeatherTeleBot

This project is a Python-based Telegram Bot that uses web scraping techniques to gather weather information and promulgates it to a channel chat on Telegram.

## Features

- Web Scraping: The bot navigates through a weather forecast website, logging in and scraping specific data points.
- Data Processing: The scraped data is processed into a readable format, and some of it is stored into Excel files.
- Telegram Integration: The bot then sends the processed data and Excel files to a specified chat on Telegram.

## Setup and Running

### Prerequisites

- Python 3.x
- Google Chrome Browser installed

### Installation

1. Clone this repository.
2. Install the required Python packages by running `pip install -r requirements.txt` in the project directory.

### Environment Variables

You need to set the following environment variables for the bot to function correctly.

- `BOT_TOKEN`: Your Telegram Bot token.
- `USER`: Your username for the weather website.
- `PW`: Your password for the weather website.
- `CHAT_ID`: The ID of the Telegram chat where the bot will send the data.

## GitHub Actions

This bot is configured to run on GitHub Actions. To run the bot using GitHub Actions, you need to:

1. Fork this repository.
2. Set your environment variables in the repository's secrets settings.

The bot is scheduled to run daily at a specified time. Modify the cron schedule in the `.github/workflows/main.yml` file to change this.

## Limitations and Future Work

The current version of the bot is fully functional but has a few limitations:

- It is limited to the specific weather forecast website it was designed to scrape.
- It does not handle errors or unexpected website changes gracefully.

Future versions will aim to address these issues and add new features.
