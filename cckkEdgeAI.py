import os

os.environ["GLOG_minloglevel"] = "2"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import string
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class cckkEdgeAIResult:
    def __init__(self, name: str = "Result of Edge AI task"):
        self._name = name
        self._labels = []
        self._scores = []
        self._positions = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def success(self) -> str:
        return self._labels and len(self._labels) > 0

    def label(self, idx: int = 0) -> str:
        if (idx < 0):
            return ", ".join(self._labels)
        elif idx >= 0 and idx < len(self._labels) and len(self._labels) > 0:
            return self._labels[idx]
        else:
            return ""

    def score(self, idx: int = 0) -> float:
        if idx >= 0 and idx < len(self._scores) and len(self._scores) > 0:
            return self._scores[idx]
        else:
            return None

    def position(self, idx: int = 0, sub_idx : int = 0, scale_to : list[int] = [1,1,1]) -> any:
        if idx >= 0 and idx < len(self._positions) and len(self._positions) > 0:
            points = self._positions[idx] 
            if sub_idx >= 0 and sub_idx < len(points) and len(points) > 0:
                pos = points[sub_idx]
                if len(scale_to) == 2:
                    scale_to.append(1)
                if (len(scale_to) >= 3):
                    pos.x = int(pos.x * scale_to[0])
                    pos.y = int(pos.y * scale_to[1])
                    pos.z = int(pos.z * scale_to[2])
                return pos
        return None

    def pos_xyz(self, idx: int = 0, sub_idx : int = 0, scale_to : list[int] = [1,1,1]) -> list[int]:
        pos = self.position(idx=idx, sub_idx=sub_idx, scale_to=scale_to)
        return [pos.x, pos.y, pos.z]

class cckkMediaPipeResult(cckkEdgeAIResult):
    def __init__(self, name: str = "Result of MediaPipe AI task"):
        super().__init__(name=name)
        self._gestures = []

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

    def run(self) -> bool:
        """Run the Edge AI task and return success flag"""
        self.create_result()
        return True

    def create_result(self) -> None:
        self._result = cckkEdgeAIResult(self.name + " result")



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
        self.create_result()

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

    def set_image(self, image: any, image_format: any = mp.ImageFormat.SRGB):
        self._image = mp.Image(image_format=image_format, data=image)

    def run(self, data: any = None) -> bool:
        self.create_result()
        return True

    def create_result(self) -> None:
        self._result = cckkMediaPipeResult(self.name + " result")

    def close(self) -> None:
        if self.skill is not None:
            self.skill.close()


class cckkMPGestureRecognizer(cckkMediaPipeTask):
    def __init__(self, task_path: str = "", name: str = "Gesture Recogniser task"):
        super().__init__(
            task_path=task_path, task_file="gesture_recognizer.task", name=name
        )
        options = vision.GestureRecognizerOptions(base_options=self.base_options)
        self._skill = vision.GestureRecognizer.create_from_options(options)

    def run(self, data: any = None) -> bool:
        if data is not None:
            self.set_image(data)

        self.create_result()
        skill_result = self.skill.recognize(self.image)
        if skill_result.gestures:
            for idx, gestures in enumerate(skill_result.gestures):
                if not gestures:
                    continue
                self._result._labels.append(gestures[0].category_name)
                self._result._scores.append(gestures[0].score)  # Get confidence score

        if skill_result.hand_landmarks:
            for idx, hand_landmarks in enumerate(skill_result.hand_landmarks):
                if not hand_landmarks:
                    continue

                self._result._positions.append(hand_landmarks)  # Add array of landmarks

        return self.result.success


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


    def run(self, data: any = None) -> bool:
        if data is not None:
            self.set_image(data)

        self.create_result()
        skill_result = self.skill.recognize(self.image)
        if skill_result.hand_landmarks:
            for idx, hand_landmarks in enumerate(skill_result.hand_landmarks):
                if not hand_landmarks:
                    continue

                self._result._positions.append(hand_landmarks)  # Add array of landmarks

        return self.result.success