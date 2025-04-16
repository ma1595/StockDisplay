# Stock Ticker Script - Updated April 10, 2025
# Includes ZenQuote integration via API (https://zenquotes.io/api/random) with scrolling
# Uses default CE0 (GPIO 8 / Pin 24) for Chip Select
# Ensure system timezone is set correctly (e.g., sudo timedatectl set-timezone America/New_York)

import time
import yfinance as yf
from datetime import datetime
from luma.oled.device import ssd1309
from luma.core.interface.serial import spi
from luma.core.render import canvas
# Assuming Pillow is installed (dependency for Luma's canvas/text often)
# from PIL import ImageFont # Example if using custom fonts
import requests # <-- Added for direct API calls
import random

# --- Configuration ---
STOCK_TICKERS = ['COF', '^GSPC', 'AAPL']
STOCK_UPDATE_INTERVAL_S = 60  # How often to fetch new stock data (in seconds)
QUOTE_UPDATE_INTERVAL_S = 300  # How often to fetch a new quote (in seconds) - Set to 60 for once a minute
ANIMATION_FRAME_INTERVAL_S = 0.05 # How often to update display/animation (smaller = smoother scroll)

# --- Scrolling Configuration ---
SCROLL_SPEED_PIXELS = 1     # How many pixels to shift the quote per frame
SCROLL_PADDING = "    "     # Space added to end of quote for smoother looping

# --- API Configuration ---
ZENQUOTES_API_URL = "https://zenquotes.io/api/random"
REQUEST_TIMEOUT_S = 10      # How long to wait for API response

# SPI interface and pin setup
# Assumes your CS wire is connected to Pin 24 (GPIO 8)
serial = spi(port=0, device=0, gpio_DC=6, gpio_RST=5)

# Initialize the display using SSD1309 driver
print("Initializing display...")
try:
    device = ssd1309(serial)
    print(f"Display initialized ({device.width}x{device.height}).")
except Exception as e:
    print(f"Error initializing display: {e}")
    print("Please check SPI is enabled, libraries (luma, pillow, rpi-lgpio, requests) are installed,") # Added requests here
    print("and wiring is correct (CS->Pin 24, etc.). Ensure RPi.GPIO is uninstalled from venv if using lgpio.")
    exit() # Exit if display fails to initialize

# --- Global variables to store latest data ---
latest_stock_data = ["Loading..." for _ in STOCK_TICKERS] # Initial placeholder
latest_quote_str = "Loading quote..." # Initial placeholder for quote
latest_time_str = "--:-- --"
last_stock_fetch_time = 0
last_quote_fetch_time = 0
quote_scroll_offset = 0 # Tracks the horizontal scroll position for the quote

# Function to fetch stock data
def fetch_stock_updates():
    global latest_stock_data
    print("Fetching new stock data...")
    new_data = []
    for ticker in STOCK_TICKERS:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            price = info.get('regularMarketPrice') or info.get('currentPrice')
            prev_close = info.get('previousClose')

            if price is not None and prev_close is not None:
                 change_percent = ((price - prev_close) / prev_close) * 100
                 new_data.append(f"{ticker}: ${price:.2f} {change_percent:+.2f}%")
            else:
                 hist = stock.history(period="2d")
                 if not hist.empty and len(hist) >= 2:
                     price = hist['Close'].iloc[-1]
                     prev_close = hist['Close'].iloc[-2]
                     change_percent = ((price - prev_close) / prev_close) * 100
                     new_data.append(f"{ticker}: ${price:.2f} {change_percent:+.2f}%")
                 else:
                    new_data.append(f"{ticker}: N/A")
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            new_data.append(f"{ticker}: Error")
    latest_stock_data = new_data
    print("Stock data updated.")

