from flask import Flask, render_template, request, Response
import io
from smbus import SMBus
import time
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont
import RPi.GPIO as GPIO
import threading
import picamera

GPIO.setwarnings(False)

# Define global variables to track button states
button_states = {
    'forward': False,
    'backward': False,
    'left': False,
    'right': False
}

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

# Initialize I2C bus
bus = SMBus(1)

# Initialize the OLED display
display = Adafruit_SSD1306.SSD1306_128_64(rst=None)
display.begin()
display.clear()
display.display()


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


# Create a blank image with the same dimensions as the display
image = Image.new('1', (display.width, display.height))

# Load a font (you can change the font file and size as per your preference)
font = ImageFont.load_default()

# Create a draw object to draw on the image
draw = ImageDraw.Draw(image)

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
                
# Function to display text on the screen
def display_text(text):
    # Clear the image
    draw.rectangle((0, 0, display.width, display.height), outline=0, fill=0)

    # Calculate the width and height of the text
    text_width, text_height = draw.textsize(text, font=font)

    # Calculate the position to center the text on the screen
    x = (display.width - text_width) // 2
    y = (display.height - text_height) // 2

    # Draw the text on the image
    draw.text((x, y), text, font=font, fill=255)

    # Display the image on the screen
    display.image(image)
    display.display()


@app.route('/control', methods=['POST'])
def control():
    button = request.form.get('button')
    action = request.form.get('action')

    if button == 'stop':
        # Code to stop the motors
        stop_motors()
        return 'Motors stopped'

    speed=100
    
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




if __name__ == '__main__':
	camera = Camera()  # Create an instance of the Camera class
	camera.start_stream()  # Start the camera stream
	app.run(host='0.0.0.0', port=5000, threaded=True)
