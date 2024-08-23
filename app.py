from flask import Flask, render_template, request
from camera import Camera
from servo_control import ServoController
from motor_control import MotorController
from display import DisplayManager

app = Flask(__name__)

# Initialize components
camera = Camera()
servo_controller = ServoController()
motor_controller = MotorController()
display_manager = DisplayManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/control_servos', methods=['POST'])
def control_servos():
    slider = request.form.get('slider')
    value = request.form.get('value', type=int)
    servo_controller.control_servos(slider, value)
    return 'Servos controlled successfully!'

@app.route('/control_motors', methods=['POST'])
def control_motors():
    button = request.form.get('button')
    action = request.form.get('action')
    motor_controller.control(button, action)
    return 'OK'

@app.route('/display_text', methods=['POST'])
def display_text():
    text = request.form['text']
    display_manager.display_text(text)
    return 'OK'

@app.route('/video_feed')
def video_feed():
    return Response(camera.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
