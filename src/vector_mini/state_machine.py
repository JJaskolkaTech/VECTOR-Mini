"""Deterministic high-level motion state machine."""

from __future__ import annotations

from dataclasses import dataclass

from .models import Command, State


class InvalidTransition(ValueError):
    """Raised when a command is illegal from the current state."""


@dataclass
class MotionStateMachine:
    state: State = State.IDLE
    entered_at_s: float = 0.0

    _TRANSITIONS = {
        (State.IDLE, Command.ARM): State.ARMING,
        (State.ARMING, Command.FLEX): State.FLEX,
        (State.FLEX, Command.HOLD): State.HOLD,
        (State.HOLD, Command.EXTEND): State.EXTEND,
        (State.EXTEND, Command.RESET): State.RESET,
        (State.RESET, Command.NONE): State.IDLE,
    }

    def dispatch(self, command: Command, now_s: float) -> State:
        if command is Command.E_STOP:
            return self.force_estop(now_s)
        if command is Command.NONE:
            return self.state
        key = (self.state, command)
        if key not in self._TRANSITIONS:
            raise InvalidTransition(f"{command.name} is invalid from {self.state.name}")
        self.state = self._TRANSITIONS[key]
        self.entered_at_s = now_s
        return self.state

    def force_estop(self, now_s: float) -> State:
        self.state = State.E_STOP
        self.entered_at_s = now_s
        return self.state

    def manual_reset(self, now_s: float, mechanism_safe: bool) -> State:
        if self.state is not State.E_STOP:
            raise InvalidTransition("manual reset is only valid from E_STOP")
        if not mechanism_safe:
            raise InvalidTransition("mechanism must be returned to a safe posture")
        self.state = State.IDLE
        self.entered_at_s = now_s
        return self.state

