# Verification Plan

## Automated acceptance criteria

| Test area | Acceptance criterion |
| --- | --- |
| Nominal sequence | Legal states execute without a fault |
| Transition guard | Illegal commands raise `InvalidTransition` |
| E-stop reachability | E-stop is reachable from every operating state |
| Watchdog | A frame older than 150 ms latches a fault |
| Travel and speed limits | Limit violations latch and zero the output |
| Motion timeout | Frozen joint produces `POSITION_TIMEOUT` and 0% output |
| Fault persistence | A later good frame cannot clear a fault |
| Reset | Reset fails away from rest and succeeds within tolerance |
| Output bounds | Requested commands remain in the range -100% to +100% |

Run the entire acceptance suite with:

```bash
make test
```

## Hardware gates for v0.2

- Verify motor power is physically isolated from USB/logic power.
- Add a normally closed physical E-stop path independent of application software.
- Confirm actuator direction with the mechanism unloaded.
- Establish conservative current, speed, force, and travel limits.
- Test every fault with no person wearing or contacting the mechanism.
- Require a witnessed pre-use checklist before any human-adjacent test.

