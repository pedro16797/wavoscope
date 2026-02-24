import jsonpatch
import copy
import time
from typing import List, Dict, Any

class UndoStep:
    def __init__(self, label: str, patch: jsonpatch.JsonPatch, timestamp: float):
        self.label = label
        self.patch = patch
        self.timestamp = timestamp

class UndoManager:
    def __init__(self, initial_state: Dict[str, Any], max_steps: int = 50):
        self.max_steps = max_steps
        self.base_state = copy.deepcopy(initial_state)
        self.base_label = "Initial State"
        self.base_timestamp = time.time()
        self.steps: List[UndoStep] = []
        self._current_state = copy.deepcopy(initial_state)

    def set_max_steps(self, max_steps: int):
        self.max_steps = max_steps
        self._truncate()

    def push(self, label: str, new_state: Dict[str, Any]):
        # Ensure new_state is a dict for jsonpatch
        patch = jsonpatch.make_patch(self._current_state, new_state)
        if not patch:
            return

        step = UndoStep(label, patch, time.time())
        self.steps.append(step)
        self._current_state = copy.deepcopy(new_state)
        self._truncate()

    def _truncate(self):
        while len(self.steps) > self.max_steps:
            oldest_step = self.steps.pop(0)
            self.base_state = oldest_step.patch.apply(self.base_state)
            self.base_label = oldest_step.label
            self.base_timestamp = oldest_step.timestamp

    def get_history(self) -> List[Dict[str, Any]]:
        history = [{"label": self.base_label, "timestamp": self.base_timestamp}]
        for step in self.steps:
            history.append({
                "label": step.label,
                "timestamp": step.timestamp
            })
        return history

    def restore(self, index: int) -> Dict[str, Any]:
        state = copy.deepcopy(self.base_state)
        if index > 0:
            for i in range(min(index, len(self.steps))):
                state = self.steps[i].patch.apply(state)
            self.steps = self.steps[:index]
        else:
            self.steps = []

        self._current_state = copy.deepcopy(state)
        return state
