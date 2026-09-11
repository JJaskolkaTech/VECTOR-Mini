"""Repeatable engineering demonstration scenarios."""

from __future__ import annotations

from collections.abc import Iterator

from .models import Command, State, Telemetry
from .system import VectorMiniSystem


def run_scenario(name: str, dt_s: float = 0.02) -> Iterator[Telemetry]:
    system = VectorMiniSystem()
    system.dispatch(Command.ARM, 0.0)
    system.dispatch(Command.FLEX, 0.10)
    now = 0.0
    hold_sent = False
    extend_sent = False
    reset_sent = False

    while now <= 12.0:
        if name == "timeout" and now >= 1.0:
            system.joint.frozen = True
        if name == "watchdog" and now >= 1.0:
            telemetry = system.step(now, dt_s, sensor_delay_s=0.25)
        else:
            telemetry = system.step(now, dt_s)
        yield telemetry

        if name == "nominal":
            if not hold_sent and system.joint.position_deg >= 58.0:
                system.dispatch(Command.HOLD, now)
                hold_sent = True
            elif hold_sent and not extend_sent and now >= 3.0:
                system.dispatch(Command.EXTEND, now)
                extend_sent = True
            elif extend_sent and not reset_sent and system.joint.position_deg <= 2.0:
                system.dispatch(Command.RESET, now)
                reset_sent = True
            elif reset_sent and system.fsm.state is State.RESET:
                system.fsm.dispatch(Command.NONE, now)
                system.fsm.state = State.IDLE
                system.fsm.entered_at_s = now
                break
        elif system.fsm.state is State.E_STOP:
            break
        now = round(now + dt_s, 10)

