import io
import time
import threading
from picamera import PiCamera

class Camera:
    def __init__(self):
        self.camera = PiCamera()
        self.lock = threading.Semaphore(1)

    def start_stream(self):
        self.camera.resolution = (640, 480)
        self.camera.framerate = 16
        self.camera.start_recording('/dev/null', format='h264', splitter_port=2, resize=(640, 480))

    def generate_frames(self):
        while True:
            with self.lock:
                stream = io.BytesIO()
                self.camera.capture(stream, format='jpeg', use_video_port=True)
                stream.seek(0)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + stream.read() + b'\r\n\r\n')
                time.sleep(0.1)
