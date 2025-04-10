# Stock Ticker Script - Updated April 10, 2025
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

# --- Configuration ---
STOCK_TICKERS = ['COF', '^GSPC', 'QQQ']
STOCK_UPDATE_INTERVAL_S = 60  # How often to fetch new stock data (in seconds)
ANIMATION_FRAME_INTERVAL_S = 0.2 # How often to update display/animation (if implemented)
# Set this to 1.0 if no animation for slower updates, but >= STOCK_UPDATE_INTERVAL_S makes no sense
DISPLAY_UPDATE_INTERVAL_S = 1.0 # Update display every second for time changes

# SPI interface and pin setup
# Assumes your CS wire is connected to Pin 24 (GPIO 8)
serial = spi(port=0, device=0, gpio_DC=6, gpio_RST=5)

# Initialize the display using SSD1309 driver
print("Initializing display...")
try:
    device = ssd1309(serial)
    print("Display initialized.")
except Exception as e:
    print(f"Error initializing display: {e}")
    print("Please check SPI is enabled, libraries (luma, pillow, rpi-lgpio) are installed,")
    print("and wiring is correct (CS->Pin 24, etc.). Ensure RPi.GPIO is uninstalled from venv.")
    exit() # Exit if display fails to initialize

# --- Global variables to store latest data ---
latest_stock_data = ["Loading..." for _ in STOCK_TICKERS] # Initial placeholder
latest_time_str = "--:-- --"
last_stock_fetch_time = 0

# Function to fetch stock data
def fetch_stock_updates():
    global latest_stock_data # Declare intent to modify global variable
    print("Fetching new stock data...")
    new_data = []
    for ticker in STOCK_TICKERS:
        try:
            stock = yf.Ticker(ticker)
            # Use info for potentially more real-time data + prev close fallback
            info = stock.info
            if 'currentPrice' in info and 'previousClose' in info:
                 price = info['currentPrice']
                 prev_close = info['previousClose']
                 change_percent = ((price - prev_close) / prev_close) * 100
                 new_data.append(f"{ticker}: ${price:.2f} {change_percent:+.2f}%")
            else: # Fallback using history if info fails
                 hist = stock.history(period="2d")
                 if not hist.empty and len(hist) >= 2:
                     price = hist['Close'].iloc[-1]
                     prev_close = hist['Close'].iloc[-2]
                     change_percent = ((price - prev_close) / prev_close) * 100
                     new_data.append(f"{ticker}: ${price:.2f} {change_percent:+.2f}%")
                 else:
                    new_data.append(f"{ticker}: N/A") # Data unavailable
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            new_data.append(f"{ticker}: Error")
    latest_stock_data = new_data
    print("Stock data updated.")

# Function to get the current formatted time string
def get_current_formatted_time():
    # *** THIS IS THE CRITICAL LINE FOR LIVE TIME ***
    # It uses the system time. Ensure Pi's timezone is correct!
    now = datetime.now()
    return now.strftime('%I:%M %p')  # 12-hour format with AM/PM

# Function to update and draw everything on the display
def update_display():
    global latest_time_str # Declare intent to modify global variable
    latest_time_str = get_current_formatted_time()

    try:
        with canvas(device) as draw:
            # Clear canvas implicitly handled by 'with canvas'
            y_position = 0
            # Draw stock data
            for data in latest_stock_data:
                # Consider using a smaller font if needed:
                # font = ImageFont.truetype("path/to/font.ttf", 8) # Example
                # draw.text((0, y_position), data, fill="white", font=font)
                draw.text((0, y_position), data, fill="white")
                y_position += 10 # Adjust line spacing if needed

            # --- Area for potential animation ---
            # y_position += 6 # Gap before time
            # draw_animation_frame(draw, y_position) # Call your animation func here

            # Draw time near the bottom
            time_y_position = device.height - 10 # Adjust as needed
            draw.text((0, time_y_position), f"Time: {latest_time_str}", fill="white")

    except Exception as e:
        print(f"Error drawing on display: {e}")

# --- Main Loop ---
print("Starting display loop...")
while True:
    current_loop_time = time.time()

    # --- Check if it's time to fetch stock data ---
    if current_loop_time - last_stock_fetch_time >= STOCK_UPDATE_INTERVAL_S:
        fetch_stock_updates()
        last_stock_fetch_time = current_loop_time

    # --- Update and redraw the display ---
    update_display()
    print(f"Display updated. Current time on Pi: {datetime.now()}") # Log current system time

    # --- Sleep until next display update ---
    # Adjust sleep time based on how long updates took, if needed for accuracy
    time.sleep(DISPLAY_UPDATE_INTERVAL_S)


