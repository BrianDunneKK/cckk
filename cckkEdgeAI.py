# To Do
# - Populate score for HandLanmarkerResult and GestureRecognizerResult

import os

os.environ["GLOG_minloglevel"] = "2"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

from typing import Any
import string
from collections import deque
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from dataclasses import dataclass

@dataclass
class cckkPosition:
    x: float
    y: float
    z: float

    def scale_to(self, scale_to: list[int] = [1, 1, 1]) -> None:
        if len(scale_to) == 2:
            scale_to.append(1)
        if len(scale_to) >= 3:
            return cckkPosition(
                x=self.x * scale_to[0], y=self.y * scale_to[1], z=self.z * scale_to[2]
            )
        return None

class cckkObject:
    def __init__(self, name: str = "Object"):
        self._name = name
        self._score = 0.0
        self._attributes: dict[str, str] = {}
        self._positions: list[cckkPosition] = []

    def get(self, key: str) -> str:
        if key in self._attributes:
            return self._attributes[key]
        else:
            return ""


class cckkEdgeAIResult:
    def __init__(self, name: str = "Result of Edge AI task"):
        self._name = name
        self._hx_max_len = 0
        self._hx_objs_lms = deque()
        self._raw_result = None
        self._objects: list[cckkObject] = []
        self.clear()

    @property
    def name(self) -> str:
        return self._name

    @property
    def history(self) -> int:
        return self._hx_max_len

    @history.setter
    def history(self, value: int):
        if value > 0:
            self._hx_max_len = value
            self._hx_objs_lms = deque(maxlen=self._hx_max_len)

    @property
    def success(self) -> bool:
        return self.num_objects() > 0  # At least one object detected

    def get_obj_attribute(self, obj_idx: int = 0, attr: str = "") -> str:
        if obj_idx >= 0 and obj_idx < len(self._objects) and len(self._objects) > 0:
            return self._objects[obj_idx].get(attr)
        else:
            return ""
        
    def clear(self) -> None:
        self._objects: list[cckkObject] = []

        # Label and score for each object
        self._labels = []
        self._scores = []

        # List of objects, each of which is a list of landmarks, each of which is a scaled cckkPosition
        self._objs_lms = [] 

    def populate(self, raw_result: Any, clear_first: bool = True) -> None:
        # Populate the result labels, objects, landmarks and any other info in the result
        if clear_first:
            self.clear()

    def score(self, obj_idx: int = 0) -> float:
        if obj_idx >= 0 and obj_idx < len(self._scores) and len(self._scores) > 0:
            return self._scores[obj_idx]
        else:
            return 0

    def num_hx_objects(self) -> int:
        if self._hx_objs_lms is None:
            return 0
        return len(self._hx_objs_lms)

    def num_objects(self) -> int:
        return len(self._objects)

    def num_landmarks(self, obj_idx: int = 0) -> int:
        if obj_idx >= 0 and obj_idx < self.num_objects() and self.num_objects() > 0:
            return len(self._objects[obj_idx]._positions)
        return 0

    def num_polylines(self, obj_idx: int = 0) -> int:
        return 0

    def _lm2pos(self, landmark, scale_to: list[int]) -> cckkPosition|None:
        # Convert a landmark return by MediaaPipe to a simple cckkPosition
        if landmark is None:
            return None
        pos = cckkPosition(x=landmark.x, y=landmark.y, z=landmark.z)
        if len(scale_to) == 2:
            scale_to.append(1)
        if len(scale_to) >= 3:
            pos.x = pos.x * scale_to[0]
            pos.y = pos.y * scale_to[1]
            pos.z = pos.z * scale_to[2]
        return pos

    def landmark(
        self, obj_idx: int = 0, lm_idx: int = 0, scale_to: list[int] = [1, 1, 1]
    ) -> cckkPosition|None:
        if obj_idx >= 0 and obj_idx < self.num_objects() and self.num_objects() > 0:
            points = self._objects[obj_idx]._positions
            if lm_idx >= 0 and lm_idx < len(points) and len(points) > 0:
                # Create a new object so that the result is not modified
                return points[lm_idx].scale_to(scale_to=scale_to)
        return None

    def pos_xyz(
        self, obj_idx: int = 0, lm_idx: int = 0, scale_to: list[int] = [1, 1, 1]
    ) -> list[int]|list[None]:
        pos = self.landmark(obj_idx=obj_idx, lm_idx=lm_idx, scale_to=scale_to)
        if pos is None:
            return [None, None, None]
        return [int(pos.x), int(pos.y), int(pos.z)]

    def pos_xy(
        self, obj_idx: int = 0, lm_idx: int = 0, scale_to: list[int] = [1, 1, 1]
    ) -> list[int]|list[None]:
        pos = self.pos_xyz(obj_idx=obj_idx, lm_idx=lm_idx, scale_to=scale_to)
        return [pos[0], pos[1]]

    def polyline(
        self, obj_idx: int = 0, poly_idx: int = 0, scale_to: list[int] = [1, 1, 1]
    ) -> np.ndarray:
        empty_pts = np.empty((0, 1, 2), dtype=np.int32)
        return empty_pts

    def hx_landmark(
        self, obj_idx: int = 0, lm_idx: int = 0, scale_to: list[int] = [1, 1, 1]
    ) -> list[cckkPosition]|None:
        hx_pos = []
        if self._hx_objs_lms is not None:
            for hx_result in self._hx_objs_lms:
                if obj_idx >= 0 and obj_idx < len(hx_result) and len(hx_result) > 0:
                    obj = hx_result[obj_idx]
                    if lm_idx >= 0 and lm_idx < len(obj) and len(obj) > 0:
                        # Create a new object so that the result is not modified
                        hx_pos.append(self._lm2pos(landmark=obj[lm_idx], scale_to=scale_to))

        return hx_pos


