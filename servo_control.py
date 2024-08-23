from adafruit_servokit import ServoKit

class ServoController:
    def __init__(self):
        self.pca = ServoKit(channels=16)
        self.curpos = [248, 560, 140, 475, 270, 250, 290]

    def control_servos(self, slider, value):
        slider_map = {
            'head-slider': 0,
            'neck-slider': 1,
            'left-eye-slider': 2,
            'right-eye-slider': 3,
            'left-arm-slider': 4,
            'right-arm-slider': 5,
        }

        if slider in slider_map:
            channel = slider_map[slider]
            if 0 <= value <= 180:
                self.pca.servo[channel].angle = value
                self.curpos[channel] = value
