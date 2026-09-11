"""Integration layer for sensing, control, plant, and safety."""

from __future__ import annotations

from dataclasses import dataclass, field

from .controller import PDController
from .models import Command, Fault, Limits, SensorFrame, State, Telemetry
from .plant import SimulatedJoint
from .safety import SafetyGate
from .state_machine import MotionStateMachine


@dataclass
class VectorMiniSystem:
    limits: Limits = field(default_factory=Limits)
    joint: SimulatedJoint = field(default_factory=SimulatedJoint)
    controller: PDController = field(default_factory=PDController)
    fsm: MotionStateMachine = field(default_factory=MotionStateMachine)
    safety: SafetyGate = field(init=False)
    target_deg: float = 0.0

    def __post_init__(self) -> None:
        self.safety = SafetyGate(self.limits)

    def dispatch(self, command: Command, now_s: float) -> None:
        if command is Command.E_STOP:
            self.safety.trip(Fault.EXTERNAL_E_STOP)
        self.fsm.dispatch(command, now_s)
        if self.fsm.state is State.FLEX:
            self.target_deg = 60.0
        elif self.fsm.state in (State.EXTEND, State.RESET, State.IDLE):
            self.target_deg = self.limits.min_position_deg
        elif self.fsm.state is State.HOLD:
            self.target_deg = self.joint.position_deg

    def step(self, now_s: float, dt_s: float, sensor_delay_s: float = 0.0) -> Telemetry:
        frame = SensorFrame(
            timestamp_s=now_s - sensor_delay_s,
            position_deg=self.joint.position_deg,
            velocity_dps=self.joint.velocity_dps,
        )
        moving = self.fsm.state in (State.FLEX, State.EXTEND, State.RESET)
        fault = self.safety.evaluate(frame, now_s, self.fsm.entered_at_s, moving)
        if fault is not Fault.NONE and self.fsm.state is not State.E_STOP:
            self.fsm.force_estop(now_s)
        requested = self.controller.calculate(
            self.target_deg, frame.position_deg, frame.velocity_dps
        )
        motor = self.safety.command(requested)
        self.joint.step(motor, dt_s)
        watchdog_healthy = now_s - frame.timestamp_s <= self.limits.watchdog_timeout_s
        return Telemetry(
            timestamp_s=now_s,
            state=self.fsm.state,
            position_deg=frame.position_deg,
            target_deg=self.target_deg,
            velocity_dps=frame.velocity_dps,
            motor_command=motor,
            safety_pass=not self.safety.locked,
            fault=self.safety.latched_fault,
            watchdog_healthy=watchdog_healthy,
        )

    def manual_reset(self, now_s: float) -> bool:
        safe = self.safety.manual_reset(self.joint.position_deg)
        if safe:
            self.fsm.manual_reset(now_s, mechanism_safe=True)
            self.target_deg = self.limits.min_position_deg
        return safe

