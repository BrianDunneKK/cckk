from sys import path
path.append('.')
import cckkCV
import cckkCamera
from logzero import logger

logger.info(f"Starting {__file__}")

img_orbs = []
for i in range(3):
    img = cckkCamera.cckkCameraORB(auto_detect=True)
    img_orbs.append(img)
    logger.info(f"  Image {i}: \"{img.filename}\" - ")

