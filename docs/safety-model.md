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

## Recovery policy

After an E-stop, the mechanism must be manually returned to within 2° of its rest position. Only then may an explicit manual-reset operation clear the fault and return the state machine to `IDLE`. The interrupted movement is never replayed automatically.

## Scope boundary

This repository is an educational software testbed, not a certified medical device or production motor controller. The Teensy scaffold intentionally boots in E-stop and contains no usable motor pin until hardware hazards, wiring, independent power isolation, and physical E-stop behavior are verified.

