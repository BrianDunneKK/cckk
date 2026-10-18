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


class cckkEdgeAIResult:
    def __init__(self, name: str = "Result of Edge AI task"):
        self._name = name
        self._hx_max_len = 0
        self._hx_objs_lms = deque()
        self.raw_result = None
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
        return len(self._labels) > 0 or len(self._objs_lms) > 0

    def clear(self) -> None:
        self._labels = []
        self._scores = []
        self._objs_lms = []  # List of objects, each of which is a list of landmarks

    def populate(self, raw_result: Any) -> None:
        pass

    def num_labels(self) -> int:
        return len(self._labels)

    def label(self, idx: int = 0) -> str:
        if idx < 0:
            return ", ".join(self._labels)
        elif idx >= 0 and idx < len(self._labels) and len(self._labels) > 0:
            return self._labels[idx]
        else:
            return ""

    def score(self, idx: int = 0) -> float:
        if idx >= 0 and idx < len(self._scores) and len(self._scores) > 0:
            return self._scores[idx]
        else:
            return 0

    def num_hx_objects(self) -> int:
        if self._hx_objs_lms is None:
            return 0
        return len(self._hx_objs_lms)

    def num_objects(self) -> int:
        return len(self._objs_lms)

    def num_landmarks(self, idx: int = 0) -> int:
        if idx >= 0 and idx < len(self._objs_lms) and len(self._objs_lms) > 0:
            return len(self._objs_lms[idx])
        return 0

    def num_polylines(self, idx: int = 0) -> int:
        return 0

    def append_objs_lms(self, objs_lms) -> None:
        self._objs_lms.append(objs_lms)
        if self._hx_max_len > 0 and self._hx_objs_lms is not None:
            self._hx_objs_lms.append(objs_lms)

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
        self, idx: int = 0, sub_idx: int = 0, scale_to: list[int] = [1, 1, 1]
    ) -> cckkPosition|None:
        if idx >= 0 and idx < len(self._objs_lms) and len(self._objs_lms) > 0:
            points = self._objs_lms[idx]
            if sub_idx >= 0 and sub_idx < len(points) and len(points) > 0:
                # Create a new object so that the result is not modified
                return self._lm2pos(landmark=points[sub_idx], scale_to=scale_to)
        return None

    def pos_xyz(
        self, idx: int = 0, sub_idx: int = 0, scale_to: list[int] = [1, 1, 1]
    ) -> list[int]|list[None]:
        pos = self.landmark(idx=idx, sub_idx=sub_idx, scale_to=scale_to)
        if pos is None:
            return [None, None, None]
        return [int(pos.x), int(pos.y), int(pos.z)]

    def pos_xy(
        self, idx: int = 0, sub_idx: int = 0, scale_to: list[int] = [1, 1, 1]
    ) -> list[int]|list[None]:
        pos = self.pos_xyz(idx=idx, sub_idx=sub_idx, scale_to=scale_to)
        return [pos[0], pos[1]]

    def polyline(
        self, idx: int = 0, sub_idx: int = 0, scale_to: list[int] = [1, 1, 1]
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

    def side(self, idx: int = 0) -> str:
        if idx >= 0 and idx < len(self._sides) and len(self._sides) > 0:
            return self._sides[idx]
        else:
            return ""

    def side_idx(self, side: str) -> int:
        ret_idx = -1  # Not found
        for i in range(len(self._sides)):
            if self.side(i) == side:
                ret_idx = i
        return ret_idx

    def pos_xyz_side(
        self, side: str, sub_idx: int = 0, scale_to: list[int] = [1, 1, 1]
    ) -> list[int]:
        idx = self.side_idx(side)
        pos = self.pos_xyz(idx=idx, sub_idx=sub_idx, scale_to=scale_to)
        if pos is None:
            return [None, None, None]
        return pos

    def pos_xy_side(
        self, side: str, sub_idx: int = 0, scale_to: list[int] = [1, 1, 1]
    ) -> list[int]:
        pos = self.pos_xyz_side(side=side, sub_idx=sub_idx, scale_to=scale_to)
        return [pos[0], pos[1]]

    def gesture(self, idx: int = 0) -> any:
        if idx >= 0 and idx < len(self._gestures) and len(self._gestures) > 0:
            return self._gestures[idx]
        else:
            return None


class cckkEdgeAITask:
    def __init__(self, name: str = "Edge AI task"):
        print(f"Initializing Edge AI task {name}")
        self._name = name
        self.create_result()

    @property
    def name(self) -> str:
        return self._name

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

    def run(self, data: Any = None) -> bool:
        if data is not None:
            self.set_image(data)

        self._result.clear()
        self._result.raw_result = self.skill.recognize(self.image)
        if self._result.raw_result.gestures:
            for idx, gestures in enumerate(self._result.raw_result.gestures):
                if not gestures:
                    continue
                self._result._labels.append(gestures[0].category_name)
                self._result._scores.append(gestures[0].score)  # Get confidence score

        if self._result.raw_result.hand_landmarks:
            for idx, hand_landmarks in enumerate(
                self._result.raw_result.hand_landmarks
            ):
                if not hand_landmarks:
                    continue

                self._result.append_objs_lms(hand_landmarks)  # Add array of landmarks

        if self._result.raw_result.handedness:
            for idx, handedness in enumerate(self._result.raw_result.handedness):
                if not handedness:
                    continue
                self._result._sides.append(handedness[0].category_name)

        return self.result.success


class cckkMPHandLandmarkerResult(cckkMediaPipeResult):
    def num_polylines(self, idx: int = 0) -> int:
        if idx >= 0 and idx < self.num_objects():
            return 6
        else:
            return 0

    def polyline(
        self, idx: int = 0, sub_idx: int = 0, scale_to: list[int] = [1, 1, 1]
    ) -> np.ndarray:
        pline = np.empty((0, 1, 2), dtype=np.int32)
        match sub_idx:
            case 0:  # Palm
                pline = np.array(
                    [
                        self.pos_xy(idx=idx, sub_idx=0, scale_to=scale_to),
                        self.pos_xy(idx=idx, sub_idx=5, scale_to=scale_to),
                        self.pos_xy(idx=idx, sub_idx=9, scale_to=scale_to),
                        self.pos_xy(idx=idx, sub_idx=13, scale_to=scale_to),
                        self.pos_xy(idx=idx, sub_idx=17, scale_to=scale_to),
                        self.pos_xy(idx=idx, sub_idx=0, scale_to=scale_to),
                    ],
                    np.int32,
                )
            case 1:  # Thumb
                pline = np.array(
                    [
                        self.pos_xy(idx=idx, sub_idx=0, scale_to=scale_to),
                        self.pos_xy(idx=idx, sub_idx=1, scale_to=scale_to),
                        self.pos_xy(idx=idx, sub_idx=2, scale_to=scale_to),
                        self.pos_xy(idx=idx, sub_idx=3, scale_to=scale_to),
                        self.pos_xy(idx=idx, sub_idx=4, scale_to=scale_to),
                    ],
                    np.int32,
                )
            case 2:  # Index
                pline = np.array(
                    [
                        self.pos_xy(idx=idx, sub_idx=5, scale_to=scale_to),
                        self.pos_xy(idx=idx, sub_idx=6, scale_to=scale_to),
                        self.pos_xy(idx=idx, sub_idx=7, scale_to=scale_to),
                        self.pos_xy(idx=idx, sub_idx=8, scale_to=scale_to),
                    ],
                    np.int32,
                )
            case 3:  # Middle
                pline = np.array(
                    [
                        self.pos_xy(idx=idx, sub_idx=9, scale_to=scale_to),
                        self.pos_xy(idx=idx, sub_idx=10, scale_to=scale_to),
                        self.pos_xy(idx=idx, sub_idx=11, scale_to=scale_to),
                        self.pos_xy(idx=idx, sub_idx=12, scale_to=scale_to),
                    ],
                    np.int32,
                )
            case 4:  # Ring
                pline = np.array(
                    [
                        self.pos_xy(idx=idx, sub_idx=13, scale_to=scale_to),
                        self.pos_xy(idx=idx, sub_idx=14, scale_to=scale_to),
                        self.pos_xy(idx=idx, sub_idx=15, scale_to=scale_to),
                        self.pos_xy(idx=idx, sub_idx=16, scale_to=scale_to),
                    ],
                    np.int32,
                )
            case 5:  # Pinky
                pline = np.array(
                    [
                        self.pos_xy(idx=idx, sub_idx=17, scale_to=scale_to),
                        self.pos_xy(idx=idx, sub_idx=18, scale_to=scale_to),
                        self.pos_xy(idx=idx, sub_idx=19, scale_to=scale_to),
                        self.pos_xy(idx=idx, sub_idx=20, scale_to=scale_to),
                    ],
                    np.int32,
                )
            case _:
                poly = super().polyline(idx, sub_idx, scale_to)

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

        self._result.clear()
        self._result.raw_result = self.skill.detect(self.image)
        if self._result.raw_result.hand_landmarks:
            for idx, hand_landmarks in enumerate(
                self._result.raw_result.hand_landmarks
            ):  # Add array of hands
                if not hand_landmarks:
                    continue
                self._result.append_objs_lms(hand_landmarks)  # Add array of landmarks

        if self._result.raw_result.handedness:
            for idx, handedness in enumerate(self._result.raw_result.handedness):
                if not handedness:
                    continue
                self._result._sides.append(handedness[0].category_name)

        return self.result.success


# task.result.raw_result.handedness[0][0].category_name = "Right"
