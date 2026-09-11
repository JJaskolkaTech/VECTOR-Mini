"""Command-line dashboard and CSV telemetry export."""

from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

from .models import Telemetry
from .scenarios import run_scenario


def dashboard(row: Telemetry) -> str:
    safety = "PASS" if row.safety_pass else "LOCKED"
    watchdog = "HEALTHY" if row.watchdog_healthy else "STALE"
    return (
        "VECTOR MINI — JOINT CONTROL TESTBED\n"
        f"Time:              {row.timestamp_s:6.2f} s\n"
        f"Controller State:  {row.state.name}\n"
        f"Joint Position:    {row.position_deg:6.2f} deg\n"
        f"Target Position:   {row.target_deg:6.2f} deg\n"
        f"Joint Velocity:    {row.velocity_dps:6.2f} deg/s\n"
        f"Motor Command:     {row.motor_command:+6.1%}\n"
        f"Safety Gate:       {safety}\n"
        f"Watchdog:          {watchdog}\n"
        f"Fault:             {row.fault.name}"
    )


def write_csv(path: Path, rows: list[Telemetry]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "timestamp_s", "state", "position_deg", "target_deg",
            "velocity_dps", "motor_command", "safety_pass", "fault",
            "watchdog_healthy",
        ])
        for row in rows:
            writer.writerow([
                f"{row.timestamp_s:.3f}", row.state.name, f"{row.position_deg:.3f}",
                f"{row.target_deg:.3f}", f"{row.velocity_dps:.3f}",
                f"{row.motor_command:.4f}", row.safety_pass, row.fault.name,
                row.watchdog_healthy,
            ])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=("nominal", "timeout", "watchdog"), default="timeout")
    parser.add_argument("--csv", type=Path, help="write full telemetry to this CSV path")
    parser.add_argument("--fast", action="store_true", help="run without real-time delay")
    args = parser.parse_args()

    rows: list[Telemetry] = []
    previous_state = None
    for row in run_scenario(args.scenario):
        rows.append(row)
        if row.state != previous_state or row.fault.name != "NONE":
            print("\n" + dashboard(row))
            previous_state = row.state
        if not args.fast:
            time.sleep(0.02)
    if args.csv:
        write_csv(args.csv, rows)
        print(f"\nTelemetry written to {args.csv}")


if __name__ == "__main__":
    main()

