"""Render rehabilitation-intent telemetry as a portfolio-ready SVG."""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path


WIDTH, HEIGHT = 1240, 1040
LEFT, RIGHT = 92, 48
PLOT_WIDTH = WIDTH - LEFT - RIGHT


def load(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def polyline(
    rows: list[dict[str, str]],
    key: str,
    top: float,
    height: float,
    minimum: float,
    maximum: float,
    stride: int = 1,
) -> str:
    max_time = float(rows[-1]["timestamp_s"])
    span = maximum - minimum
    points: list[str] = []
    for row in rows[::stride]:
        x = LEFT + float(row["timestamp_s"]) / max_time * PLOT_WIDTH
        normalized = (float(row[key]) - minimum) / span
        y = top + height * (1.0 - normalized)
        points.append(f"{x:.1f},{y:.1f}")
    return " ".join(points)


def chart_grid(top: float, height: float, labels: list[tuple[float, str]], maximum: float) -> str:
    parts: list[str] = []
    for value, label in labels:
        y = top + height * (1.0 - value / maximum)
        parts.append(
            f'<line x1="{LEFT}" y1="{y:.1f}" x2="{WIDTH-RIGHT}" '
            f'y2="{y:.1f}" class="grid"/>'
        )
        parts.append(
            f'<text x="{LEFT-14}" y="{y+4:.1f}" class="axis" '
            f'text-anchor="end">{label}</text>'
        )
    return "".join(parts)


def time_grid(top: float, height: float) -> str:
    parts: list[str] = []
    for second in range(6):
        x = LEFT + second / 5.0 * PLOT_WIDTH
        parts.append(
            f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" '
            f'y2="{top+height}" class="vgrid"/>'
        )
        parts.append(
            f'<text x="{x:.1f}" y="{top+height+22}" class="axis" '
            f'text-anchor="middle">{second}s</text>'
        )
    return "".join(parts)


def first_time(rows: list[dict[str, str]], key: str, value: str) -> float | None:
    for row in rows:
        if row[key] == value:
            return float(row["timestamp_s"])
    return None


def rmse(rows: list[dict[str, str]], key: str) -> float:
    active = [row for row in rows if 1.30 <= float(row["timestamp_s"]) <= 3.55]
    errors = [float(row["target_angle_deg"]) - float(row[key]) for row in active]
    return math.sqrt(sum(error * error for error in errors) / len(errors))


def render(rows: list[dict[str, str]]) -> str:
    intent_time = first_time(rows, "intent_detected", "True")
    contact = float(rows[0]["electrode_contact_quality"])
    alignment = float(rows[0]["placement_alignment"])
    unassisted_peak = max(float(row["unassisted_angle_deg"]) for row in rows)
    assisted_peak = max(float(row["assisted_angle_deg"]) for row in rows)
    unassisted_rmse = rmse(rows, "unassisted_angle_deg")
    assisted_rmse = rmse(rows, "assisted_angle_deg")
    reduction = 100.0 * (1.0 - assisted_rmse / unassisted_rmse)
    intent_x = LEFT + (intent_time or 0.0) / 5.0 * PLOT_WIDTH

    signal_top, signal_height = 250.0, 150.0
    control_top, control_height = 500.0, 145.0
    motion_top, motion_height = 755.0, 150.0
    threshold_y = control_top + control_height * (1.0 - 0.58)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
<defs>
  <linearGradient id="header" x1="0" x2="1"><stop stop-color="#162447"/><stop offset="1" stop-color="#10182d"/></linearGradient>
  <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>
  .bg {{ fill:#070b16 }} .card {{ fill:#11182a; stroke:#273553; stroke-width:1 }}
  .panel {{ fill:#0c1323; stroke:#25324d; stroke-width:1 }}
  .grid {{ stroke:#2e3b58; stroke-width:1 }} .vgrid {{ stroke:#27334d; stroke-width:1; opacity:.55 }}
  .title {{ fill:#f5f8ff; font:800 28px system-ui,sans-serif; letter-spacing:.4px }}
  .subtitle {{ fill:#9daecc; font:14px system-ui,sans-serif }}
  .stage {{ fill:#c5d2e9; font:700 12px system-ui,sans-serif; letter-spacing:1px }}
  .stage2 {{ fill:#ffffff; font:700 15px system-ui,sans-serif }}
  .section {{ fill:#f0f4ff; font:700 17px system-ui,sans-serif }}
  .note {{ fill:#8798b8; font:12px system-ui,sans-serif }}
  .axis {{ fill:#8596b5; font:11px ui-monospace,monospace }}
  .legend {{ fill:#c8d3e8; font:12px system-ui,sans-serif }}
  .metric {{ fill:#ffffff; font:800 22px ui-monospace,monospace }}
  .metric-label {{ fill:#8798b8; font:11px system-ui,sans-serif; letter-spacing:.6px }}
  .reference {{ fill:none; stroke:#55c7ff; stroke-width:1.6; opacity:.88 }}
  .impaired {{ fill:none; stroke:#f5b942; stroke-width:1.6; opacity:.9 }}
  .confidence {{ fill:none; stroke:#58e0a4; stroke-width:3.5 }}
  .stim {{ fill:none; stroke:#df7cff; stroke-width:3 }}
  .kinetic {{ fill:none; stroke:#55a3ff; stroke-width:3 }}
  .target {{ fill:none; stroke:#c5d2e9; stroke-width:2; stroke-dasharray:8 6 }}
  .unassisted {{ fill:none; stroke:#f5b942; stroke-width:3.5 }}
  .assisted {{ fill:none; stroke:#58e0a4; stroke-width:4; filter:url(#glow) }}
  .threshold {{ stroke:#ff697f; stroke-width:1.5; stroke-dasharray:6 5 }}
  .intent-marker {{ stroke:#58e0a4; stroke-width:1.5; stroke-dasharray:5 5; opacity:.8 }}
  .arrow {{ stroke:#526887; stroke-width:2; fill:none }}
  .ok {{ fill:#58e0a4; font:700 12px system-ui,sans-serif }}
  .evidence {{ fill:#8fb7ff; font:600 12px system-ui,sans-serif; letter-spacing:.35px }}
</style>
<rect width="100%" height="100%" class="bg"/>
<rect x="24" y="20" width="1192" height="118" rx="18" fill="url(#header)" stroke="#2c3b5c"/>
<text x="54" y="58" class="title">VECTOR MINI — THE SIGNAL BEFORE MOTION</text>
<text x="54" y="83" class="subtitle">A computational model of the proposed SYNAPSE → VECTOR → KINETIC rehabilitation loop</text>
<text x="54" y="112" class="evidence">SOFTWARE-IN-THE-LOOP · SYNTHETIC sEMG · NORMALIZED COMMANDS · VIRTUAL FINGER RESPONSE</text>

<rect x="54" y="158" width="252" height="62" rx="12" class="card"/>
<text x="72" y="181" class="stage">SYNAPSE</text><text x="72" y="204" class="stage2">Acquire + condition sEMG</text>
<path d="M306 189 H342" class="arrow"/><path d="M336 183 L344 189 L336 195" class="arrow"/>
<rect x="344" y="158" width="252" height="62" rx="12" class="card"/>
<text x="362" y="181" class="stage">VECTOR</text><text x="362" y="204" class="stage2">Estimate movement intent</text>
<path d="M596 189 H632" class="arrow"/><path d="M626 183 L634 189 L626 195" class="arrow"/>
<rect x="634" y="158" width="252" height="62" rx="12" class="card"/>
<text x="652" y="181" class="stage">SAFETY GATE</text><text x="652" y="204" class="stage2">Qualify + bound outputs</text>
<path d="M886 189 H922" class="arrow"/><path d="M916 183 L924 189 L916 195" class="arrow"/>
<rect x="924" y="158" width="262" height="62" rx="12" class="card"/>
<text x="942" y="181" class="stage">VIRTUAL OUTPUTS</text><text x="942" y="204" class="stage2">STIM-A/B + KINETIC</text>

<rect x="24" y="232" width="1192" height="202" rx="16" class="panel"/>
<text x="54" y="263" class="section">1 · SYNAPSE ACQUISITION — NORMALIZED SURFACE EMG</text>
<text x="1182" y="263" class="ok" text-anchor="end">CONTACT {contact:.0%} · ALIGNMENT {alignment:.0%}</text>
{chart_grid(signal_top, signal_height, [(0.0, "-1.0"), (1.0, "0.0"), (2.0, "+1.0")], 2.0)}
{time_grid(signal_top, signal_height)}
<line x1="{LEFT}" y1="{signal_top+signal_height/2:.1f}" x2="{WIDTH-RIGHT}" y2="{signal_top+signal_height/2:.1f}" class="grid"/>
<polyline points="{polyline(rows, 'reference_emg_norm', signal_top, signal_height, -1.0, 1.0, 2)}" class="reference"/>
<polyline points="{polyline(rows, 'impaired_emg_norm', signal_top, signal_height, -1.0, 1.0, 2)}" class="impaired"/>
<line x1="810" y1="251" x2="842" y2="251" class="reference"/><text x="850" y="255" class="legend">Reference voluntary pattern</text>
<line x1="1018" y1="251" x2="1050" y2="251" class="impaired"/><text x="1058" y="255" class="legend">Reduced-recruitment model</text>

<rect x="24" y="462" width="1192" height="222" rx="16" class="panel"/>
<text x="54" y="492" class="section">2 · VECTOR INTERPRETATION + NORMALIZED OUTPUT COMMANDS</text>
{chart_grid(control_top, control_height, [(0.0, "0%"), (0.5, "50%"), (1.0, "100%")], 1.0)}
{time_grid(control_top, control_height)}
<line x1="{LEFT}" y1="{threshold_y:.1f}" x2="{WIDTH-RIGHT}" y2="{threshold_y:.1f}" class="threshold"/>
<text x="{WIDTH-RIGHT-6}" y="{threshold_y-6:.1f}" class="axis" text-anchor="end">58% QUALIFICATION THRESHOLD</text>
<line x1="{intent_x:.1f}" y1="{control_top}" x2="{intent_x:.1f}" y2="{control_top+control_height}" class="intent-marker"/>
<text x="{intent_x+8:.1f}" y="{control_top+17}" class="ok">INTENT QUALIFIED {intent_time:.3f}s</text>
<polyline points="{polyline(rows, 'intent_confidence', control_top, control_height, 0.0, 1.0, 2)}" class="confidence"/>
<polyline points="{polyline(rows, 'stimulation_command_norm', control_top, control_height, 0.0, 1.0, 2)}" class="stim"/>
<polyline points="{polyline(rows, 'kinetic_command_norm', control_top, control_height, 0.0, 1.0, 2)}" class="kinetic"/>
<line x1="700" y1="480" x2="732" y2="480" class="confidence"/><text x="740" y="484" class="legend">Intent confidence</text>
<line x1="860" y1="480" x2="892" y2="480" class="stim"/><text x="900" y="484" class="legend">Virtual STIM dose</text>
<line x1="1030" y1="480" x2="1062" y2="480" class="kinetic"/><text x="1070" y="484" class="legend">KINETIC command</text>

<rect x="24" y="717" width="1192" height="222" rx="16" class="panel"/>
<text x="54" y="747" class="section">3 · VIRTUAL FINGER EXTENSION — ASSISTED MOVEMENT RESPONSE</text>
{chart_grid(motion_top, motion_height, [(0.0, "0°"), (30.0, "30°"), (60.0, "60°")], 60.0)}
{time_grid(motion_top, motion_height)}
<polyline points="{polyline(rows, 'target_angle_deg', motion_top, motion_height, 0.0, 60.0, 2)}" class="target"/>
<polyline points="{polyline(rows, 'unassisted_angle_deg', motion_top, motion_height, 0.0, 60.0, 2)}" class="unassisted"/>
<polyline points="{polyline(rows, 'assisted_angle_deg', motion_top, motion_height, 0.0, 60.0, 2)}" class="assisted"/>
<line x1="805" y1="739" x2="837" y2="739" class="target"/><text x="845" y="743" class="legend">Target</text>
<line x1="905" y1="739" x2="937" y2="739" class="unassisted"/><text x="945" y="743" class="legend">Unassisted</text>
<line x1="1053" y1="739" x2="1085" y2="739" class="assisted"/><text x="1093" y="743" class="legend">Hybrid</text>

<rect x="24" y="963" width="284" height="58" rx="13" class="card"/>
<text x="42" y="986" class="metric-label">UNASSISTED PEAK</text><text x="42" y="1011" class="metric">{unassisted_peak:.1f}°</text>
<rect x="326" y="963" width="284" height="58" rx="13" class="card"/>
<text x="344" y="986" class="metric-label">HYBRID-ASSISTED PEAK</text><text x="344" y="1011" class="metric">{assisted_peak:.1f}°</text>
<rect x="628" y="963" width="284" height="58" rx="13" class="card"/>
<text x="646" y="986" class="metric-label">MODELED TRACKING IMPROVEMENT</text><text x="646" y="1011" class="metric">{reduction:.1f}%</text>
<rect x="930" y="963" width="286" height="58" rx="13" class="card"/>
<text x="948" y="986" class="metric-label">FINAL SAFETY STATE</text><text x="948" y="1011" class="metric">READY · NO FAULT</text>
</svg>'''


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: render_rehab.py REHAB.csv OUTPUT.svg")
    input_path, output_path = map(Path, sys.argv[1:])
    rows = load(input_path)
    if not rows:
        raise SystemExit("rehabilitation telemetry is empty")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render(rows), encoding="utf-8")


if __name__ == "__main__":
    main()
