import cv2                  ## pip install opencv-python
from exif import Image
from datetime import datetime
import math
import numpy as np
import numpy.ma as ma
from logzero import logger  ## pip install logzero
from os.path import join

__version__ = "1.0.0"

# Sony IMX477 image sensor
# Native Aspect Ratio: 4:3.
# Resolution: 4056 x 3040 pixels (12.3 MP).
# Pixel Size: 1.55µm x 1.55µm (square pixels).
# Optical Format: 1/2.3 inch. 
# Focal Length: 16 mm
# GSD (Width): (Flight Altitude × Sensor Width) / (Focal Length × Image Width) 
# GSD = (410 km × 6.2868 mm) / (16 mm × 4056 pixels) = 39.72 m/pixel = 3972 cm/pixel
# From website: GSD = 12648 cm/pixel

# Both the Earth and the ISS move in a west-to-east, or counterclockwise, direction
# when viewed from above the North Pole. The ISS maintains an orbital inclination of
# approximately 51.6 degrees, allowing it to pass over most of the Earth's surface.
# Because the Earth rotates while the ISS orbits, the station passes over a different,
# shifting longitudinal path with every 90-minute orbit, moving roughly 2200 km to
# the west relative to the ground with each revolution.

class cckkORB:
    _orb = cv2.ORB_create(nfeatures = 1000)
    imread_flags = cv2.IMREAD_GRAYSCALE

    def read_colour():
        cckkORB.imread_flags = cv2.IMREAD_COLOR
        
    def read_grayscale():
        cckkORB.imread_flags = cv2.IMREAD_GRAYSCALE

    def __init__(self, img_filename: str, img_path: str, auto_detect: bool = True):
        """Contructs a cckkORB object

        Args:
        img_path: Path to the image file
        auto_detect: If True, automatically detects keypoints and descriptors

        Returns:
        cckkORB  object

        Raises:
        Exception: Never
        """
        self._img_filename = img_filename
        self._img_path = join(img_path, self._img_filename)
        self._img = cv2.imread(self._img_path, cckkORB.imread_flags)
        self._img_orig = self._img.copy()
        self._img_edited = None
        self._keypoints = None
        self._descriptors = None
        if auto_detect:
            self.detectAndCompute()

    @property
    def descriptors(self):
        """ORB descriptors"""
        return self._descriptors
    
    @property
    def keypoints(self):
        """ORB keypoints"""
        return self._keypoints

    @property
    def img(self):
        """Image"""
        return self._img

    def detectAndCompute(self):
        self._keypoints, self._descriptors = cckkORB._orb.detectAndCompute(self._img, None)

    def get_exif_time(self) -> datetime:
        with open(self._img_path, 'rb') as image_file:
            img = Image(image_file)
            time_str = img.get("datetime_original")
            time = datetime.strptime(time_str, '%Y:%m:%d %H:%M:%S')
            return time

    def sobel(self):
        sobelx = cv2.Sobel(self._img, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(self._img, cv2.CV_64F, 0, 1, ksize=3)
        sobel_img = cv2.magnitude(sobelx, sobely)
        sobel_img = cv2.convertScaleAbs(sobel_img)
        self._img_edited = sobel_img
        # sobel = cv2.resize(sobel_img, (1000,600), interpolation = cv2.INTER_AREA)
        # self.show_image(sobel)
        return sobel_img

    def copy_edited_to_img(self):
        if self._img_edited is not None:
            self._img = self._img_edited.copy()
            self._img_edited = None
            
    def copy_orig_to_img(self):
        self._img = self._img_orig.copy()
        self._img_edited = None

    def show_image(self, img, wait_time_ms: int = 0):
        cv2.imshow("imgwindow", img)
        cv2.waitKey(wait_time_ms)
        cv2.destroyWindow("imgwindow")

    @property
    def info(self) -> dict[str, any]:
        """Returns information about the image"""
        ret = {
            "img_path": self._img_path,
            "img_filename": self._img_filename,
            "num_keypoints": len(self._keypoints) if self._keypoints is not None else 0,
            "num_descriptors": len(self._descriptors) if self._descriptors is not None else 0,
            "exif_time": self.get_exif_time()
        }
        return ret


class cckkMatcher:
    _norm_type = cv2.NORM_HAMMING
    _brute_force = cv2.BFMatcher(_norm_type, crossCheck=True)
    _GSD = 12648  # Ground Sample Distance in cm/pixel
    _GSD_km_per_pixel = _GSD / 100000  # GSD in km/pixel

    def __init__(self, img1: cckkORB, img2: cckkORB):
        """Constructs a cckkMatch object.

        Args:
        img1: cckkORB object for image 1
        img2: cckkORB object for image 2

        Returns:
        cckkMatch object

        Raises:
        Exception: Never
        """
        self._img1 = img1
        self._img2 = img2
        self._time_difference = self._img2.get_exif_time() - self._img1.get_exif_time()
        self._time_diff_secs = self._time_difference.seconds
        self._matches = []  # List of cv2.DMatch objects
        self._include_match = []  # List of booleans indicating if match is included in speed calculation
        self._inc_matches_count = 0
        self._avg_distance = None
        self._speed_km_per_sec = None

    @property
    def info(self) -> dict[str, any]:
        """Returns statistics about the matching process"""
        ret = {
            "speed_km_per_sec": self._speed_km_per_sec,
            "num_matches": len(self._matches),
            "num_inc_matches": self._inc_matches_count,
            "avg_distance": self._avg_distance,
            "time_difference_secs": self._time_diff_secs
        }
        return ret

    @property
    def avg_distance(self):
        """Average distance between matched features"""
        if self._avg_distance is None:
            return 0
        return self._avg_distance

    @property
    def speed_km_per_sec(self):
        """Average speed in km/sec between two images"""
        if self._speed_km_per_sec is None:
            return 0
        return self._speed_km_per_sec

    @property
    def matches_inc(self):
        """List of matches included in speed calculation"""
        match_list = []
        for i in range(len(self._matches)):
            if self._include_match[i]:
                match_list.append(self._matches[i])
        return match_list

    def match(self):
        """Matches features between two images using brute-force matcher"""
        self._matches = cckkMatcher._brute_force.match(self._img1.descriptors, self._img2.descriptors)
        self._matches = sorted(self._matches, key=lambda x: x.distance)
        coordinates_1 = []
        coordinates_2 = []
        for match in self._matches:
            (x1,y1) = self._img1.keypoints[match.queryIdx].pt
            (x2,y2) = self._img2.keypoints[match.trainIdx].pt
            coordinates_1.append((x1,y1))
            coordinates_2.append((x2,y2))

        self._coord_matches = list(zip(coordinates_1, coordinates_2))

    def calc_coord_pairs(self):
        """Calculates distances, and angles between coordinate pairs ofmatched features"""
        self._distances = []
        self._angles = []
        for coordinate in self._coord_matches:
            x_difference = coordinate[0][0] - coordinate[1][0]
            y_difference = coordinate[0][1] - coordinate[1][1]
            self._distances.append(math.hypot(x_difference, y_difference))
            self._angles.append(math.degrees(math.atan2(y_difference, x_difference)))

    def draw_matches(self, num_matches: int = 200, size : tuple[int,int] = None):
        match_img = cv2.drawMatches(self._img1.img, self._img1.keypoints,
                                    self._img2.img, self._img2.keypoints,
                                    self.matches_inc[:num_matches], None, matchesThickness=5)
        if size is not None:
            match_img = cv2.resize(match_img, size, interpolation = cv2.INTER_AREA)
        return match_img

    def show_matches(self, num_matches: int = 100, size : tuple[int,int] = None, window_name: str = 'matches', display_time_ms: int = 3000):
        match_img = self.draw_matches(num_matches, size)
        cv2.imshow("sobel", match_img)
        cv2.waitKey(display_time_ms)
        cv2.destroyWindow("sobel")

    def analyse(self, angle_range: int = 5, outlier_percentiles: tuple[int,int] = (10,90)):
        """Analyses angles of matched features to determine which are close to the median value"""
        a = np.array(self._angles)
        med = np.median(a)
        self._include_match = []
        self._inc_matches_count = 0
        for angle in self._angles:
            if angle_range is None or ((med - angle_range) <= angle <= (med + angle_range)):
                self._include_match.append(True)
                self._inc_matches_count += 1
            else:
                self._include_match.append(False)

        """Calculates average distance and speed based on included matches and removing outliers"""
        self._inc_distances = np.array([self._distances[i] for i in range(len(self._distances)) if self._include_match[i]])

        if outlier_percentiles is not None and len(outlier_percentiles) == 2:
            lower_limit = np.percentile(self._inc_distances, outlier_percentiles[0])
            upper_limit = np.percentile(self._inc_distances, outlier_percentiles[1])
        else:
            lower_limit = self._inc_distances.min()
            upper_limit = self._inc_distances.max()

        masked_distances = ma.masked_array(self._inc_distances,
                                           mask=np.logical_or(self._inc_distances<lower_limit, self._inc_distances>upper_limit))

        self._avg_distance = self._inc_distances.mean() * cckkMatcher._GSD_km_per_pixel
        self._avg_distance = masked_distances.mean() * cckkMatcher._GSD_km_per_pixel

        if self._time_diff_secs > 0:
            self._speed_km_per_sec = self._avg_distance / self._time_diff_secs
        else:
            self._speed_km_per_sec = 0


class cckkMatchAnalysis:
    def __init__(self, img1_info, img2_info: dict, matcher_info: dict):
        self.img1_info = img1_info
        self.img2_info = img2_info
        self.matcher_info = matcher_info

    @property
    def speed_km_per_sec(self):
        return self.matcher_info["speed_km_per_sec"]

    @property
    def num_inc_matches(self):
        return self.matcher_info["num_inc_matches"]
    
    @property
    def time_difference_secs(self):
        return self.matcher_info["time_difference_secs"]

    def summary_as_str(self, str_prefix: str = None, line_prefix: str = "  ") -> list[str]:
        str_list = []
        if str_prefix is not None:
            str_list.append(str_prefix)
        str_list.append(line_prefix + "Image 1: " + self.img1_info["img_path"])
        # str_list.append(line_prefix + "  Keypoints: " + str(self.img1_info["num_keypoints"]))
        # str_list.append(line_prefix + "  Descriptors: " + str(self.img1_info["num_descriptors"]))
        # str_list.append(line_prefix + "  EXIF Time: " + (self.img1_info["exif_time"]).strftime('%Y-%m-%d %H:%M:%S'))
        str_list.append(line_prefix + "Image 2: " + self.img2_info["img_path"])
        # str_list.append(line_prefix + "  Keypoints: " + str(self.img2_info["num_keypoints"]))
        # str_list.append(line_prefix + "  Descriptors: " + str(self.img2_info["num_descriptors"]))
        # str_list.append(line_prefix + "  EXIF Time: " + (self.img2_info["exif_time"]).strftime('%Y-%m-%d %H:%M:%S'))
        str_list.append(line_prefix + "Time Difference (secs): " + str(self.matcher_info["time_difference_secs"]))
        str_list.append(line_prefix + "Total Matches: " + str(self.matcher_info["num_matches"]))
        str_list.append(line_prefix + "Included Matches: " + str(self.matcher_info["num_inc_matches"]))
        str_list.append(line_prefix + "Calculated Speed (km/sec): " + str(self.matcher_info["speed_km_per_sec"]))
        return str_list

class cckkCalculateSpeed:
    def __init__(self):
        self.analysis_list = []

    def add_analysis(self, analysis: cckkMatchAnalysis, min_inc_matches: int = 30):
        ret_str = None
        if min_inc_matches is None:
            min_inc_matches = 30
        if (analysis.num_inc_matches >= min_inc_matches):
            self.analysis_list.append(analysis)
        else:
            ret_str = f"Analysis skipped due to insufficient included matches: {analysis.num_inc_matches}"
        return ret_str

    def result(self, outlier_percentiles: tuple[int,int] = (10,90)) -> float:
        """Calculates weighted average speed from all analyses"""

        speeds = []
        inc_matches = []
        time_diffs = []
        for a in self.analysis_list:
            speeds.append(a.speed_km_per_sec)
            inc_matches.append(a.num_inc_matches)
            time_diffs.append(a.time_difference_secs)

        if len(speeds) == 0:
            return 0, {
                "inc_analyses": 0,
                "total_matches": 0,
                "avg_time_diff_secs": 0,
                "speeds_excluded": 0,
                "speed_limits": (0,0)
            }
        
        speeds_excluded = 0
        lower_limit = 0
        upper_limit = 0
        if outlier_percentiles is not None and len(outlier_percentiles) == 2:
            lower_limit = np.percentile(speeds, outlier_percentiles[0])
            upper_limit = np.percentile(speeds, outlier_percentiles[1])

            for i in range(len(speeds)):
                if speeds[i] < lower_limit or speeds[i] > upper_limit:
                    inc_matches[i] = 0  # Exclude from weighted average calculation
                    speeds_excluded += 1

        wt_avg_speed = np.average(speeds, weights=inc_matches) if len(speeds) > 0 else 0
        avg_time_diff_secs = np.mean(time_diffs) if len(time_diffs) > 0 else 0

        return (
            wt_avg_speed,
            {
                "inc_analyses": len(speeds),
                 "total_matches": len(self.analysis_list),
                 "avg_time_diff_secs": avg_time_diff_secs,
                 "speeds_excluded": speeds_excluded,
                 "speed_limits": (lower_limit, upper_limit)
            }
        )