class cckkMediaPipeResult(cckkEdgeAIResult):
    def __init__(self, name: str = "Result of MediaPipe AI task"):
        super().__init__(name=name)
        self.clear()

    def clear(self) -> None:
        super().clear()
        self._sides = []
        self._gestures = []

    def side(self, obj_idx: int = 0) -> str:
        if obj_idx >= 0 and obj_idx < len(self._sides) and len(self._sides) > 0:
            return self._sides[obj_idx]
        else:
            return ""

    def side_obj_idx(self, side: str) -> int:
        ret_idx = -1  # Not found
        for i in range(len(self._sides)):
            if self.side(i) == side:
                ret_idx = i
        return ret_idx

    def pos_xyz_side(
        self, side: str, lm_idx: int = 0, scale_to: list[int] = [1, 1, 1]
    ) -> list[int]:
        obj_idx = self.side_obj_idx(side)
        pos = self.pos_xyz(obj_idx=obj_idx, lm_idx=lm_idx, scale_to=scale_to)
        if pos is None:
            return [None, None, None]
        return pos

    def pos_xy_side(
        self, side: str, lm_idx: int = 0, scale_to: list[int] = [1, 1, 1]
    ) -> list[int]:
        pos = self.pos_xyz_side(side=side, lm_idx=lm_idx, scale_to=scale_to)
        return [pos[0], pos[1]]

    def gesture(self, obj_idx: int = 0) -> any:
        if obj_idx >= 0 and obj_idx < len(self._gestures) and len(self._gestures) > 0:
            return self._gestures[obj_idx]
        else:
            return None


class cckkEdgeAITask:
    def __init__(self, name: str = "Edge AI task"):
        print(f"Initializing Edge AI task {name}")
        self._name = name
        self._scale_to = [1, 1, 1]
        self.create_result()

    @property
    def name(self) -> str:
        return self._name

    @property
    def scale_to(self) -> list[int]:
        return self._scale_to

    @scale_to.setter
    def scale_to(self, value: list[int]):
        if isinstance(value, list) and len(value) >= 2:
            if (len(value) == 2):
                value.append(1)
            self._scale_to = value  

    @property
    def result(self) -> cckkEdgeAIResult:
        return self._result

    def run(self, data: Any = None) -> bool:
        """Run the Edge AI task and return success flag"""
        self._result.clear()
        return True

    def create_result(self) -> None:
        self._result = cckkEdgeAIResult(self.name + " result")

    def set_result_history(self, length:int = 10) -> None:
        self._result.history = length


