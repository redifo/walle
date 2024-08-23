import RPi.GPIO as GPIO
import time

class MotorController:
    def __init__(self):
        self.ENA_PIN = 12
        self.ENB_PIN = 13
        self.IN1_PIN = 22
        self.IN2_PIN = 27
        self.IN3_PIN = 23
        self.IN4_PIN = 24

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.ENA_PIN, GPIO.OUT)
        GPIO.setup(self.ENB_PIN, GPIO.OUT)
        GPIO.setup(self.IN1_PIN, GPIO.OUT)
        GPIO.setup(self.IN2_PIN, GPIO.OUT)
        GPIO.setup(self.IN3_PIN, GPIO.OUT)
        GPIO.setup(self.IN4_PIN, GPIO.OUT)

        self.pwm_a = GPIO.PWM(self.ENA_PIN, 100)
        self.pwm_b = GPIO.PWM(self.ENB_PIN, 100)

    def control(self, button, action):
        speed = 100
        if button == 'stop':
            self.stop_motors()
        elif button == 'forward':
            self.control_motors(speed, speed, action)
        elif button == 'backward':
            self.control_motors(-speed, -speed, action)
        elif button == 'left':
            self.control_motors(-speed, speed, action)
        elif button == 'right':
            self.control_motors(speed, -speed, action)

    def control_motors(self, left_speed, right_speed, action):
        if action == 'press':
            self.pwm_a.start(abs(left_speed))
            self.pwm_b.start(abs(right_speed))
        elif action == 'release':
            self.stop_motors()

    def stop_motors(self):
        self.pwm_a.stop()
        self.pwm_b.stop()
