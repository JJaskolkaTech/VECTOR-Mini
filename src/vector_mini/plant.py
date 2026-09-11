"""Simple joint physics used for software-in-the-loop testing."""

from dataclasses import dataclass


@dataclass
class SimulatedJoint:
    position_deg: float = 0.0
    velocity_dps: float = 0.0
    max_acceleration_dps2: float = 280.0
    damping: float = 5.0
    frozen: bool = False

    def step(self, motor_command: float, dt_s: float) -> None:
        if self.frozen:
            self.velocity_dps = 0.0
            return
        acceleration = (
            motor_command * self.max_acceleration_dps2
            - self.damping * self.velocity_dps
        )
        self.velocity_dps += acceleration * dt_s
        self.position_deg += self.velocity_dps * dt_s

