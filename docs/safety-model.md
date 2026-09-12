# Safety Model

## Safety objective

No detected fault may leave an actuator command energized. Emergency stops are latched and require deliberate recovery; a normal motion command cannot clear them.

## Implemented hazards and controls

| Hazard | Detection | Response |
| --- | --- | --- |
| Stale sensor data | 150 ms watchdog | Latch `WATCHDOG_TIMEOUT`; command 0% |
| Movement fails to finish | 5 s state timeout | Latch `POSITION_TIMEOUT`; command 0% |
| Joint exceeds travel | 0–90° bounds | Latch `POSITION_LIMIT`; command 0% |
| Excessive speed | 120°/s bound | Latch `VELOCITY_LIMIT`; command 0% |
| Invalid sensor value | validity and finite-number checks | Latch `SENSOR_INVALID`; command 0% |
| Human stop request | external E-stop event | Latch `EXTERNAL_E_STOP`; command 0% |

## Rehabilitation-intent simulation controls

The v0.1.1 lab adds two **virtual** assistance channels. The following checks apply to both, so a fault cannot leave either the normalized stimulation output or KINETIC command active.

| Hazard | Simulation detection | Response |
| --- | --- | --- |
| Weak or ambiguous intent | confidence threshold, dwell, and hysteresis | keep both outputs at zero |
| Invalid sEMG observation | validity and finite-number checks | latch `SIGNAL_INVALID`; zero both outputs |
| Poor virtual electrode contact | normalized contact threshold | latch `ELECTRODE_CONTACT`; zero both outputs |
| Invalid virtual placement | normalized alignment threshold | latch `PLACEMENT_INVALID`; zero both outputs |
| Abrupt dose increase | normalized slew limiter | bound the virtual stimulation ramp |
| Excessive continuous assistance | hard duration limit | latch `ASSIST_TIMEOUT`; zero both outputs |
| Human stop request | external E-stop event | latch `EXTERNAL_E_STOP`; zero both outputs |

Fail-closed shutdown is immediate. The dose ramp applies only while increasing an authorized virtual output; it never slows a safety shutdown.

## Recovery policy

After an E-stop, the mechanism must be manually returned to within 2° of its rest position. Only then may an explicit manual-reset operation clear the fault and return the state machine to `IDLE`. The interrupted movement is never replayed automatically.

## Scope boundary

This repository is an educational software testbed, not a certified medical device, stimulation protocol, or production motor controller. The rehabilitation channel contains no real electrical dose or anatomical placement instructions and cannot communicate with stimulation hardware. The Teensy scaffold intentionally boots in E-stop and contains no usable motor pin until hardware hazards, wiring, independent power isolation, and physical E-stop behavior are verified.
