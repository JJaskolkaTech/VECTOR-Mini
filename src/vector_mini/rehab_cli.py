"""Run the VECTOR Mini synthetic rehabilitation-intent demonstration."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from .rehab import RehabSample, run_rehab_simulation, summarize_rehab


def write_csv(path: Path, rows: list[RehabSample]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "timestamp_s",
                "reference_emg_norm",
                "impaired_emg_norm",
                "reference_envelope",
                "impaired_envelope",
                "intent_confidence",
                "intent_detected",
                "electrode_contact_quality",
                "placement_alignment",
                "dose_request_norm",
                "stimulation_command_norm",
                "kinetic_command_norm",
                "target_angle_deg",
                "unassisted_angle_deg",
                "assisted_angle_deg",
                "safety_state",
                "fault",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    f"{row.timestamp_s:.3f}",
                    f"{row.reference_emg_norm:.6f}",
                    f"{row.impaired_emg_norm:.6f}",
                    f"{row.reference_envelope:.6f}",
                    f"{row.impaired_envelope:.6f}",
                    f"{row.intent_confidence:.6f}",
                    row.intent_detected,
                    f"{row.electrode_contact_quality:.4f}",
                    f"{row.placement_alignment:.4f}",
                    f"{row.dose_request_norm:.6f}",
                    f"{row.stimulation_command_norm:.6f}",
                    f"{row.kinetic_command_norm:.6f}",
                    f"{row.target_angle_deg:.4f}",
                    f"{row.unassisted_angle_deg:.4f}",
                    f"{row.assisted_angle_deg:.4f}",
                    row.safety_state.value,
                    row.fault.value,
                ]
            )


def format_report(rows: list[RehabSample]) -> str:
    summary = summarize_rehab(rows)
    detected = (
        f"{summary.intent_detected_at_s:.3f} s"
        if summary.intent_detected_at_s is not None
        else "NOT DETECTED"
    )
    final = rows[-1]
    ratio = summary.impaired_peak_envelope / summary.reference_peak_envelope
    return (
        "VECTOR MINI — SYNTHETIC REHABILITATION INTENT LAB\n"
        "SIMULATION ONLY · NOT PATIENT DATA · NO HARDWARE OUTPUT\n\n"
        "SYNAPSE / SENSING\n"
        f"  Reference envelope peak:      {summary.reference_peak_envelope:6.3f} norm\n"
        f"  Impaired-pattern peak:        {summary.impaired_peak_envelope:6.3f} norm "
        f"({ratio:4.0%} of reference)\n"
        f"  Virtual electrode contact:    {final.electrode_contact_quality:6.1%}\n"
        f"  Virtual placement alignment:  {final.placement_alignment:6.1%}\n\n"
        "VECTOR / INTERPRETATION\n"
        f"  Intent detected at:           {detected}\n"
        f"  Peak confidence:              {summary.peak_confidence:6.1%}\n"
        f"  Safety state:                 {summary.final_state.value}\n"
        f"  Latched fault:                {summary.final_fault.value}\n\n"
        "VIRTUAL ASSISTANCE / MOVEMENT OUTCOME\n"
        f"  Unassisted peak extension:    {summary.unassisted_peak_deg:6.2f} deg\n"
        f"  Hybrid-assisted extension:    {summary.assisted_peak_deg:6.2f} deg\n"
        f"  Unassisted tracking RMSE:     {summary.unassisted_rmse_deg:6.2f} deg\n"
        f"  Assisted tracking RMSE:       {summary.assisted_rmse_deg:6.2f} deg\n"
        f"  Simulated error reduction:    {summary.tracking_error_reduction_pct:6.1f}%\n\n"
        "Dose and placement values are normalized software variables, not clinical settings."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scenario",
        choices=("nominal", "contact-fault", "signal-fault", "estop"),
        default="nominal",
    )
    parser.add_argument("--csv", type=Path, help="write full telemetry to this CSV path")
    args = parser.parse_args()

    options: dict[str, float] = {}
    if args.scenario == "contact-fault":
        options["contact_drop_at_s"] = 1.80
    elif args.scenario == "signal-fault":
        options["invalid_signal_at_s"] = 1.80
    elif args.scenario == "estop":
        options["external_estop_at_s"] = 1.80

    rows = run_rehab_simulation(**options)
    print(format_report(rows))
    if args.csv:
        write_csv(args.csv, rows)
        print(f"\nTelemetry written to {args.csv}")


if __name__ == "__main__":
    main()