class cckkMediaPipeTask(cckkEdgeAITask):

    def __init__(
        self, task_path: str = "", task_file: str = "", name: str = "MediaPipe task"
    ):
        super().__init__(name=name)
        self._task_path = task_path
        self._task_file = task_file
        self._task_path_file = task_path + task_file
        self._base_options = None
        if self._task_path_file != "":
            self._base_options = python.BaseOptions(
                model_asset_path=self._task_path_file
            )
        self._image = None
        self._skill = None

    @property
    def base_options(self) -> any:
        return self._base_options

    @property
    def image(self) -> any:
        return self._image

    @property
    def skill(self) -> any:
        return self._skill

    @property
    def result(self) -> cckkMediaPipeResult:
        return self._result

    def set_image(self, image: Any, image_format: Any = mp.ImageFormat.SRGB):
        self._image = mp.Image(image_format=image_format, data=image)

    def create_result(self) -> None:
        self._result = cckkMediaPipeResult(self.name + " result")

    def close(self) -> None:
        if self.skill is not None:
            self.skill.close()

class cckkMPGestureRecognizerResult(cckkMediaPipeResult):
    def populate(self, raw_result: vision.GestureRecognizerResult, clear_first: bool = True) -> None:
        if clear_first:
            self.clear()
        self._raw_result = raw_result


        if self._raw_result.gestures:
            num_objects = len(self._raw_result.gestures)
        else:
            num_objects = 0

        for obj_idx in range(num_objects):
            if len(self._raw_result.handedness) > obj_idx:
                handedness = self._raw_result.handedness[obj_idx][0].category_name
                obj_name = f"{handedness} hand"
            else:
                obj_name = f"Hand {obj_idx+1}"

            obj_result = cckkObject(name=obj_name)
            obj_result._attributes["handedness"] = handedness
            obj_result._attributes["side"] = handedness

            if len(self._raw_result.gestures) > obj_idx:
                obj_gestures = self._raw_result.gestures[obj_idx]
                obj_result._attributes["label"] = obj_gestures[0].category_name

            if len(self._raw_result.hand_landmarks) > obj_idx:
                obj_lms = self._raw_result.hand_landmarks[obj_idx]
                for lm_idx, lm in enumerate(obj_lms):
                    obj_result._positions.append(cckkPosition(x=lm.x, y=lm.y, z=lm.z))

            self._objects.append(obj_result)


class cckkMPGestureRecognizer(cckkMediaPipeTask):
    def __init__(
        self,
        task_path: str = "",
        num_hands: int = 1,
        name: str = "Gesture Recogniser task",
    ):
        super().__init__(
            task_path=task_path, task_file="gesture_recognizer.task", name=name
        )
        options = vision.GestureRecognizerOptions(
            base_options=self.base_options, num_hands=num_hands
        )
        self._skill = vision.GestureRecognizer.create_from_options(options)

    def create_result(self) -> None:
        self._result = cckkMPGestureRecognizerResult(self.name + " result")

    def run(self, data: Any = None) -> bool:
        if data is not None:
            self.set_image(data)


        raw_result = self.skill.recognize(self.image)
        self._result.populate(raw_result, clear_first=True)
        return self._result.success


