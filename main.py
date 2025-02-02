import requests
from bs4 import BeautifulSoup
import time
import schedule
import csv
from flask import Flask, render_template
import matplotlib
matplotlib.use('Agg')  # Set the backend to non-interactive
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from datetime import datetime

# File to store the scraped data
DATA_FILE = 'price_data.csv'

# Print the absolute path of the data file
print(f"Data file path: {os.path.abspath(DATA_FILE)}")
print(f"Current working directory: {os.getcwd()}")

# Function to scrape the price with error handling
def scrape_price():
    url = 'https://fastlane.co.il/'
    retries = 3  # Number of retries in case of failure
    delay = 5  # Delay between retries in seconds

    for attempt in range(retries):
        try:
            # Add a timeout to the request to avoid hanging
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise an exception for HTTP errors
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the span element with id="lblPrice"
            price_span = soup.find('span', id='lblPrice')

            if price_span:
                new_price = price_span.text.strip()
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Check if the CSV file exists and read the last recorded price
                last_price = None
                if os.path.exists(DATA_FILE):
                    with open(DATA_FILE, 'r') as file:
                        reader = csv.reader(file)
                        rows = list(reader)
                        if len(rows) > 1:  # Skip header row
                            last_price = rows[-1][1]  # Last recorded price

                # Only update the CSV file if the price has changed
                if last_price is None or new_price != last_price:
                    with open(DATA_FILE, 'a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([timestamp, new_price])
                    print(f"Scraped price: {new_price} at {timestamp} (Price changed)")
                else:
                    print(f"Scraped price: {new_price} at {timestamp} (No change)")
                break  # Exit the retry loop if successful
            else:
                print("Price element not found")
                break  # Exit the retry loop if the element is not found

        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay)  # Wait before retrying
            else:
                print("All retries failed. Skipping this scrape.")

# Function to create all charts
def create_charts():
    try:
        # Read the data from the CSV file
        df = pd.read_csv(DATA_FILE, parse_dates=['Timestamp'])
        df['Hour'] = df['Timestamp'].dt.hour
        df['DayOfWeek'] = df['Timestamp'].dt.day_name()
        df['TimeWindow15Min'] = df['Timestamp'].dt.floor('15T')  # 15-minute intervals
        df['TimeWindow1Hour'] = df['Timestamp'].dt.floor('1H')  # 1-hour intervals

        # Chart 1: Price Over Time
        plt.figure(figsize=(10, 5))
        if len(df) > 1:
            plt.plot(df['Timestamp'], df['Price'], marker='o', linestyle='-', label='Price Over Time')
        else:
            plt.plot(df['Timestamp'], df['Price'], marker='o', linestyle='none', label='Single Price Point')
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.title('Price Over Time')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.savefig('static/price_over_time.png')
        plt.close()

        # Chart 2: Price Distribution by Hour of the Day (Only if enough data)
        if len(df) > 1:
            plt.figure(figsize=(10, 5))
            plt.hist(df['Hour'], bins=24, edgecolor='black')
            plt.xlabel('Hour of the Day')
            plt.ylabel('Frequency')
            plt.title('Price Distribution by Hour of the Day')
            plt.xticks(range(24))
            plt.tight_layout()
            plt.savefig('static/price_distribution_by_hour.png')
            plt.close()

        # Chart 3: Average Price by Day of the Week (Only if enough data)
        if len(df) > 1:
            avg_price_by_day = df.groupby('DayOfWeek')['Price'].mean().reindex([
                'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
            ])
            plt.figure(figsize=(10, 5))
            avg_price_by_day.plot(kind='bar', edgecolor='black')
            plt.xlabel('Day of the Week')
            plt.ylabel('Average Price')
            plt.title('Average Price by Day of the Week')
            plt.tight_layout()
            plt.savefig('static/avg_price_by_day.png')
            plt.close()

        # Chart 4: Price Stability (Only if enough data)
        if len(df) > 1:
            price_changes = df.groupby('TimeWindow15Min')['Price'].std().fillna(0)
            plt.figure(figsize=(10, 5))
            plt.plot(price_changes.index, price_changes.values, marker='o', linestyle='-')
            plt.xlabel('Time')
            plt.ylabel('Price Standard Deviation (15-Minute Window)')
            plt.title('Price Stability Over Time')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('static/price_stability.png')
            plt.close()

        # Chart 5: Minimum Price by 15-Minute and Hourly Intervals (Only if enough data)
        if len(df) > 1:
            min_prices_15min = df.groupby('TimeWindow15Min')['Price'].min().reset_index()
            min_prices_1hour = df.groupby('TimeWindow1Hour')['Price'].min().reset_index()

            plt.figure(figsize=(14, 6))
            plt.plot(min_prices_15min['TimeWindow15Min'], min_prices_15min['Price'], marker='o', label='15-Minute Intervals')
            plt.plot(min_prices_1hour['TimeWindow1Hour'], min_prices_1hour['Price'], marker='x', label='1-Hour Intervals')
            plt.xlabel('Time')
            plt.ylabel('Minimum Price')
            plt.title('Minimum Price by 15-Minute and Hourly Intervals')
            plt.xticks(rotation=45)
            plt.legend()
            plt.tight_layout()
            plt.savefig('static/min_price_intervals.png')
            plt.close()

    except FileNotFoundError:
        print("Data file not found. No charts generated.")
    except Exception as e:
        print(f"Error generating charts: {e}")

# Flask app to display the charts
app = Flask(__name__)

@app.route('/')
def index():
    create_charts()
    chart_files = {
        'price_distribution_by_hour': 'price_distribution_by_hour.png',
        'avg_price_by_day': 'avg_price_by_day.png',
        'price_stability': 'price_stability.png',
        'min_price_intervals': 'min_price_intervals.png'
    }
    chart_exists = {f"{key}_exists": os.path.exists(f"static/{value}") for key, value in chart_files.items()}
    return render_template('index.html', **chart_exists)

# Schedule the scraping task to run every 30 seconds
schedule.every(30).seconds.do(scrape_price)

if __name__ == '__main__':
    # Create the data file if it doesn't exist
    if not os.path.exists(DATA_FILE):
        print(f"Creating data file: {DATA_FILE}")
        with open(DATA_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Price'])

    # Run the Flask app
    app.run(debug=True)

    # Keep the script running to execute scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(1)
