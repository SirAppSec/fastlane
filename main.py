import requests
from bs4 import BeautifulSoup
import time
import schedule
import csv
from flask import Flask, render_template
import matplotlib.pyplot as plt
import os
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Set the backend to non-interactive
# File to store the scraped data
DATA_FILE = 'price_data.csv'

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
                price = price_span.text.strip()
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Save the price and timestamp to a CSV file
                with open(DATA_FILE, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([timestamp, price])

                print(f"Scraped price: {price} at {timestamp}")
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

# Function to create a chart from the scraped data
def create_chart():
    timestamps = []
    prices = []

    try:
        with open(DATA_FILE, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                timestamps.append(row[0])
                prices.append(float(row[1]))

        plt.figure(figsize=(10, 5))
        plt.plot(timestamps, prices, marker='o')
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.title('Price Over Time')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save the chart as an image
        chart_path = 'static/price_chart.png'
        plt.savefig(chart_path)
        plt.close()
    except FileNotFoundError:
        print("Data file not found. No chart generated.")
    except Exception as e:
        print(f"Error generating chart: {e}")

# Flask app to display the chart
app = Flask(__name__)

@app.route('/')
def index():
    create_chart()
    return render_template('index.html')

# Schedule the scraping task to run every 30 seconds
schedule.every(30).seconds.do(scrape_price)

if __name__ == '__main__':
    print(f"Current working directory: {os.getcwd()}")

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
