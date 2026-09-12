# LinkedIn Launch Kit

## Featured-project description

**VECTOR Mini — Safety-First Closed-Loop Motion Controller**

Designed and implemented a software-in-the-loop motion-control testbed for wearable robotics. The Python system combines deterministic state control, a bounded PD controller, virtual joint physics, telemetry, watchdog monitoring, safety interlocks, latched emergency-stop handling, and automated fault-injection tests. A Teensy 4.0 firmware scaffold defines the next embedded milestone.

## Launch post

I’ve been developing VECTOR Mini, a safety-first closed-loop motion-control testbed inspired by the engineering challenges of wearable robotics.

Version 0.1 is a complete Python software-in-the-loop model. It represents a robotic joint moving through ARMING, FLEX, HOLD, EXTEND, and RESET states while an independent safety gate monitors sensor freshness, position, velocity, and movement time.

The most important part of the demo is not the successful movement—it is the intentional failure. When I freeze the virtual joint, the controller detects a position timeout, latches E-STOP, and forces motor output to zero. The interrupted movement cannot resume until the mechanism is returned to a safe posture and manually reset.

What this version demonstrates:

- Closed-loop control and virtual joint dynamics
- Deterministic finite-state-machine design
- Watchdogs, bounds checking, and fault latching
- Emergency-stop and manual-recovery logic
- Automated verification and CSV telemetry
- A migration path from the Python model to Teensy 4.0 firmware

This is an independent educational testbed—not production medical hardware—but it represents the way I want to build physical systems: testable, observable, and designed around human safety from the beginning.

#Robotics #EmbeddedSystems #Python #ControlSystems #WearableRobotics #Engineering

## Suggested 45-second video sequence

1. Show the repository README and architecture diagram (5 seconds).
2. Run `make demo` and point out FLEX, HOLD, EXTEND, and IDLE (12 seconds).
3. Run `make fault-demo` and explain that the joint is intentionally frozen (15 seconds).
4. Pause on `POSITION_TIMEOUT`, `E_STOP`, `LOCKED`, and motor command `0%` (8 seconds).
5. End on the passing automated test suite (5 seconds).

## v0.1.1 rehabilitation-intent follow-up post

Movement begins as an electrical pattern before it becomes visible motion.

I’ve expanded VECTOR Mini with **The Signal Before Motion**, a computational rehabilitation-intent demonstrator that makes the proposed SYNAPSE → VECTOR → KINETIC loop observable and testable.

The demo compares a reference surface-EMG activation model with a weaker, delayed, variable recruitment model. SYNAPSE acquires and conditions the signal. VECTOR uses personalized calibration, an RMS envelope, trend evidence, dwell time, and hysteresis to qualify movement intent.

Once intent is qualified, an independent safety gate can authorize two separately modeled outputs:

- a ramp-limited, normalized virtual NMES/FES channel; and
- a bounded KINETIC mechanical-assistance command.

In the deterministic demonstration, the virtual finger reaches 20.15° unassisted and 53.31° with hybrid assistance, reducing tracking RMSE by 46.3%.

The fault behavior is just as important as the nominal result. Invalid signal data, inadequate virtual electrode contact, invalid virtual placement, excessive assistance duration, or E-stop immediately force both outputs to zero and latch the safety state.

Every waveform and response shown in this release is generated inside the computational model: synthetic sEMG in, normalized commands through the controller, and a virtual finger response out. That gives us a measurable foundation for the next evidence milestone—real sEMG acquisition and instrumented electrode/skin-phantom and electrical-load testing.

The long-term research question is whether pairing a person’s detected movement intent with precisely timed, safety-gated assistance can support motor relearning and allow that assistance to taper as voluntary control improves.

The future I’m engineering toward is not movement imposed on a person. It is technology recognizing their intent and helping them complete it.

#RehabilitationEngineering #Robotics #SurfaceEMG #ControlSystems #EmbeddedSystems #Python #WearableRobotics

## Suggested v0.1.1 video sequence

Use the complete [The Signal Before Motion storyboard](docs/demo-storyboard.md). Its opening frame identifies the evidence stage once, then the narration leads with the human possibility, the working signal-to-motion pipeline, the measured model result, and fail-safe behavior.
