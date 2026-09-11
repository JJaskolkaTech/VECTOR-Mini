"""Render telemetry CSV files into a dependency-free SVG engineering plot."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


WIDTH, HEIGHT = 1100, 620
LEFT, RIGHT, TOP, BOTTOM = 90, 35, 75, 75
PLOT_W = WIDTH - LEFT - RIGHT
PLOT_H = HEIGHT - TOP - BOTTOM


def load(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def points(rows: list[dict[str, str]], key: str, max_t: float) -> str:
    values = []
    for row in rows:
        x = LEFT + float(row["timestamp_s"]) / max_t * PLOT_W
        y = TOP + (90.0 - float(row[key])) / 90.0 * PLOT_H
        values.append(f"{x:.1f},{y:.1f}")
    return " ".join(values)


def render(nominal: list[dict[str, str]], fault: list[dict[str, str]]) -> str:
    max_t = max(float(row["timestamp_s"]) for row in nominal + fault)
    fault_row = fault[-1]
    fault_x = LEFT + float(fault_row["timestamp_s"]) / max_t * PLOT_W
    grid = []
    for degree in (0, 30, 60, 90):
        y = TOP + (90 - degree) / 90 * PLOT_H
        grid.append(f'<line x1="{LEFT}" y1="{y:.1f}" x2="{WIDTH-RIGHT}" y2="{y:.1f}" class="grid"/>')
        grid.append(f'<text x="{LEFT-18}" y="{y+5:.1f}" class="axis" text-anchor="end">{degree}°</text>')
    for second in range(0, int(max_t) + 1):
        x = LEFT + second / max_t * PLOT_W
        grid.append(f'<line x1="{x:.1f}" y1="{TOP}" x2="{x:.1f}" y2="{HEIGHT-BOTTOM}" class="grid faint"/>')
        grid.append(f'<text x="{x:.1f}" y="{HEIGHT-BOTTOM+28}" class="axis" text-anchor="middle">{second}s</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
<style>
  .bg {{ fill:#0b1020 }} .panel {{ fill:#111a2e; stroke:#263657; stroke-width:1 }}
  .grid {{ stroke:#33415f; stroke-width:1 }} .faint {{ opacity:.45 }}
  .title {{ fill:#f4f7ff; font:700 25px system-ui,sans-serif }}
  .subtitle {{ fill:#9fb0cf; font:14px system-ui,sans-serif }}
  .axis {{ fill:#8fa1c2; font:12px ui-monospace,monospace }}
  .nominal {{ fill:none; stroke:#35d399; stroke-width:4 }}
  .fault {{ fill:none; stroke:#f5b942; stroke-width:4 }}
  .marker {{ stroke:#ff5c75; stroke-width:2; stroke-dasharray:8 6 }}
  .label {{ fill:#f4f7ff; font:600 13px system-ui,sans-serif }}
  .danger {{ fill:#ff5c75; font:700 15px system-ui,sans-serif }}
</style>
<rect width="100%" height="100%" class="bg"/><rect x="20" y="20" width="1060" height="580" rx="16" class="panel"/>
<text x="55" y="52" class="title">VECTOR MINI — CLOSED-LOOP FAULT DEMONSTRATION</text>
<text x="55" y="76" class="subtitle">Nominal recovery compared with an intentionally frozen joint</text>
{''.join(grid)}
<polyline points="{points(nominal, 'position_deg', max_t)}" class="nominal"/>
<polyline points="{points(fault, 'position_deg', max_t)}" class="fault"/>
<line x1="{fault_x:.1f}" y1="{TOP}" x2="{fault_x:.1f}" y2="{HEIGHT-BOTTOM}" class="marker"/>
<text x="{fault_x-10:.1f}" y="{TOP+24}" text-anchor="end" class="danger">E-STOP · POSITION TIMEOUT</text>
<line x1="650" y1="45" x2="690" y2="45" class="nominal"/><text x="700" y="50" class="label">Nominal cycle</text>
<line x1="835" y1="45" x2="875" y2="45" class="fault"/><text x="885" y="50" class="label">Frozen joint</text>
<text x="{LEFT + PLOT_W/2}" y="{HEIGHT-22}" text-anchor="middle" class="axis">TIME</text>
<text x="25" y="{TOP + PLOT_H/2}" transform="rotate(-90 25 {TOP + PLOT_H/2})" text-anchor="middle" class="axis">JOINT POSITION</text>
</svg>'''


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("usage: render_telemetry.py NOMINAL.csv TIMEOUT.csv OUTPUT.svg")
    nominal_path, fault_path, output_path = map(Path, sys.argv[1:])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render(load(nominal_path), load(fault_path)), encoding="utf-8")


if __name__ == "__main__":
    main()

