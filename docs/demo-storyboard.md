# The Signal Before Motion — Demonstration Storyboard

## Positioning

This is a **computational research demonstrator**: a working, inspectable model of the proposed system behavior Jaskolka Industries is engineering toward. The public demo uses synthetic sEMG, normalized assistance commands, and a virtual finger response. That evidence-stage label should appear once in the opening frame and remain as a small footer; it should never interrupt the story with a wall of disclaimers.

The demo presents three different ideas clearly:

1. **What works now:** deterministic signal generation, personalized intent estimation, safety gating, virtual stimulation and mechanical-assistance commands, telemetry, fault injection, and automated tests.
2. **What the model shows:** under its stated assumptions, assistance brings the virtual finger closer to the intended movement.
3. **What the research is pursuing:** whether intent-contingent assistance can eventually support motor relearning and taper as voluntary control improves.

Use **reference activation model** and **reduced-recruitment model** rather than “normal person” and “paralyzed person.” Real neuromuscular conditions are individual, and paralysis does not produce one universal waveform.

## Opening frame

**Title:** The Signal Before Motion  
**Subtitle:** Inside the proposed SYNAPSE → VECTOR → KINETIC rehabilitation loop  
**Evidence label:** Computational model · synthetic sEMG · normalized commands · virtual finger response

## 75-second narration and shot plan

| Time | Visual | Narration |
| --- | --- | --- |
| 0–7 s | A finger silhouette; reference sEMG begins to appear | “Every voluntary movement begins before we can see it—as an electrical pattern associated with muscle activation.” |
| 7–16 s | Reference activation and reduced-recruitment traces appear together | “When recruitment is weak, delayed, or disrupted, a person’s attempted movement may produce far less motion than they intended.” |
| 16–26 s | Highlight sensing electrodes and the SYNAPSE acquisition panel | “SYNAPSE is designed to listen for the activity that remains and condition it against that individual’s own calibrated pattern.” |
| 26–37 s | Intent confidence rises and crosses the qualification threshold | “VECTOR evaluates the signal over time, estimates movement intent, and compares that intent with the movement actually produced.” |
| 37–49 s | Contact, placement, signal quality, and timing checks turn green; commands ramp from zero | “When confidence and every safety condition are satisfied, the model authorizes bounded assistance through a virtual neuromuscular-stimulation channel and KINETIC mechanical support.” |
| 49–59 s | Unassisted and hybrid-assisted finger trajectories separate | “In this deterministic run, the unassisted model reaches 20.15 degrees. Hybrid assistance reaches 53.31 degrees and reduces tracking error by 46.3 percent.” |
| 59–67 s | Inject contact loss; both outputs fall to zero and E-stop latches | “If electrode contact, placement, signal quality, or timing fails, AEGIS cuts both assistance paths to zero and latches the emergency stop.” |
| 67–75 s | Architecture returns, followed by the repository and test result | “This is the behavior we can inspect today: a complete signal-to-motion model with 24 automated tests. The next evidence comes from real signal acquisition and instrumented bench validation.” |

## Closing line

> The future we are engineering toward is not movement imposed on a person. It is technology recognizing their intent and helping them complete it.

## On-screen language

Use these labels:

- Reference activation model
- Reduced-recruitment model
- Personalized calibration
- Movement intent confidence
- Safety conditions satisfied
- Virtual stimulation command
- KINETIC assistance command
- Virtual finger response
- Software evidence: 24 tests passing
- Next evidence: instrumented bench validation

Avoid these claims:

- repaired nerve signal;
- proven rehabilitation;
- treatment outcome;
- universal paralysis waveform; or
- replacement for physical therapy.

The vision may be ambitious. The verbs must remain exact: the current system **generates, detects, estimates, authorizes, models, measures, and fails safely**. Future research will **evaluate** whether the complete system can support motor relearning in appropriate users.
