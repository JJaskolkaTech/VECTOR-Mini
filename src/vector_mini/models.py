"""Shared types for the VECTOR Mini control loop."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class State(Enum):
    IDLE = auto()
    ARMING = auto()
    FLEX = auto()
    HOLD = auto()
    EXTEND = auto()
    RESET = auto()
    E_STOP = auto()


class Command(Enum):
    NONE = auto()
    ARM = auto()
    FLEX = auto()
    HOLD = auto()
    EXTEND = auto()
    RESET = auto()
    E_STOP = auto()


class Fault(Enum):
    NONE = auto()
    WATCHDOG_TIMEOUT = auto()
    POSITION_TIMEOUT = auto()
    POSITION_LIMIT = auto()
    VELOCITY_LIMIT = auto()
    SENSOR_INVALID = auto()
    EXTERNAL_E_STOP = auto()


@dataclass(frozen=True)
class Limits:
    min_position_deg: float = 0.0
    max_position_deg: float = 90.0
    max_velocity_dps: float = 120.0
    max_motor_command: float = 1.0
    movement_timeout_s: float = 5.0
    watchdog_timeout_s: float = 0.150
    reset_tolerance_deg: float = 2.0


@dataclass
class SensorFrame:
    timestamp_s: float
    position_deg: float
    velocity_dps: float
    intent_confidence: float = 0.0
    valid: bool = True


@dataclass
class Telemetry:
    timestamp_s: float
    state: State
    position_deg: float
    target_deg: float
    velocity_dps: float
    motor_command: float
    safety_pass: bool
    fault: Fault
    watchdog_healthy: bool

