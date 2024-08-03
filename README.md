# WALL-E Robot Project

## Description

WALL-E is a Raspberry Pi-based robot project that combines movement control, visual feedback, and voice interaction capabilities. The robot operates using two main programs:

1. A Flask-based server for movement control, LED screen display, and live camera feed.
2. A speech interaction program utilizing ChatGPT API for voice-activated responses.

## Features

- Remote control via web interface
- Live camera feed
- OLED display for visual feedback
- Voice activation and response using ChatGPT API
- Motor control for movement
- Servo control for additional movements

## Hardware Requirements

- Raspberry Pi 4 (4GB RAM)
- Adafruit SSD1306 1.3 inch OLED display
- L298N DC motor controller
- PCA9685 16-channel servo controller
- auvisio Omnidirectional 360° Condenser Conference Microphone (USB)
- 12V battery
- 12V to 5V step-down converter
- 3W speaker with 5V amplifier
- Raspberry Pi Camera Module
- Power bank (30000 mAh, 3A output capability) for Raspberry Pi

## Software Requirements

- Raspberry Pi OS (latest version recommended)
- Python 3.7+
- Flask
- OpenAI API key

## Installation

1. Clone the repository:
git clone https://github.com/redifo/walle.git
cd walle
2. Install required Python packages:
pip install -r requirements.txt
3. Enable I2C interfaces:
- Run `sudo raspi-config`
- Navigate to "Interfacing Options" > "I2C" and enable it
- For the second I2C interface (GPIO 0 and 1), add the following to `/boot/config.txt`:
  ```
  dtoverlay=i2c-gpio,bus=3,i2c_gpio_sda=0,i2c_gpio_scl=1
  ```

4. Set up environment variables:
Add the following to your `.bashrc` or `.env` file:
export CHATGPT_API_KEY="your_api_key_here"
5. Set up auto-start on boot:
- Create a service file: `sudo nano /etc/systemd/system/walle.service`
- Add the following content:
  ```
  [Unit]
  Description=WALL-E Robot Service
  After=network.target

  [Service]
  ExecStart=/usr/bin/python3 /path/to/your/main_script.py
  WorkingDirectory=/path/to/your/project
  StandardOutput=inherit
  StandardError=inherit
  Restart=always
  User=pi

  [Install]
  WantedBy=multi-user.target
  ```
- Enable the service:
  ```
  sudo systemctl enable walle.service
  sudo systemctl start walle.service
  ```

## Usage

1. Power on the robot and wait for it to boot up.
2. Connect to the robot's network or ensure it's on your local network.
3. Access the web interface by navigating to `http://<raspberry_pi_ip>:5000` in your web browser.
4. Use the on-screen controls to move the robot and adjust servo positions.
5. Speak the activation keyword to interact with the robot using voice commands.

## Configuration

- Motor control GPIO pins:
- ENA_PIN = 12
- ENB_PIN = 13
- IN1_PIN = 22
- IN2_PIN = 27
- IN3_PIN = 23
- IN4_PIN = 24

- Adjust these in the main Python script if your wiring differs.

## Troubleshooting

- If the robot doesn't respond to commands, check the log files at:
- `/home/walle/Desktop/repo/cron_script.log`
- `/home/walle/Desktop/repo/server_output.log`
- Ensure all connections are secure and the battery is charged.
- Verify that the ChatGPT API key is correctly set in the environment variables.

## Safety Precautions

- Always operate the robot in a safe, open area.
- Be cautious of moving parts when the robot is powered on.
- Disconnect the battery when making any hardware changes.
- Ensure proper ventilation to prevent overheating.

## Future Improvements

- Image recognition capabilities using ChatGPT.
- Facial recognition for identifying individuals.
- Location awareness using a library of known location photos.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions to the WALL-E Robot Project are welcome. Please feel free to submit pull requests or open issues to suggest improvements or add new features.