from flask import Flask, render_template, request, Response
import io
import time
import RPi.GPIO as GPIO
import threading
import picamera
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio
import adafruit_st7789 as ST7789  
from PIL import Image, ImageDraw, ImageFont


font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)  # Tripled from default size 12

# Suppress GPIO warnings
GPIO.setwarnings(False)

# I2C setup for GPIO 2 and 3 (default I2C bus 1)
I2C_BUS = 1
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x40)
pca.frequency = 50  # Set PWM frequency to 50Hz

# Constants
nbPCAServo = 7  # Number of servos being controlled 

# Initialize PCA9685 (16-channel PWM driver)
pca = ServoKit(channels=16)

# Servo Control Parameters
curpos = [248, 560, 140, 475, 270, 250, 290]  # Current position (units)
setpos = [248, 560, 140, 475, 270, 250, 290]  # Required position (units)
curvel = [0, 0, 0, 0, 0, 0, 0]  # Current velocity (units/sec)
maxvel = [500, 400, 500, 2400, 2400, 600, 600]  # Max Servo velocity (units/sec)
accell = [350, 300, 480, 1800, 1800, 500, 500]  # Servo acceleration (units/sec^2)

# Function to initialize servos
def init_servos():
    for i in range(nbPCAServo):
        pca.servo[i].set_pulse_width_range(500, 2500)  # Set pulse width range for all servos

# Function to control servos based on position values from the web interface
def control_servos(positions):
    for i in range(nbPCAServo):
        required_position = positions[i]
        
        if 0 <= required_position <= 180:  # Ensure the value is within the valid range
            # Control the servo to move to the required position
            pca.servo[i].angle = required_position
            time.sleep(0.01)  # Adjust sleep time for smoother movement
            
            # Update the current position after movement
            curpos[i] = required_position

# Define motor control GPIO pins
ENA_PIN = 12  # Enable pin for Motor A
ENB_PIN = 13  # Enable pin for Motor B
IN1_PIN = 22  # Input 1 pin for Motor A
IN2_PIN = 27  # Input 2 pin for Motor A
IN3_PIN = 23  # Input 1 pin for Motor B
IN4_PIN = 24  # Input 2 pin for Motor B

# Set the mode of the GPIO pins
GPIO.setmode(GPIO.BCM)

# Set the GPIO pins as outputs
GPIO.setup(ENA_PIN, GPIO.OUT)
GPIO.setup(ENB_PIN, GPIO.OUT)
GPIO.setup(IN1_PIN, GPIO.OUT)
GPIO.setup(IN2_PIN, GPIO.OUT)
GPIO.setup(IN3_PIN, GPIO.OUT)
GPIO.setup(IN4_PIN, GPIO.OUT)

# Create PWM objects for controlling the motor speed
pwm_a = GPIO.PWM(ENA_PIN, 100)  # PWM frequency is set to 100 Hz
pwm_b = GPIO.PWM(ENB_PIN, 100)  # PWM frequency is set to 100 Hz

app = Flask(__name__, template_folder='templates')

# Initialize the ST7789 display (SPI)
RST_PIN = 25  # Reset pin for ST7789
DC_PIN = 8  # Data/Command pin for ST7789
SPI_PORT = 0  # SPI port (0 for /dev/spidev0.0)
SPI_DEVICE = 0  # SPI device (0 for /dev/spidev0.0)
spi_speed_hz = 40000000  # 40MHz SPI speed

disp = ST7789.ST7789(
    SPI_PORT,
    SPI_DEVICE,
    rst=RST_PIN,
    dc=DC_PIN,
    spi_speed_hz=spi_speed_hz
)

disp.begin()

