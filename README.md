# Raspberry Pi 5 OLED Stock Ticker

## Overview

This project displays stock ticker information (currently COF, SPY, QQQ) and the current time on a Waveshare 2.42-inch SPI OLED display module (SSD1309 driver).

It is specifically configured and tested for:
* **Hardware:** Raspberry Pi 5
* **Operating System:** Raspberry Pi OS Bookworm (32-bit)
* **Display:** Waveshare 2.42" OLED Display Module (128x64, SSD1309, SPI interface)

## Hardware Setup

### Components
* Raspberry Pi 5
* Waveshare 2.42" OLED Display Module (SSD1309 SPI version)
* Female-to-Female Jumper Wires

### Wiring (SPI Interface)
**Critical:** Ensure the connections are made exactly as follows, especially the CS pin.

| OLED Pin | Function     | Raspberry Pi Header Pin | Raspberry Pi GPIO | Notes                          |
| :------- | :----------- | :---------------------- | :---------------- | :----------------------------- |
| VCC      | Power        | Pin 1 (3.3V)            | -                 | Or Pin 17 (3.3V)               |
| GND      | Ground       | Pin 6 (GND)             | -                 | Or any other GND pin           |
| DIN      | Data In      | Pin 19 (SPI0 MOSI)      | GPIO 10           | Master Out -> Slave In         |
| CLK      | Clock        | Pin 23 (SPI0 SCLK)      | GPIO 11           | Serial Clock                   |
| **CS** | Chip Select  | **Pin 24 (SPI0 CE0)** | **GPIO 8** | **Crucial! Use this pin.** |
| DC       | Data/Command | Pin 31                  | GPIO 6            | Data/Command Select          |
| RST      | Reset        | Pin 29                  | GPIO 5            | Reset line                     |

### Enable SPI Interface
You need to enable the SPI hardware interface on your Raspberry Pi:
1.  Open a terminal.
2.  Run `sudo raspi-config`.
3.  Navigate to `Interface Options`.
4.  Select `SPI`.
5.  Choose `<Yes>` to enable the SPI interface.
6.  Select `<Ok>` and then `<Finish>`. Reboot if prompted.

## Software Setup

### Prerequisites
* Raspberry Pi 5 running Raspberry Pi OS Bookworm (32-bit recommended based on testing).
* Internet connection (for installing packages and fetching stock data).

### 1. Get the Code
* Ensure you have the project files (`stock_display.py`, `test_display.py`, `requirements.txt`) in a dedicated folder on your Raspberry Pi.

### 2. Install System Dependencies
* These libraries are needed for low-level hardware access on Bookworm. Open a terminal and run:
    ```bash
    sudo apt update
    sudo apt install gpiod libgpiod-dev python3-libgpiod python3-lgpio -y
    ```

### 3. Create Python Virtual Environment
* It's highly recommended to use a virtual environment. Navigate into your project folder in the terminal and run:
    ```bash
    python3 -m venv venv
    ```
    *This creates a folder named `venv` containing an isolated Python environment.*

### 4. Activate Virtual Environment
* Before installing Python packages or running the scripts, activate the environment:
    ```bash
    source venv/bin/activate
    ```
    *Your terminal prompt should now start with `(venv)`.*

### 5. Install Python Packages
* Install all the required Python libraries listed in `requirements.txt` (this includes `luma.oled`, `Pillow`, `yfinance`, `rpi-lgpio`, etc., and importantly **excludes** `RPi.GPIO`):
    ```bash
    pip install -r requirements.txt
    ```

## Running the Scripts

**Important:** Ensure your virtual environment is active (`source venv/bin/activate`) before running the scripts.

### 1. Test Display Script
* You can run a minimal test to ensure the display initializes and shows "Hello World":
    ```bash
    python3 test_display.py
    ```
    *(Assuming your minimal test script is named `test_display.py`)*

### 2. Run Stock Ticker Script
* To run the main application:
    ```bash
    python3 stock_display.py
    ```
* The script will fetch stock data and update the display every 60 seconds.
* Press `Ctrl + C` in the terminal to stop the script.

## Troubleshooting
* **No Display:** Double-check all wiring connections, especially **CS to Pin 24 (GPIO 8)**. Ensure SPI is enabled via `raspi-config`. Make sure the virtual environment is active.
* **Errors during `pip install`:** Check your internet connection and ensure system dependencies (Step 2) were installed correctly.
* **Errors running script:** Ensure the virtual environment is active. Check error messages for clues (e.g., network issues for `yfinance`, display initialization errors). Remember this setup specifically avoids the standard `RPi.GPIO` pip package due to incompatibility issues found during testing on RPi 5/Bookworm.

