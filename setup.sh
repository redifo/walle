#!/bin/bash

# Update and upgrade the system
sudo apt update && sudo apt upgrade -y

# Install Python3, pip, and virtualenv
sudo apt install -y python3 python3-pip python3-venv

# Create a virtual environment
python3 -m venv my_project_env

# activate the v env
source /home/Desktop/repo/my_project_env/bin/activate

# Install necessary Python libraries
pip install RPi.GPIO picamera adafruit-circuitpython-servokit adafruit-circuitpython-pca9685 \
            Flask luma.lcd Pillow

# Install any additional system dependencies
sudo apt install -y python3-dev libopenjp2-7 libtiff5

# Enable I2C and SPI (if not already enabled)
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0

# Print a message indicating the setup is complete
echo "Setup complete. Don't forget to activate your virtual environment with 'source my_project_env/bin/activate'"

### Usage
### chmod +x setup.sh
### ./setup.sh
