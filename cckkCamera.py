cckkCamera_ok = True
try:
    from picamzero import Camera
except ImportError:
    cckkCamera_ok = False

import cckkCV
from logzero import logger
from os.path import join

if not cckkCamera_ok:
    logger.warning("cckkCamera: picamzero module not found. Camera functionality will be disabled.")

__version__ = "1.0.0"

class cckkCameraORB(cckkCV.cckkORB):
    _next_id = 1
    _base_filename = "image"
    _base_path = "./camera"
    _camera = None

    def available():
        return cckkCamera_ok

    def _generate_filename():
        filename = f"{cckkCameraORB._base_filename}_{cckkCameraORB._next_id:04d}.jpg"
        cckkCameraORB._next_id += 1
        return filename
    
    def __init__(self, auto_detect=True):
        if not cckkCamera_ok:
            raise ImportError("cckkCamera: picamzero module not found. Cannot use cckkCameraORB.")

        if cckkCameraORB._camera is None:
            cckkCameraORB._camera = Camera()

        self._img_filename = cckkCameraORB._generate_filename()
        img_path = join(cckkCameraORB._base_path, self._img_filename)
        cckkCameraORB._camera.take_photo(img_path)
        super().__init__(img_filename=self._img_filename, img_path=cckkCameraORB._base_path, auto_detect=auto_detect) 

    @property
    def filename(self):
        return self._img_filename