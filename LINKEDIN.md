# LinkedIn Launch Kit

## Featured-project description

**VECTOR Mini — Safety-First Closed-Loop Motion Controller**

Designed and implemented a software-in-the-loop motion-control testbed for wearable robotics. The Python system combines deterministic state control, a bounded PD controller, simulated joint physics, telemetry, watchdog monitoring, safety interlocks, latched emergency-stop handling, and automated fault-injection tests. A Teensy 4.0 firmware scaffold defines the next embedded milestone.

## Launch post

I’ve been developing VECTOR Mini, a safety-first closed-loop motion-control testbed inspired by the engineering challenges of wearable robotics.

Version 0.1 is a complete Python software-in-the-loop simulation. It models a robotic joint moving through ARMING, FLEX, HOLD, EXTEND, and RESET states while an independent safety gate monitors sensor freshness, position, velocity, and movement time.

The most important part of the demo is not the successful movement—it is the intentional failure. When I freeze the simulated joint, the controller detects a position timeout, latches E-STOP, and forces motor output to zero. The interrupted movement cannot resume until the mechanism is returned to a safe posture and manually reset.

What this version demonstrates:

- Closed-loop control and simulated joint dynamics
- Deterministic finite-state-machine design
- Watchdogs, bounds checking, and fault latching
- Emergency-stop and manual-recovery logic
- Automated verification and CSV telemetry
- A migration path from Python simulation to Teensy 4.0 firmware

This is an independent educational testbed—not production medical hardware—but it represents the way I want to build physical systems: testable, observable, and designed around human safety from the beginning.

#Robotics #EmbeddedSystems #Python #ControlSystems #WearableRobotics #Engineering

## Suggested 45-second video sequence

1. Show the repository README and architecture diagram (5 seconds).
2. Run `make demo` and point out FLEX, HOLD, EXTEND, and IDLE (12 seconds).
3. Run `make fault-demo` and explain that the joint is intentionally frozen (15 seconds).
4. Pause on `POSITION_TIMEOUT`, `E_STOP`, `LOCKED`, and motor command `0%` (8 seconds).
5. End on the passing automated test suite (5 seconds).

