"""Independent, latched safety gate for actuator commands."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .models import Fault, Limits, SensorFrame


@dataclass
class SafetyGate:
    limits: Limits
    latched_fault: Fault = Fault.NONE

    @property
    def locked(self) -> bool:
        return self.latched_fault is not Fault.NONE

    def evaluate(
        self,
        frame: SensorFrame,
        now_s: float,
        movement_started_at_s: float | None,
        moving: bool,
    ) -> Fault:
        if self.locked:
            return self.latched_fault
        values = (frame.timestamp_s, frame.position_deg, frame.velocity_dps)
        if not frame.valid or not all(math.isfinite(value) for value in values):
            return self.trip(Fault.SENSOR_INVALID)
        if now_s - frame.timestamp_s > self.limits.watchdog_timeout_s:
            return self.trip(Fault.WATCHDOG_TIMEOUT)
        if not (self.limits.min_position_deg <= frame.position_deg <= self.limits.max_position_deg):
            return self.trip(Fault.POSITION_LIMIT)
        if abs(frame.velocity_dps) > self.limits.max_velocity_dps:
            return self.trip(Fault.VELOCITY_LIMIT)
        if moving and movement_started_at_s is not None:
            if now_s - movement_started_at_s > self.limits.movement_timeout_s:
                return self.trip(Fault.POSITION_TIMEOUT)
        return Fault.NONE

    def trip(self, fault: Fault) -> Fault:
        if fault is Fault.NONE:
            raise ValueError("cannot latch Fault.NONE")
        if not self.locked:
            self.latched_fault = fault
        return self.latched_fault

    def command(self, requested: float) -> float:
        if self.locked:
            return 0.0
        return max(-self.limits.max_motor_command, min(self.limits.max_motor_command, requested))

    def manual_reset(self, position_deg: float) -> bool:
        safe = abs(position_deg - self.limits.min_position_deg) <= self.limits.reset_tolerance_deg
        if safe:
            self.latched_fault = Fault.NONE
        return safe

