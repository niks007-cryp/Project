"""
Unit Tests for Job State Machine.
"""

import pytest
from clipper.core.state import JobState, JobStateMachine
from clipper.core.errors import InvalidStateTransitionError


def test_initial_state():
    sm = JobStateMachine(JobState.QUEUED)
    assert sm.current_state == JobState.QUEUED
    assert not sm.is_terminal()


def test_legal_transitions():
    sm = JobStateMachine(JobState.QUEUED)

    # QUEUED -> RUNNING
    assert sm.can_transition_to(JobState.RUNNING)
    assert sm.transition_to(JobState.RUNNING) == JobState.RUNNING

    # RUNNING -> FAILED
    assert sm.transition_to(JobState.FAILED) == JobState.FAILED

    # FAILED -> RETRYING
    assert sm.transition_to(JobState.RETRYING) == JobState.RETRYING

    # RETRYING -> RUNNING
    assert sm.transition_to(JobState.RUNNING) == JobState.RUNNING

    # RUNNING -> SUCCEEDED
    assert sm.transition_to(JobState.SUCCEEDED) == JobState.SUCCEEDED
    assert sm.is_terminal()


def test_illegal_transition_raises():
    sm = JobStateMachine(JobState.QUEUED)
    # QUEUED -> SUCCEEDED is illegal
    with pytest.raises(InvalidStateTransitionError):
        sm.transition_to(JobState.SUCCEEDED)


def test_terminal_state_has_no_legal_transitions():
    sm = JobStateMachine(JobState.SUCCEEDED)
    assert sm.is_terminal()
    with pytest.raises(InvalidStateTransitionError):
        sm.transition_to(JobState.RUNNING)
