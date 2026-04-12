cckkCamera_ok = True
try:
    from picamzero import Camera # pyright: ignore[reportMissingImports]
except ImportError:
    cckkCamera_ok = False

import cckkCV
from logzero import logger
from os.path import join
from time import sleep

if not cckkCamera_ok:
    logger.warning("cckkCamera: picamzero module not found. Camera functionality will be disabled.")

__version__ = "1.0.0"



class cckkCamera():
    _next_id = 1
    _base_filename = "image"
    _base_path = "./camera"
    _camera = None

    def available() -> bool:
        return cckkCamera_ok

    def _generate_filename() -> str:
        filename = f"{cckkCamera._base_filename}_{cckkCamera._next_id:04d}.jpg"
        cckkCamera._next_id += 1
        return filename
    
    def __init__(self, auto_take=True):
        if not cckkCamera_ok:
            raise ImportError("cckkCamera: picamzero module not found. Cannot use cckkCamera.")

        self._img_filename = None
        
        if cckkCamera._camera is None:
            cckkCamera._camera = Camera()

        if (auto_take):
            self.take_photo()

    @property
    def filename(self) -> str:
        return self._img_filename
    
    def take_photo(self) -> None:
        self._img_filename = cckkCamera._generate_filename()
        img_path = join(cckkCamera._base_path, self._img_filename)
        cckkCamera._camera.take_photo(img_path)

    def start_preview(self) -> None:
        cckkCamera._camera.start_preview()

    def stop_preview(self) -> None:
        cckkCamera._camera.stop_preview()

    def start_stop_preview(self, duration_secs: float) -> None:
        self.start_preview()
        sleep(duration_secs)
        self.stop_preview()


class cckkCameraORB(cckkCV.cckkCV2ORB):
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