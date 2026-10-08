import os

os.environ["GLOG_minloglevel"] = "2"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class cckkEdgeAITask:
    def __init__(self, name: str = "Edge AI task"):
        print(f"Initializing Edge AI task {name}")
        self._name = name
        self._result = ""

    @property
    def name(self) -> str:
        return self._name

    @property
    def result(self) -> any:
        return self._result

    def run(self) -> bool:
        """Run the Edge AI task and return success flag"""
        self._result = "Task complete"
        return True


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
        self._result = None

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
    def result(self) -> any:
        return self._result

    def set_image(self, image: any, image_format: any = mp.ImageFormat.SRGB):
        self._image = mp.Image(image_format=image_format, data=image)

    def run(self, data: any = None) -> bool:
        self._result = None
        return True

    def result_label(self, idx: int = 0) -> str | list[str]:
        if idx >= 0:
            return ""
        else:
            return [""]

    def result_score(self, idx: int = 0) -> float | list[float]:
        if idx >= 0:
            return 0.0
        else:
            return [0.0]

    def result_position(self, idx: int = 0, sub_idx: int = 0) -> any:
        if idx >= 0:
            return None
        else:
            return [None]

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

    def result_label(self, idx: int = 0) -> str | list[str]:
        labels = []

        if self.result.gestures:
            for idx, gestures in enumerate(self.result.gestures):
                if not gestures:
                    continue

                labels.append(gestures[0].category_name)

        if idx >= 0:
            return labels[idx]
        else:
            return labels

    def result_score(self, idx: int = 0) -> float | list[float]:
        scores = []

        if self.result.gestures:
            for idx, gestures in enumerate(self.result.gestures):
                if not gestures:
                    continue

                scores.append(gestures[0].score)  # Get confidence score

        if idx >= 0:
            return scores[idx]
        else:
            return scores

    def result_position(self, idx: int = 0, sub_idx: int = 0) -> any:
        positions = []

        if self.result.hand_landmarks:
            for idx, hand_landmarks in enumerate(self.result.hand_landmarks):
                if not hand_landmarks:
                    continue

                positions.append(hand_landmarks)  # Add array of landmarks

        if idx >= 0:
            if sub_idx >= 0:
                return positions[idx][sub_idx]
            else:
                return positions[idx]
        else:
            return positions

    def run(self, data: any = None) -> bool:
        if data is not None:
            self.set_image(data)

        self._result = self.skill.recognize(self.image)
        return self.result.gestures and len(self.result.gestures[0]) > 0


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