# Function to fetch a new Zen quote using the API directly
def fetch_zen_quote():
    global latest_quote_str, quote_scroll_offset
    print(f"Fetching new quote from {ZENQUOTES_API_URL}...")
    try:
        response = requests.get(ZENQUOTES_API_URL, timeout=REQUEST_TIMEOUT_S)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        data = response.json()
        if data and isinstance(data, list) and len(data) > 0:
            quote_data = data[0]
            quote = quote_data.get('q', 'Quote unavailable.')
            author = quote_data.get('a', 'Unknown')
            latest_quote_str = f'"{quote}" - {author}'
            quote_scroll_offset = 0 # Reset scroll position when new quote arrives
            print("Quote updated via API.")
        else:
            print("Error: Invalid data format received from ZenQuotes API.")
            latest_quote_str = "Invalid API response."
            quote_scroll_offset = 0

    except requests.exceptions.Timeout:
        print(f"Error fetching quote: Request timed out after {REQUEST_TIMEOUT_S} seconds.")
        latest_quote_str = "Quote API timeout."
        # Keep old quote scrolling? Or reset? Resetting offset for consistency.
        quote_scroll_offset = 0
    except requests.exceptions.RequestException as e:
        print(f"Error fetching quote via API: {e}")
        latest_quote_str = "Quote API error."
        quote_scroll_offset = 0
    except Exception as e:
        # Catch other potential errors (e.g., JSON decoding if API returns non-JSON)
        print(f"An unexpected error occurred processing the quote: {e}")
        latest_quote_str = "Quote processing error."
        quote_scroll_offset = 0


# Function to get the current formatted time string
def get_current_formatted_time():
    now = datetime.now()
    # Using EDT/EST based on current time/location context
    # If running elsewhere, ensure Pi's timezone is correct
    return now.strftime('%I:%M:%S %p %Z') # 12-hour format with seconds, AM/PM, Timezone

# Function to update and draw everything on the display
def update_display():
    global latest_time_str, quote_scroll_offset

    latest_time_str = get_current_formatted_time()

    try:
        with canvas(device) as draw:
            y_position = 0
            line_height = 10

            # --- Draw stock data ---
            for data in latest_stock_data:
                draw.text((0, y_position), data, fill="white")
                y_position += line_height

            # --- Draw Zen Quote (with scrolling) ---
            quote_y_position = device.height - (2 * line_height)

            full_quote_with_padding = latest_quote_str + SCROLL_PADDING
            text_width = draw.textlength(full_quote_with_padding)

            if text_width <= device.width:
                draw.text((0, quote_y_position), latest_quote_str, fill="white")
                quote_scroll_offset = 0
            else:
                draw_x = -quote_scroll_offset
                draw.text((draw_x, quote_y_position), full_quote_with_padding, fill="white")
                quote_scroll_offset += SCROLL_SPEED_PIXELS
                if quote_scroll_offset >= text_width:
                    quote_scroll_offset = 0

            # --- Draw Time ---
            time_y_position = device.height - line_height
            draw.text((0, time_y_position), latest_time_str, fill="white")

    except Exception as e:
        print(f"Error drawing on display: {e}")

# --- Initial Data Fetch ---
print("Performing initial data fetch...")
fetch_stock_updates()
fetch_zen_quote() # Fetch initial quote using the API method
last_stock_fetch_time = time.time()
last_quote_fetch_time = time.time()

# --- Main Loop ---
print("Starting display loop...")
while True:
    current_loop_time = time.time()

    # --- Check if it's time to fetch NEW stock data ---
    if current_loop_time - last_stock_fetch_time >= STOCK_UPDATE_INTERVAL_S:
        fetch_stock_updates()
        last_stock_fetch_time = current_loop_time

    # --- Check if it's time to fetch a NEW quote ---
    if current_loop_time - last_quote_fetch_time >= QUOTE_UPDATE_INTERVAL_S:
        fetch_zen_quote()
        # Update time marker regardless of fetch success/failure to ensure it tries again in 1 min
        last_quote_fetch_time = current_loop_time

    # --- Update and redraw the display (handles animation/scrolling) ---
    update_display()

    # --- Sleep until next animation frame ---
    time.sleep(ANIMATION_FRAME_INTERVAL_S)

