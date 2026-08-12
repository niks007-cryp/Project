"""
Foundational Job State Machine for Local AI Clipper.
"""

from enum import Enum
from typing import Set, Dict
from clipper.core.errors import InvalidStateTransitionError


class JobState(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    CANCELLED = "CANCELLED"


# Define explicit legal transitions
LEGAL_TRANSITIONS: Dict[JobState, Set[JobState]] = {
    JobState.QUEUED: {JobState.RUNNING, JobState.CANCELLED},
    JobState.RUNNING: {JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED},
    JobState.FAILED: {JobState.RETRYING, JobState.CANCELLED},
    JobState.RETRYING: {JobState.RUNNING, JobState.FAILED, JobState.CANCELLED},
    JobState.SUCCEEDED: set(),  # Terminal state
    JobState.CANCELLED: set(),  # Terminal state
}


class JobStateMachine:
    """Manages legal state transitions for a processing job."""

    def __init__(self, initial_state: JobState = JobState.QUEUED):
        self._current_state = initial_state

    @property
    def current_state(self) -> JobState:
        return self._current_state

    def is_terminal(self) -> bool:
        return self._current_state in (JobState.SUCCEEDED, JobState.CANCELLED)

    def can_transition_to(self, target_state: JobState) -> bool:
        return target_state in LEGAL_TRANSITIONS.get(self._current_state, set())

    def transition_to(self, target_state: JobState) -> JobState:
        """Transitions to the target state if legal, else raises InvalidStateTransitionError."""
        if not isinstance(target_state, JobState):
            try:
                target_state = JobState(target_state)
            except ValueError:
                raise InvalidStateTransitionError(
                    f"Unknown state value: {target_state}"
                )

        if not self.can_transition_to(target_state):
            raise InvalidStateTransitionError(
                f"Illegal state transition from '{self._current_state.value}' to '{target_state.value}'. "
                f"Legal next states: {[s.value for s in LEGAL_TRANSITIONS.get(self._current_state, set())]}"
            )

        self._current_state = target_state
        return self._current_state
