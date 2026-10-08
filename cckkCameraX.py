# import platform
import cv2

IS_RASPBERRY_PI = False

# Try importing Picamera2 (only works on Raspberry Pi)
try:
    from picamera2 import Picamera2
    IS_RASPBERRY_PI = True
except ImportError:
    IS_RASPBERRY_PI = False


class cckkCameraX:
    def __init__(self):
        self._frame_bgr = None
        if IS_RASPBERRY_PI:
            print("Initializing Picamera2 (Raspberry Pi)...")
            self.picam2 = Picamera2()
            config = self.picam2.create_preview_configuration(
                main={"size": (640, 480), "format": "RGB888"}
            )
            self.picam2.configure(config)
            self.picam2.start()

            # Enable continuous autofocus and auto white balance on Raspberry Pi
            self.picam2.set_controls({
                "AfMode": 2,  # Continuous Autofocus
                "AwbMode": 0  # Auto White Balance
            })
        else:
            print("Initializing OpenCV VideoCapture (Windows/Webcam)...")
            self.cap = cv2.VideoCapture(0)

    @property
    def frame_bgr(self) -> any:
        return self._frame_bgr

    @property
    def frame_rgb(self) -> any:
        return cv2.cvtColor(self.frame_bgr, cv2.COLOR_BGR2RGB)

    @property
    def shape(self) -> any:
        return self.frame_bgr.shape

    @property
    def width(self) -> int:
        h, w, _ = self.shape
        return w

    @property
    def height(self) -> int:
        h, w, _ = self.shape
        return h


    def read_frame(self, mirror: bool = True):
        """Returns a BGR frame ready for standard OpenCV rendering/processing."""
        if IS_RASPBERRY_PI:
            # On Pi, "RGB888" format in Picamera2 returns BGR-ordered array bytes directly
            frame_bgr = self.picam2.capture_array("main")
            if frame_bgr is None or frame_bgr.size == 0:
                return None
        else:
            ret, frame_bgr = self.cap.read()
            if not ret:
                return None

        if (mirror):
            frame_bgr = cv2.flip(frame_bgr, 1)

        self._frame_bgr = frame_bgr
        return frame_bgr

    def release(self):
        if IS_RASPBERRY_PI:
            self.picam2.stop()
        else:
            self.cap.release()
