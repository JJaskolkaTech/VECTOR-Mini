# VECTOR Mini v0.1.1 Verification Record

**Status:** Portfolio-ready software-in-the-loop release  
**Verification date:** September 12, 2026
**Runtime:** Python standard library, Python 3.10+

## Results

- 24 of 24 automated tests passed across Python 3.10 and 3.12 targets.
- Nominal scenario completed FLEX, HOLD, EXTEND, and RESET without a safety fault.
- Frozen-joint injection latched `POSITION_TIMEOUT` at 5.12 seconds.
- Fault response changed the controller state to `E_STOP` and forced motor command to `0%`.
- Stale-sensor injection latched `WATCHDOG_TIMEOUT` and forced motor command to `0%`.
- Nominal and timeout telemetry were exported to CSV.
- The telemetry visualization was generated successfully as valid SVG.
- Synthetic reference and impaired-pattern sEMG signals were generated repeatably from a fixed seed.
- Personalized intent confidence qualified the impaired-pattern attempt at 1.252 seconds.
- Both virtual stimulation and KINETIC outputs remained zero until intent qualification.
- Virtual contact loss, invalid placement, invalid signal, and external E-stop each latched a fault and forced both outputs to zero.
- The nominal virtual finger model reached 20.15° unassisted and 53.31° with hybrid assistance, reducing modeled tracking RMSE by 46.3%.

## Evidence stage

Version 0.1.1 establishes software architecture, modeled behavior, safety logic, automated testing, telemetry, and documentation. Its evidence comes from synthetic signals, normalized commands, and virtual plant response. The next evidence milestones are hardware-in-the-loop control on a Teensy 4.0, real sEMG acquisition, and instrumented phantom/load testing; biological and clinical questions belong to later supervised studies.

## Re-verification — October 28, 2026

- Full automated suite re-run on the current tree: 24 of 24 tests passed.
- Nominal scenario re-run: completed FLEX, HOLD, EXTEND, and RESET with the safety gate at PASS and no fault.
- Frozen-joint fault injection re-run: POSITION_TIMEOUT latched, controller state E_STOP, motor command forced to 0.0%, safety gate LOCKED.
- No code changes in this entry — a standing re-verification that the published v0.1.1 evidence still reproduces exactly.
