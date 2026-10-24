import cv2
import numpy as np

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
        self._overlay_text = None  # Overlay with text so don't mirror
        self._overlay_img = None  # Overlay of the image and so mirror with image

        if IS_RASPBERRY_PI:
            print("Initializing Picamera2 (Raspberry Pi)...")
            self.picam2 = Picamera2()
            config = self.picam2.create_preview_configuration(
                main={"size": (640, 480), "format": "RGB888"}
            )
            self.picam2.configure(config)
            self.picam2.start()

            # Enable continuous autofocus and auto white balance on Raspberry Pi
            self.picam2.set_controls(
                {
                    "AfMode": 2,  # Continuous Autofocus
                    "AwbMode": 0,  # Auto White Balance
                }
            )
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

    def read_frame(self, mirror: bool = False):
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

        if mirror:
            frame_bgr = cv2.flip(frame_bgr, 1)

        self._frame_bgr = frame_bgr
        return frame_bgr

    def mirror(self) -> "cckkCameraX":
        self._frame_bgr = cv2.flip(self.frame_bgr, 1)
        return self

    def frame(self, mirror: bool = False, bgr: bool = True):
        if bgr:
            if mirror:
                return cv2.flip(self.frame_bgr, 1)
            else:
                return self.frame_bgr
        else:
            if mirror:
                return cv2.flip(self.frame_rgb, 1)
            else:
                return self.frame_rgb

    def release(self):
        if IS_RASPBERRY_PI:
            self.picam2.stop()
        else:
            self.cap.release()

    def clear_overlays(self) -> "cckkCameraX":
        self._overlay_text = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        self._overlay_img = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        return self 

    def putText(
        self,
        text: str,
        origin,
        color,
        fontFace: int = cv2.FONT_HERSHEY_SIMPLEX,
        fontScale: float = 1.0,
        thickness: int = 1,
        lineType: int = cv2.LINE_AA,
        bottomLeftOrigin: bool = False,
    ):
        cv2.putText(
            self._overlay_text,
            text,
            origin,
            fontFace,
            fontScale,
            color,
            thickness,
            lineType,
            bottomLeftOrigin
        )


    def create_overlay(self) -> np.ndarray:
        return np.zeros((self.height, self.width, 4), dtype=np.uint8)

    def frame_overlays(self, overlays_with_flags: list[tuple[np.ndarray, bool]], mirror:bool = True) -> np.ndarray:
        """Returns a BGR frame with multiple RGBA overlays applied, each with its own mirror flag."""
        frame_bgr = self.frame_bgr.copy()
        if mirror:
            frame_bgr = cv2.flip(frame_bgr, 1)

        if (self._overlay_text is not None):
            frame_bgr = self.add_overlay(False, frame_bgr, self._overlay_text)


        for overlay, mirror in overlays_with_flags:
            frame_bgr = self.add_overlay(mirror, frame_bgr, overlay)

        return frame_bgr

    def add_overlay(self, mirror, frame_bgr, overlay):
        if overlay.ndim != 3 or overlay.shape[2] != 4:
            raise ValueError("Each overlay must be a 4-channel (RGBA) NumPy array.")

            # Apply individual mirror flag if specified for this overlay
        current_overlay = overlay
        if mirror:
            current_overlay = cv2.flip(overlay, 1)

            # Split color channels and alpha channel, normalize alpha to 0.0 - 1.0
        overlay_rgb = current_overlay[:, :, :3]
        alpha = current_overlay[:, :, 3] / 255.0
        alpha_3ch = np.dstack([alpha, alpha, alpha])

            # Perform alpha blending for this layer
        frame_bgr = (overlay_rgb * alpha_3ch + frame_bgr * (1.0 - alpha_3ch)).astype(np.uint8)
        return frame_bgr
