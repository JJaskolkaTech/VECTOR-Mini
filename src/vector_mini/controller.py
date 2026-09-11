"""Bounded proportional-derivative position controller."""

from dataclasses import dataclass


@dataclass
class PDController:
    kp: float = 0.045
    kd: float = 0.010
    deadband_deg: float = 0.35

    def calculate(self, target_deg: float, position_deg: float, velocity_dps: float) -> float:
        error = target_deg - position_deg
        if abs(error) <= self.deadband_deg:
            return 0.0
        return self.kp * error - self.kd * velocity_dps