def control_motors(left_speed, right_speed):
    # Convert the speed values (-100 to 100) to a PWM duty cycle (0 to 100)
    duty_a = abs(left_speed)
    duty_b = abs(right_speed)

    # Set the direction of the motors based on the speed values
    if left_speed >= 0:
        GPIO.output(IN1_PIN, GPIO.HIGH)
        GPIO.output(IN2_PIN, GPIO.LOW)
    else:
        GPIO.output(IN1_PIN, GPIO.LOW)
        GPIO.output(IN2_PIN, GPIO.HIGH)

    if right_speed >= 0:
        GPIO.output(IN3_PIN, GPIO.HIGH)
        GPIO.output(IN4_PIN, GPIO.LOW)
    else:
        GPIO.output(IN3_PIN, GPIO.LOW)
        GPIO.output(IN4_PIN, GPIO.HIGH)

    # Start the PWM with the corresponding duty cycle
    pwm_a.start(duty_a)
    pwm_b.start(duty_b)

def stop_motors():
    # Stop the PWM
    pwm_a.stop()
    pwm_b.stop()

# Route for the index page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(camera.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

class Camera:
    def __init__(self):
        self.camera = picamera.PiCamera()
        self.lock = threading.Semaphore(1)  # Limit concurrent connections to 1

    def start_stream(self):
        # Set camera resolution and other settings
        self.camera.resolution = (640, 480)
        self.camera.framerate = 16
        # Enable hardware acceleration
        self.camera.start_recording(
            '/dev/null', format='h264', splitter_port=2, resize=(640, 480))

    def generate_frames(self):
        # Continuously capture frames from the camera
        while True:
            with self.lock:
                # Create a temporary in-memory stream
                stream = io.BytesIO()
                
                # Capture a frame and save it to the stream
                self.camera.capture(stream, format='jpeg', use_video_port=True)
                
                # Reset the stream for reading
                stream.seek(0)
                
                # Yield the frame as a multipart response
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + stream.read() + b'\r\n\r\n')
                
                # Wait for a short time before capturing the next frame
                time.sleep(0.1)

# Function to display text on the ST7789 screen
def display_text(text):
    # Create a blank image with the same dimensions as the display
    width, height = disp.width, disp.height
    image = Image.new('RGB', (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Calculate the width and height of the text
    text_width, text_height = draw.textsize(text, font=font)

    # Calculate the position to center the text on the screen
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Draw the text on the image
    draw.text((x, y), text, font=font, fill=(255, 255, 255))

    # Display the image on the screen
    disp.display(image)

@app.route('/control', methods=['POST'])
def control_servos_endpoint():
    # Mapping of slider names to servo indices
    slider_map = {
        'head-slider': 0,
        'neck-slider': 1,
        'left-eye-slider': 2,
        'right-eye-slider': 3,
        'left-arm-slider': 4,
        'right-arm-slider': 5,
    }
    
    # Retrieve the slider name and value from the request
    slider = request.form.get('slider')
    value = request.form.get('value', type=int)
    
    # Determine the servo channel from the slider name
    if slider in slider_map:
        channel = slider_map[slider]
        control_servos([value if i == channel else curpos[i] for i in range(nbPCAServo)])

    return 'Servos controlled successfully!'
    
def control():
    speed = 100
    button = request.form.get('button')
    action = request.form.get('action')

    if button == 'stop':
        # Code to stop the motors
        stop_motors()
        return 'Motors stopped'

    if button == 'forward':
        if action == 'press':
            control_motors(speed, speed)
        elif action == 'release':
            stop_motors()
    elif button == 'backward':
        if action == 'press':
            control_motors(-speed, -speed)
        elif action == 'release':
            stop_motors()
    elif button == 'left':
        if action == 'press':
            control_motors(-speed, speed)
        elif action == 'release':
            stop_motors()
    elif button == 'right':
        if action == 'press':
            control_motors(speed, -speed)
        elif action == 'release':
            stop_motors()

    return 'OK'

@app.route('/text', methods=['POST'])
def handle_text():
    text = request.form['text']
    # Handle the text input
    display_text(text)
    return 'OK'

if __name__ == '__main__':
    init_servos()
    camera = Camera()  # Create an instance of the Camera class
    camera.start_stream()  # Start the camera stream
    app.run(host='0.0.0.0', port=5000, threaded=True)
