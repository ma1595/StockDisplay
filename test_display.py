# Save this as minimal_luma_test_gpio8.py
import time
import traceback # To print detailed errors

# Luma libraries for SSD1309 display via SPI
from luma.oled.device import ssd1309
from luma.core.interface.serial import spi
from luma.core.render import canvas

# --- Pin Configuration ---
SPI_PORT = 0
SPI_DEVICE = 0 # Using default CE0 (Chip Enable 0) which is GPIO 8 / Pin 24
GPIO_DC = 6    # Data/Command pin (GPIO 6 / Pin 31)
GPIO_RST = 5   # Reset pin (GPIO 5 / Pin 29)
# We are NOT specifying gpio_CS, so the system uses device=0 (CE0)
# -------------------------------------------------------

print("--- Starting Minimal Luma OLED Test (SSD1309 - Using GPIO 8/CE0 for CS) ---")
print(f"Target Platform: Raspberry Pi 5 / Bookworm OS")
print("Attempting to use SPI settings:")
print(f"  SPI Port: {SPI_PORT}")
print(f"  SPI Device: {SPI_DEVICE} (Uses kernel CE0 / GPIO 8)") # Updated comment
print(f"  GPIO DC: {GPIO_DC}")
print(f"  GPIO RST: {GPIO_RST}")
print("  GPIO CS: Using system CE0 (GPIO 8 / Pin 24) - Not specified in code") # Updated comment
print("Expected Wiring: RST->GPIO5(Pin29), DC->GPIO6(Pin31), CS->GPIO8(Pin24), MOSI->GPIO10(Pin19), SCLK->GPIO11(Pin23)") # Updated wiring expectation
print("-" * 40)

try:
    # 1. Initialize SPI Interface
    print("Step 1: Initializing SPI interface (using device=0 for CS)...")
    # *** MODIFIED LINE: Removed gpio_CS parameter ***
    serial = spi(port=SPI_PORT,
                 device=SPI_DEVICE,
                 gpio_DC=GPIO_DC,
                 gpio_RST=GPIO_RST)
    print("Step 1: SPI interface initialized successfully.")
    print("-" * 40)

    # 2. Initialize SSD1309 Device
    print("Step 2: Initializing SSD1309 device...")
    device = ssd1309(serial)
    print("Step 2: SSD1309 device initialized successfully.")
    print("-" * 40)

    # 3. Clear Display
    print("Step 3: Clearing display...")
    device.clear()
    device.clear()
    print("Step 3: Display cleared.")
    print("-" * 40)

    # 4. Draw "Hello World"
    print("Step 4: Drawing 'Hello World' text...")
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((10, 20), "Hello World", fill="white")
    print("Step 4: Drawing complete.")
    print("-" * 40)

    print("\nSUCCESS! The screen should be displaying 'Hello World'.")
    print("The script will keep the message displayed for 30 seconds.")
    time.sleep(30)

except Exception as e:
    print("\n!!!!!!!! AN ERROR OCCURRED !!!!!!!!")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Details: {e}")
    print("-" * 40)
    print("Detailed Traceback:")
    traceback.print_exc() # Print the full error stack trace
    print("-" * 40)
    print("Please double-check wiring (CS MUST be on Pin 24/GPIO 8).")
    print("Ensure SPI is enabled (`sudo raspi-config`).")
    print("Check library installations (luma.oled, luma.core, Pillow, libgpiod).")

finally:
    print("\n--- Minimal Luma OLED Test Finished ---")

