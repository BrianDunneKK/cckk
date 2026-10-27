import cckk.cckkCameraX as cckkCameraX
from cckk.cckkEdgeAI import *


class cckkAITask:
    def __init__(self, name="AI Task"):
        self._name = name

    def init_task(self):
        pass

    def run_task(self) -> bool:
        return True

    def cleanup(self):
        pass


class cckkCameraAITask:
    cam : cckkCameraX.cckkCameraX | None = None
    
    def __init__(self, name="Camera AI Task"):
        self._name = name
        self._frame_avl = False
        self._task : cckkEdgeAITask | None = None
        self._task_success = False

    @property
    def task(self) -> cckkEdgeAITask | None:
        return self._task

    @task.setter
    def task(self, value: cckkEdgeAITask | None):
        self._task = value
    
    def init_task(self) -> None:
        if cckkCameraAITask.cam is None:
            cckkCameraAITask.cam = cckkCameraX.cckkCameraX()

    def run_task(self) -> bool:
        if self.task is not None and cckkCameraAITask.cam is not None:
            self._frame_avl = (cckkCameraAITask.cam.read_frame() is not None)
            self._task_success = self._frame_avl and self.task.run(cckkCameraAITask.cam.frame_rgb) and self.task.result.num_objects() > 0
        return self._task_success

    def cleanup(self) -> None:
        if cckkCameraAITask.cam is not None:
            cckkCameraAITask.cam.release()
            cckkCameraAITask.cam = None
        if self.task is not None:
            self.task.close()


