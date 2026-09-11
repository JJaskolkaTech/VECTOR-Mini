# VECTOR Mini v0.1 Verification Record

**Status:** Portfolio-ready software-in-the-loop release  
**Verification date:** September 11, 2026  
**Runtime:** Python standard library, Python 3.10+

## Results

- 13 of 13 automated tests passed.
- Nominal scenario completed FLEX, HOLD, EXTEND, and RESET without a safety fault.
- Frozen-joint injection latched `POSITION_TIMEOUT` at 5.12 seconds.
- Fault response changed the controller state to `E_STOP` and forced motor command to `0%`.
- Stale-sensor injection latched `WATCHDOG_TIMEOUT` and forced motor command to `0%`.
- Nominal and timeout telemetry were exported to CSV.
- The telemetry visualization was generated successfully as valid SVG.

## Honest scope statement

Version 0.1 proves software architecture, simulation, safety logic, automated testing, telemetry, and documentation. It does not claim physical closed-loop operation. Hardware-in-the-loop control on a Teensy 4.0 is the defined v0.2 milestone.

