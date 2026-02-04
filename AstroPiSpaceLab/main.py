import cv2
from sys import path

path.append('.')
from os import listdir
import cckkCV
import numpy as np
from logzero import logger

logger.info(f"Starting {__file__}")
logger.info(f"  cv2 version: {cv2.__version__}")
logger.info(f"  numpy version: {np.__version__}")
logger.info(f"  cckkCV version: {cckkCV.__version__}")

config = {
    "output_file_path": "result.txt",
    "image_path": "local_only/Earth1/",
    "angle_range": 5,  #5  # degrees ... 5 or None for no angle filtering
    "outlier_percentiles": (10,90),  # tuple ... (10,90) or None for no outlier filtering
}
logger.info(f"  Angle range: {config['angle_range']} degrees")

image_files = listdir(config['image_path'])
image_files.sort()
# image_files = image_files[6:8]  # Limit number of images for testing

logger.info(f"Loading {len(image_files)} image files from \"{config['image_path']}\"")
img_orbs = []
for i in range(len(image_files)):
    img = cckkCV.cckkORB(img_filename = image_files[i], img_path = config['image_path'], auto_detect=True)

    # img = cckkCV.cckkORB(img_filename = image_files[i], img_path = config['image_path'], auto_detect=False)
    # img.sobel()
    # img.copy_edited_to_img()
    # img.detectAndCompute()

    img_orbs.append(img)
    logger.info(f"  Image {i}: \"{img.info['img_filename']}\" - " +
                f"Keypoints={img.info['num_keypoints']}, " +
                f"DT={img.info['exif_time'].strftime('%Y-%m-%d %H:%M:%S')}")

logger.info(f"Execute match analysis and calculate speed for {len(image_files)-1} image pairs")
calculate_speed = cckkCV.cckkCalculateSpeed()
matcher = None
for i in range(len(image_files)-1):
    img1 = img_orbs[i]
    img2 = img_orbs[i+1]

    matcher = cckkCV.cckkMatcher(img1, img2)
    matcher.match()
    matcher.calc_coord_pairs()
    matcher.analyse(angle_range=config['angle_range'], outlier_percentiles=config['outlier_percentiles'])

    analysis = cckkCV.cckkMatchAnalysis(img1.info, img2.info, matcher.info)
    str = calculate_speed.add_analysis(analysis)
    if str is not None:
        logger.info(f"  Analysis {i} - " + str)
    else:
        for str in analysis.summary_as_str(str_prefix=f"Analysis {i}"):
            logger.info("  " + str)

speed_km_per_sec, result_analysis = calculate_speed.result()
speed_fmt = "{:.4f}".format(speed_km_per_sec)
with open(config['output_file_path'], 'w') as file:
    file.write(speed_fmt)


logger.info(f"Detailed Analysis: Analyses included={result_analysis['inc_analyses']}, " +
            f"Total matches={result_analysis['total_matches']}, " +
            f"Average Time Difference={result_analysis['avg_time_diff_secs']:.2f} secs")
logger.info(f"** RESULT: Speed={speed_fmt} km/sec - Data written to \"{config['output_file_path']}\"")

matcher.show_matches(num_matches=300, size=(1600,800), display_time_ms=0)
