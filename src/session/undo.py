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
    """History of project states as forward json-patches from a base snapshot.

    A `cursor` marks the current position (0 = base, k = after steps[k-1]).
    Undo/redo move the cursor without destroying steps; a new edit made while the
    cursor is behind the tip discards the now-orphaned redo branch.
    """

    def __init__(self, initial_state: Dict[str, Any], max_steps: int = 50):
        self.max_steps = max_steps
        self.base_state = copy.deepcopy(initial_state)
        self.base_label = "Initial State"
        self.base_timestamp = time.time()
        self.steps: List[UndoStep] = []
        self.cursor = 0
        self._current_state = copy.deepcopy(initial_state)

    def set_max_steps(self, max_steps: int):
        self.max_steps = max_steps
        self._truncate()

    def push(self, label: str, new_state: Dict[str, Any]):
        patch = jsonpatch.make_patch(self._current_state, new_state)
        if not patch:
            return

        # A new edit made after undo(s) discards the redo branch.
        if self.cursor < len(self.steps):
            del self.steps[self.cursor:]

        self.steps.append(UndoStep(label, patch, time.time()))
        self.cursor = len(self.steps)
        self._current_state = copy.deepcopy(new_state)
        self._truncate()

    def _truncate(self):
        while len(self.steps) > self.max_steps:
            oldest_step = self.steps.pop(0)
            self.base_state = oldest_step.patch.apply(self.base_state)
            self.base_label = oldest_step.label
            self.base_timestamp = oldest_step.timestamp
            self.cursor = max(0, self.cursor - 1)

    def _state_at(self, index: int) -> Dict[str, Any]:
        state = copy.deepcopy(self.base_state)
        for i in range(min(index, len(self.steps))):
            state = self.steps[i].patch.apply(state)
        return state

    def get_history(self) -> List[Dict[str, Any]]:
        history = [{"label": self.base_label, "timestamp": self.base_timestamp}]
        for step in self.steps:
            history.append({
                "label": step.label,
                "timestamp": step.timestamp
            })
        return history

    def restore(self, index: int) -> Dict[str, Any]:
        """Move the cursor to `index` and return that state (non-destructive)."""
        index = max(0, min(index, len(self.steps)))
        self.cursor = index
        state = self._state_at(index)
        self._current_state = copy.deepcopy(state)
        return state

    @property
    def can_undo(self) -> bool:
        return self.cursor > 0

    @property
    def can_redo(self) -> bool:
        return self.cursor < len(self.steps)

    def undo(self) -> Dict[str, Any]:
        if not self.can_undo:
            return self._current_state
        return self.restore(self.cursor - 1)

    def redo(self) -> Dict[str, Any]:
        if not self.can_redo:
            return self._current_state
        return self.restore(self.cursor + 1)
