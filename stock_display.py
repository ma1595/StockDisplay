# Stock Ticker Script - MODIFIED April 9, 2025
# Uses default CE0 (GPIO 8 / Pin 24) for Chip Select

import time
import yfinance as yf
from datetime import datetime
from luma.oled.device import ssd1309
from luma.core.interface.serial import spi
from luma.core.render import canvas

# SPI interface and pin setup
# *** MODIFIED LINE: Removed gpio_CS=26 parameter ***
# This assumes your CS wire is now connected to Pin 24 (GPIO 8)
serial = spi(port=0, device=0, gpio_DC=6, gpio_RST=5)

# Initialize the display using SSD1309 driver
print("Initializing display...") # Added a print statement for feedback
try:
    device = ssd1309(serial)
    print("Display initialized.")
except Exception as e:
    print(f"Error initializing display: {e}")
    print("Please check SPI is enabled, libraries are installed, and wiring is correct (CS->Pin 24).")
    exit() # Exit if display fails to initialize

# Function to fetch stock data and trend info
def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        # Use a longer history to increase chance of getting data if market just closed/opened
        hist = stock.history(period="2d")
        if hist.empty or len(hist) < 2:
             # If only one day, use previous close for comparison if available
             info = stock.info
             if 'previousClose' in info and 'currentPrice' in info:
                  price = info['currentPrice']
                  open_price = info['previousClose'] # Use previous close instead of open
             else: # Fallback if info isn't sufficient
                 return f"{ticker}: N/A"
        else:
            # Get the most recent close price and the previous close price
            price = hist['Close'].iloc[-1]
            open_price = hist['Close'].iloc[-2] # Previous day's close

        # Calculate percentage change based on previous close
        change_percent = ((price - open_price) / open_price) * 100
        return f"{ticker}: ${price:.2f} {change_percent:+.2f}%"
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return f"{ticker}: Error"


# Get the current formatted date and time (no seconds)
def get_current_datetime():
    # Using current time from context - April 9, 2025 at 11:21 PM EDT
    # Replace with datetime.now() for live time
    # now = datetime.now()
    # For demonstration, using the fixed context time
    now = datetime(2025, 4, 9, 23, 21, 46) # Approx context time EDT (needs timezone handling ideally)
    return now.strftime('%I:%M %p')  # 12-hour format with AM/PM

# Function to display the stock ticker and time
def display_stock_ticker():
    print("Updating display...") # Added print statement
    # Stock tickers to display
    tickers = ['COF', '^GSPC', 'QQQ']

    # Get stock data for each ticker
    stock_data = [get_stock_data(ticker) for ticker in tickers]

    # Get current date and time
    current_time = get_current_datetime()

    # Display the stock data and time
    try:
        with canvas(device) as draw:
            y_position = 0

            # Display the stock data
            for data in stock_data:
                # Use smaller default font if available with Luma
                # from luma.core.legacy import text
                # from luma.core.legacy.font import proportional, TINY_FONT
                # text(draw, (0, y_position), data, fill="white", font=proportional(TINY_FONT))
                # Default font:
                draw.text((0, y_position), data, fill="white")
                y_position += 10 # Adjust line spacing if needed

            # Display the current date and time near the bottom
            # Get text size if possible to position better (requires font object)
            # For now, position manually
            time_y_position = device.height - 10 # Adjust as needed
            draw.text((0, time_y_position), f"Time: {current_time}", fill="white")
        print("Display update complete.")
    except Exception as e:
        print(f"Error drawing on display: {e}")


# Run the stock ticker
print("Starting stock ticker loop...")
while True:
    display_stock_ticker()
    # Consider network issues; add delay even if fetch fails
    print(f"Sleeping for 60 seconds... (Time: {datetime.now()})") # Show actual time
    time.sleep(60)  # Update every minute