class cckkMPHandLandmarkerResult(cckkMediaPipeResult):
    def populate(self, raw_result: vision.HandLandmarkerResult, clear_first: bool = True) -> None:
        # raw_result is a list of lists (List[List[NormalizedLandmark]]).
        # Each inner list corresponds to a single detected hand
        # and contains 21 3D landmark points (indexed from 0 to 20).

        if clear_first:
            self.clear()
        self._raw_result = raw_result

        if self._raw_result.hand_landmarks:
            num_objects = len(self._raw_result.hand_landmarks)
        else:
            num_objects = 0

        for obj_idx in range(num_objects):
            if len(self._raw_result.handedness) > obj_idx:
                handedness = self._raw_result.handedness[obj_idx][0].category_name
                obj_name = f"{handedness} hand"
            else:
                obj_name = f"Hand {obj_idx+1}"

            obj_lms = self._raw_result.hand_landmarks[obj_idx]
            obj_result = cckkObject(name=obj_name)
            obj_result._attributes["handedness"] = handedness
            obj_result._attributes["side"] = handedness

            for lm_idx, lm in enumerate(obj_lms):
                obj_result._positions.append(cckkPosition(x=lm.x, y=lm.y, z=lm.z))

            self._objects.append(obj_result)

    def num_polylines(self, obj_idx: int = 0) -> int:
        if obj_idx >= 0 and obj_idx < self.num_objects():
            return 6
        else:
            return 0

    def polyline(
        self, obj_idx: int = 0, poly_idx: int = 0, scale_to: list[int] = [1, 1, 1]
    ) -> np.ndarray:
        pline = np.empty((0, 1, 2), dtype=np.int32)
        match poly_idx:
            case 0:  # Palm
                pline = np.array(
                    [
                        self.pos_xy(obj_idx=obj_idx, lm_idx=0, scale_to=scale_to),
                        self.pos_xy(obj_idx=obj_idx, lm_idx=5, scale_to=scale_to),
                        self.pos_xy(obj_idx=obj_idx, lm_idx=9, scale_to=scale_to),
                        self.pos_xy(obj_idx=obj_idx, lm_idx=13, scale_to=scale_to),
                        self.pos_xy(obj_idx=obj_idx, lm_idx=17, scale_to=scale_to),
                        self.pos_xy(obj_idx=obj_idx, lm_idx=0, scale_to=scale_to),
                    ],
                    np.int32,
                )
            case 1:  # Thumb
                pline = np.array(
                    [
                        self.pos_xy(obj_idx=obj_idx, lm_idx=0, scale_to=scale_to),
                        self.pos_xy(obj_idx=obj_idx, lm_idx=1, scale_to=scale_to),
                        self.pos_xy(obj_idx=obj_idx, lm_idx=2, scale_to=scale_to),
                        self.pos_xy(obj_idx=obj_idx, lm_idx=3, scale_to=scale_to),
                        self.pos_xy(obj_idx=obj_idx, lm_idx=4, scale_to=scale_to),
                    ],
                    np.int32,
                )
            case 2:  # Index
                pline = np.array(
                    [
                        self.pos_xy(obj_idx=obj_idx, lm_idx=5, scale_to=scale_to),
                        self.pos_xy(obj_idx=obj_idx, lm_idx=6, scale_to=scale_to),
                        self.pos_xy(obj_idx=obj_idx, lm_idx=7, scale_to=scale_to),
                        self.pos_xy(obj_idx=obj_idx, lm_idx=8, scale_to=scale_to),
                    ],
                    np.int32,
                )
            case 3:  # Middle
                pline = np.array(
                    [
                        self.pos_xy(obj_idx=obj_idx, lm_idx=9, scale_to=scale_to),
                        self.pos_xy(obj_idx=obj_idx, lm_idx=10, scale_to=scale_to),
                        self.pos_xy(obj_idx=obj_idx, lm_idx=11, scale_to=scale_to),
                        self.pos_xy(obj_idx=obj_idx, lm_idx=12, scale_to=scale_to),
                    ],
                    np.int32,
                )
            case 4:  # Ring
                pline = np.array(
                    [
                        self.pos_xy(obj_idx=obj_idx, lm_idx=13, scale_to=scale_to),
                        self.pos_xy(obj_idx=obj_idx, lm_idx=14, scale_to=scale_to),
                        self.pos_xy(obj_idx=obj_idx, lm_idx=15, scale_to=scale_to),
                        self.pos_xy(obj_idx=obj_idx, lm_idx=16, scale_to=scale_to),
                    ],
                    np.int32,
                )
            case 5:  # Pinky
                pline = np.array(
                    [
                        self.pos_xy(obj_idx=obj_idx, lm_idx=17, scale_to=scale_to),
                        self.pos_xy(obj_idx=obj_idx, lm_idx=18, scale_to=scale_to),
                        self.pos_xy(obj_idx=obj_idx, lm_idx=19, scale_to=scale_to),
                        self.pos_xy(obj_idx=obj_idx, lm_idx=20, scale_to=scale_to),
                    ],
                    np.int32,
                )
            case _:
                poly = super().polyline(obj_idx, poly_idx, scale_to)

        pline = pline.reshape((-1, 1, 2))
        return pline


class cckkMPHandLandmarker(cckkMediaPipeTask):
    def __init__(
        self,
        task_path: str = "",
        num_hands: int = 1,
        name: str = "Hand Landmarker task",
    ):
        super().__init__(
            name=name, task_path=task_path, task_file="hand_landmarker.task"
        )
        options = vision.HandLandmarkerOptions(
            base_options=self.base_options, num_hands=num_hands
        )
        self._skill = vision.HandLandmarker.create_from_options(options)

    def create_result(self) -> None:
        self._result = cckkMPHandLandmarkerResult(self.name + " result")

    def run(self, data: Any = None) -> bool:
        if data is not None:
            self.set_image(data)

        raw_result = self.skill.detect(self.image)
        self._result.populate(raw_result, clear_first=True)
        return self._result.success
