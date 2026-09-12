#!/usr/bin/env python3
"""
render_dfa.py
Generates clean, academic TikZ-style DFA vector diagrams (SVG) and interactive
HTML string testing simulators.
Zero external dependencies (uses standard library json, math, sys, os, argparse).
"""

import argparse
import json
import math
import os
import sys

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>__TITLE__</title>
  <style>
    :root {
      --bg: #0d1117;
      --card-bg: #161b22;
      --border: #30363d;
      --text: #c9d1d9;
      --text-heading: #f0f6fc;
      --accent: #58a6ff;
      --success: #3fb950;
      --danger: #f85149;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background-color: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
      padding: 24px;
      display: flex;
      flex-direction: column;
      align-items: center;
      min-height: 100vh;
    }
    .container {
      width: 100%;
      max-width: 960px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    .header {
      text-align: center;
    }
    .header h1 {
      color: var(--text-heading);
      font-size: 1.4rem;
      font-weight: 600;
      letter-spacing: 0.5px;
      margin-bottom: 6px;
    }
    .header p {
      color: #8b949e;
      font-size: 0.9rem;
      font-style: italic;
    }
    .canvas-card {
      background: #07090e;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      display: flex;
      justify-content: center;
      align-items: center;
      overflow-x: auto;
      box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    svg.dfa-diagram {
      max-width: 100%;
      height: auto;
      user-select: none;
    }
    .simulator-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 18px 22px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }
    .sim-title {
      font-size: 0.95rem;
      font-weight: 600;
      color: var(--text-heading);
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .sim-controls {
      display: flex;
      gap: 10px;
      align-items: center;
      flex-wrap: wrap;
    }
    .sim-input {
      flex: 1;
      min-width: 200px;
      background: #0d1117;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 8px 12px;
      color: #f0f6fc;
      font-family: "Courier New", monospace;
      font-size: 1rem;
      outline: none;
    }
    .sim-input:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 2px rgba(88, 166, 255, 0.2);
    }
    .btn {
      background: #21262d;
      color: #c9d1d9;
      border: 1px solid var(--border);
      padding: 8px 16px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.9rem;
      font-weight: 500;
      transition: all 0.15s ease;
    }
    .btn:hover {
      background: #30363d;
      color: #fff;
    }
    .btn-primary {
      background: #238636;
      border-color: #2ea043;
      color: #fff;
    }
    .btn-primary:hover {
      background: #2ea043;
    }
    .tape-display {
      display: flex;
      align-items: center;
      gap: 4px;
      min-height: 48px;
      padding: 8px 12px;
      background: #090d13;
      border: 1px solid #21262d;
      border-radius: 6px;
      overflow-x: auto;
    }
    .tape-cell {
      min-width: 34px;
      height: 34px;
      border: 1px solid #30363d;
      border-radius: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: "Courier New", monospace;
      font-weight: bold;
      font-size: 1.1rem;
      color: #8b949e;
      background: #161b22;
      transition: all 0.2s ease;
    }
    .tape-cell.active {
      background: rgba(88, 166, 255, 0.18);
      border-color: var(--accent);
      color: #58a6ff;
      transform: scale(1.08);
    }
    .tape-cell.consumed {
      opacity: 0.45;
      text-decoration: line-through;
    }
    .status-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.9rem;
    }
    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 12px;
      font-weight: 600;
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .badge-ready { background: #21262d; color: #8b949e; }
    .badge-running { background: rgba(88, 166, 255, 0.15); color: #58a6ff; border: 1px solid #58a6ff; }
    .badge-accepted { background: rgba(63, 185, 80, 0.15); color: #3fb950; border: 1px solid #3fb950; }
    .badge-rejected { background: rgba(248, 81, 73, 0.15); color: #f85149; border: 1px solid #f85149; }
    .step-trace {
      font-family: "Courier New", monospace;
      font-size: 0.85rem;
      color: #8b949e;
      word-break: break-all;
    }
    /* SVG Node Active Highlights */
    .node-group {
      cursor: pointer;
      transition: all 0.2s ease;
    }
    .node-group.active circle.state-circle {
      stroke: #58a6ff !important;
      stroke-width: 2.8px !important;
      filter: drop-shadow(0 0 6px rgba(88, 166, 255, 0.7));
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>__TITLE__</h1>
      <p>__SUBTITLE__</p>
    </div>

    <div class="canvas-card">
      __SVG_CONTENT__
    </div>

    <div class="simulator-card">
      <div class="sim-title">
        <span>Interactive String Simulator</span>
      </div>
      <div class="sim-controls">
        <input type="text" id="strInput" class="sim-input" placeholder="Enter input string (e.g. __SAMPLE_INPUT__)" value="__SAMPLE_INPUT__">
        <button id="btnStep" class="btn btn-primary">Step</button>
        <button id="btnAuto" class="btn">Play</button>
        <button id="btnReset" class="btn">Reset</button>
      </div>
      <div class="tape-display" id="tapeDisplay"></div>
      <div class="status-row">
        <div class="step-trace" id="stepTrace">Ready. State: <strong>__START_STATE__</strong></div>
        <div class="status-badge badge-ready" id="statusBadge">Ready</div>
      </div>
    </div>
  </div>

  <script>
    const DFA_SPEC = __DFA_SPEC_JSON__;

    let currentState = DFA_SPEC.start_state;
    let inputString = "";
    let headPos = 0;
    let isRunning = false;
    let timer = null;
    let traceSteps = [];

    const strInput = document.getElementById("strInput");
    const btnStep = document.getElementById("btnStep");
    const btnAuto = document.getElementById("btnAuto");
    const btnReset = document.getElementById("btnReset");
    const tapeDisplay = document.getElementById("tapeDisplay");
    const stepTrace = document.getElementById("stepTrace");
    const statusBadge = document.getElementById("statusBadge");

    function highlightState(stateId) {
      document.querySelectorAll(".node-group").forEach(el => {
        el.classList.remove("active");
      });
      const target = document.getElementById("node-" + stateId);
      if (target) {
        target.classList.add("active");
      }
    }

    function renderTape() {
      tapeDisplay.innerHTML = "";
      if (inputString.length === 0) {
        const emptyCell = document.createElement("div");
        emptyCell.className = "tape-cell active";
        emptyCell.textContent = "\\u03B5"; // epsilon
        tapeDisplay.appendChild(emptyCell);
        return;
      }
      for (let i = 0; i < inputString.length; i++) {
        const cell = document.createElement("div");
        cell.className = "tape-cell";
        cell.textContent = inputString[i];
        if (i < headPos) {
          cell.classList.add("consumed");
        } else if (i === headPos) {
          cell.classList.add("active");
        }
        tapeDisplay.appendChild(cell);
      }
    }

    function resetSimulation() {
      if (timer) {
        clearInterval(timer);
        timer = null;
        isRunning = false;
        btnAuto.textContent = "Play";
      }
      inputString = strInput.value.trim();
      headPos = 0;
      currentState = DFA_SPEC.start_state;
      traceSteps = [`( ${currentState}, "${inputString || "\\u03B5"}" )`];
      highlightState(currentState);
      renderTape();
      updateStatus("ready", "Ready");
      stepTrace.innerHTML = `Start state: <strong>${currentState}</strong>`;
      
      // If string is empty, evaluate immediate acceptance
      if (inputString.length === 0) {
        evaluateFinal();
      }
    }

    function stepSimulation() {
      if (headPos >= inputString.length) {
        evaluateFinal();
        return false;
      }

      const symbol = inputString[headPos];
      const transKey = `${currentState},${symbol}`;
      const nextState = DFA_SPEC.transition_map[transKey];

      if (nextState === undefined) {
        updateStatus("rejected", "No transition for symbol");
        stepTrace.innerHTML += ` &rarr; <strong>Rejected (Undefined)</strong>`;
        if (timer) { clearInterval(timer); timer = null; isRunning = false; btnAuto.textContent = "Play"; }
        return false;
      }

      headPos++;
      currentState = nextState;
      highlightState(currentState);
      renderTape();

      const remaining = inputString.slice(headPos) || "\\u03B5";
      traceSteps.push(`( ${currentState}, "${remaining}" )`);
      stepTrace.innerHTML = traceSteps.join(" &vdash; ");

      if (headPos >= inputString.length) {
        evaluateFinal();
        return false;
      }
      updateStatus("running", `Reading "${inputString[headPos]}"`);
      return true;
    }

    function evaluateFinal() {
      const isAccept = DFA_SPEC.accept_states.includes(currentState);
      if (isAccept) {
        updateStatus("accepted", "ACCEPTED");
        stepTrace.innerHTML += ` &rarr; <span style="color:#3fb950; font-weight:bold;">&check; Accepted in ${currentState}</span>`;
      } else {
        updateStatus("rejected", "REJECTED");
        stepTrace.innerHTML += ` &rarr; <span style="color:#f85149; font-weight:bold;">&cross; Rejected in ${currentState}</span>`;
      }
      if (timer) {
        clearInterval(timer);
        timer = null;
        isRunning = false;
        btnAuto.textContent = "Play";
      }
    }

    function updateStatus(stateClass, text) {
      statusBadge.className = `status-badge badge-${stateClass}`;
      statusBadge.textContent = text;
    }

    btnStep.addEventListener("click", () => {
      if (headPos >= inputString.length && inputString.length > 0) {
        resetSimulation();
      }
      stepSimulation();
    });

    btnAuto.addEventListener("click", () => {
      if (isRunning) {
        clearInterval(timer);
        timer = null;
        isRunning = false;
        btnAuto.textContent = "Play";
      } else {
        if (headPos >= inputString.length && inputString.length > 0) {
          resetSimulation();
        }
        isRunning = true;
        btnAuto.textContent = "Pause";
        timer = setInterval(() => {
          const hasMore = stepSimulation();
          if (!hasMore) {
            clearInterval(timer);
            timer = null;
            isRunning = false;
            btnAuto.textContent = "Play";
          }
        }, 700);
      }
    });

    btnReset.addEventListener("click", resetSimulation);
    strInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        resetSimulation();
      }
    });

    // Initialize on load
    resetSimulation();
  </script>
</body>
</html>
"""

def generate_svg(spec):
    """
    Generates pure SVG matching TikZ academic style:
    - Pure dark background
    - Crisp circular nodes (radius R = 28)
    - Double circle for accepting states (inner radius R - 4.5)
    - Free incoming arrow from left for start state
    - Directed quadratic/cubic Bezier curves with stealth arrowheads
    - Clean LaTeX math serif typography
    """
    states = spec.get("states", [])
    transitions = spec.get("transitions", [])
    width = spec.get("width", 800)
    height = spec.get("height", 360)
    node_radius = 26

    svg_lines = []
    svg_lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" class="dfa-diagram">')
    
    # Defs: Arrowhead markers and font styles
    svg_lines.append('''  <defs>
    <marker id="tikz-arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
      <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#f0f6fc" />
    </marker>
    <style>
      .state-circle { fill: #07090e; stroke: #f0f6fc; stroke-width: 1.6px; }
      .state-circle-inner { fill: none; stroke: #f0f6fc; stroke-width: 1.4px; }
      .state-label {
        font-family: "Computer Modern", "Latin Modern Math", "STIX Two Text", "Times New Roman", serif;
        font-size: 16px;
        fill: #f0f6fc;
        text-anchor: middle;
        dominant-baseline: central;
      }
      .trans-edge {
        fill: none;
        stroke: #f0f6fc;
        stroke-width: 1.4px;
        stroke-linecap: round;
        marker-end: url(#tikz-arrow);
      }
      .trans-label {
        font-family: "Computer Modern", "Latin Modern Math", "STIX Two Text", "Times New Roman", serif;
        font-size: 15px;
        fill: #f0f6fc;
        text-anchor: middle;
        dominant-baseline: central;
        font-style: italic;
        paint-order: stroke fill;
        stroke: #07090e;
        stroke-width: 4px;
        stroke-linejoin: round;
      }
      .start-arrow {
        fill: none;
        stroke: #f0f6fc;
        stroke-width: 1.5px;
        marker-end: url(#tikz-arrow);
      }
    </style>
  </defs>''')

    # State map for coordinates
    state_map = {s["id"]: s for s in states}

    # Render Transitions
    svg_lines.append('  <!-- Transitions -->')
    svg_lines.append('  <g class="transitions-layer">')

    for t in transitions:
        src_id = t["from"]
        dst_id = t["to"]
        symbols = t.get("symbols", [])
        sym_str = ", ".join(symbols) if isinstance(symbols, list) else str(symbols)
        curve = t.get("curve", 0)
        loop = t.get("loop", None)

        if src_id not in state_map or dst_id not in state_map:
            continue

        src = state_map[src_id]
        dst = state_map[dst_id]

        if src_id == dst_id:
            # Self-loop
            x, y = src["x"], src["y"]
            r = node_radius
            if loop == "top":
                p1_x, p1_y = x - 10, y - r
                p2_x, p2_y = x + 10, y - r
                c1_x, c1_y = x - 26, y - r - 42
                c2_x, c2_y = x + 26, y - r - 42
                lbl_x, lbl_y = x, y - r - 32
                svg_lines.append(f'    <path d="M {p1_x} {p1_y} C {c1_x} {c1_y}, {c2_x} {c2_y}, {p2_x} {p2_y}" class="trans-edge" />')
                svg_lines.append(f'    <text x="{lbl_x}" y="{lbl_y}" class="trans-label">{sym_str}</text>')
            elif loop == "left":
                p1_x, p1_y = x - r, y + 10
                p2_x, p2_y = x - r, y - 10
                c1_x, c1_y = x - r - 42, y + 26
                c2_x, c2_y = x - r - 42, y - 26
                lbl_x, lbl_y = x - r - 32, y
                svg_lines.append(f'    <path d="M {p1_x} {p1_y} C {c1_x} {c1_y}, {c2_x} {c2_y}, {p2_x} {p2_y}" class="trans-edge" />')
                svg_lines.append(f'    <text x="{lbl_x}" y="{lbl_y}" class="trans-label">{sym_str}</text>')
            elif loop == "right":
                p1_x, p1_y = x + r, y - 10
                p2_x, p2_y = x + r, y + 10
                c1_x, c1_y = x + r + 42, y - 26
                c2_x, c2_y = x + r + 42, y + 26
                lbl_x, lbl_y = x + r + 32, y
                svg_lines.append(f'    <path d="M {p1_x} {p1_y} C {c1_x} {c1_y}, {c2_x} {c2_y}, {p2_x} {p2_y}" class="trans-edge" />')
                svg_lines.append(f'    <text x="{lbl_x}" y="{lbl_y}" class="trans-label">{sym_str}</text>')
            else:
                # Default: loop bottom
                p1_x, p1_y = x + 10, y + r
                p2_x, p2_y = x - 10, y + r
                c1_x, c1_y = x + 26, y + r + 42
                c2_x, c2_y = x - 26, y + r + 42
                lbl_x, lbl_y = x, y + r + 32
                svg_lines.append(f'    <path d="M {p1_x} {p1_y} C {c1_x} {c1_y}, {c2_x} {c2_y}, {p2_x} {p2_y}" class="trans-edge" />')
                svg_lines.append(f'    <text x="{lbl_x}" y="{lbl_y}" class="trans-label">{sym_str}</text>')

        else:
            # Directed edge between distinct nodes
            x1, y1 = src["x"], src["y"]
            x2, y2 = dst["x"], dst["y"]

            dx = x2 - x1
            dy = y2 - y1
            dist = math.hypot(dx, dy)
            if dist < 1e-4:
                continue

            ux = dx / dist
            uy = dy / dist
            # Normal vector (perpendicular)
            nx = -uy
            ny = ux

            if curve == 0:
                # Straight line from node edge to node edge
                p1_x = x1 + ux * node_radius
                p1_y = y1 + uy * node_radius
                p2_x = x2 - ux * (node_radius + 1)
                p2_y = y2 - uy * (node_radius + 1)

                lbl_offset = t.get("label_offset", 14)
                lbl_x = (p1_x + p2_x) / 2 + nx * lbl_offset
                lbl_y = (p1_y + p2_y) / 2 + ny * lbl_offset

                svg_lines.append(f'    <line x1="{p1_x:.1f}" y1="{p1_y:.1f}" x2="{p2_x:.1f}" y2="{p2_y:.1f}" class="trans-edge" />')
                svg_lines.append(f'    <text x="{lbl_x:.1f}" y="{lbl_y:.1f}" class="trans-label">{sym_str}</text>')
            else:
                # Quadratic Bezier with curvature
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                ctrl_x = mid_x + nx * curve
                ctrl_y = mid_y + ny * curve

                # Start and end intersection with circles
                ang1 = math.atan2(ctrl_y - y1, ctrl_x - x1)
                p1_x = x1 + math.cos(ang1) * node_radius
                p1_y = y1 + math.sin(ang1) * node_radius

                ang2 = math.atan2(ctrl_y - y2, ctrl_x - x2)
                p2_x = x2 + math.cos(ang2) * (node_radius + 1)
                p2_y = y2 + math.sin(ang2) * (node_radius + 1)

                # Point at t=0.5 on quadratic bezier
                curve_mid_x = 0.25 * p1_x + 0.5 * ctrl_x + 0.25 * p2_x
                curve_mid_y = 0.25 * p1_y + 0.5 * ctrl_y + 0.25 * p2_y

                # Push label outside the curve
                offset_dist = t.get("label_offset", 16)
                sign = 1 if curve >= 0 else -1
                lbl_x = curve_mid_x + nx * sign * offset_dist
                lbl_y = curve_mid_y + ny * sign * offset_dist

                svg_lines.append(f'    <path d="M {p1_x:.1f} {p1_y:.1f} Q {ctrl_x:.1f} {ctrl_y:.1f} {p2_x:.1f} {p2_y:.1f}" class="trans-edge" />')
                svg_lines.append(f'    <text x="{lbl_x:.1f}" y="{lbl_y:.1f}" class="trans-label">{sym_str}</text>')

    svg_lines.append('  </g>')

    # Render Nodes
    svg_lines.append('  <!-- States / Nodes -->')
    svg_lines.append('  <g class="nodes-layer">')

    for s in states:
        sid = s["id"]
        lbl = s.get("label", sid)
        x = s["x"]
        y = s["y"]
        is_start = s.get("is_start", False)
        is_accept = s.get("is_accept", False)

        svg_lines.append(f'    <g class="node-group" id="node-{sid}">')
        
        # Start state arrow
        if is_start:
            start_x = x - 52
            target_x = x - node_radius - 1
            svg_lines.append(f'      <line x1="{start_x}" y1="{y}" x2="{target_x}" y2="{y}" class="start-arrow" />')

        # Outer circle
        svg_lines.append(f'      <circle cx="{x}" cy="{y}" r="{node_radius}" class="state-circle" />')

        # Inner circle for accepting state
        if is_accept:
            svg_lines.append(f'      <circle cx="{x}" cy="{y}" r="{node_radius - 4.5}" class="state-circle-inner" />')

        # State label
        svg_lines.append(f'      <text x="{x}" y="{y + 0.5}" class="state-label">{lbl}</text>')
        svg_lines.append('    </g>')

    svg_lines.append('  </g>')
    svg_lines.append('</svg>')

    return "\n".join(svg_lines)

def build_simulation_data(spec):
    """Prepares structured transition map for JS simulation."""
    trans_map = {}
    for t in spec.get("transitions", []):
        src = t["from"]
        dst = t["to"]
        symbols = t.get("symbols", [])
        if isinstance(symbols, str):
            symbols = [s.strip() for s in symbols.split(",")]
        for s in symbols:
            trans_map[f"{src},{s}"] = dst

    start_state = None
    accept_states = []
    for s in spec.get("states", []):
        if s.get("is_start", False) and start_state is None:
            start_state = s["id"]
        if s.get("is_accept", False):
            accept_states.append(s["id"])

    if not start_state and spec.get("states"):
        start_state = spec["states"][0]["id"]

    return {
        "start_state": start_state,
        "accept_states": accept_states,
        "transition_map": trans_map,
        "alphabet": spec.get("alphabet", ["0", "1"])
    }

def compile_dfa(spec, out_html_path, out_svg_path=None):
    """Compiles DFA specification into standalone SVG and interactive HTML."""
    svg_content = generate_svg(spec)
    sim_data = build_simulation_data(spec)

    if out_svg_path:
        os.makedirs(os.path.dirname(os.path.abspath(out_svg_path)), exist_ok=True)
        with open(out_svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

    title = spec.get("title", "Deterministic Finite Automaton")
    subtitle = spec.get("subtitle", "Formal Automata State Diagram")
    sample_input = spec.get("sample_input", "101")

    html = HTML_TEMPLATE
    html = html.replace("__TITLE__", title)
    html = html.replace("__SUBTITLE__", subtitle)
    html = html.replace("__SAMPLE_INPUT__", sample_input)
    html = html.replace("__START_STATE__", sim_data["start_state"] or "q0")
    html = html.replace("__SVG_CONTENT__", svg_content)
    html = html.replace("__DFA_SPEC_JSON__", json.dumps(sim_data))

    os.makedirs(os.path.dirname(os.path.abspath(out_html_path)), exist_ok=True)
    with open(out_html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Successfully generated DFA artifact:\n  HTML: {out_html_path}")
    if out_svg_path:
        print(f"  SVG:  {out_svg_path}")

def auto_layout(spec, layout_type="linear"):
    """Applies auto coordinates if missing."""
    states = spec.get("states", [])
    n = len(states)
    if n == 0:
        return spec

    # Check if all states already have x, y
    if all("x" in s and "y" in s for s in states):
        return spec

    width = spec.get("width", 800)
    height = spec.get("height", 360)

    if layout_type == "circle" or (layout_type == "auto" and n in [3, 5, 6, 7, 8]):
        cx = width / 2
        cy = height / 2 + 10
        radius = min(width, height) * 0.32
        start_angle = math.pi if n == 3 else -math.pi / 2
        for i, s in enumerate(states):
            if n == 3:
                coords = [
                    (cx - 150, cy + 50), # 0%3
                    (cx, cy - 80),       # 1%3
                    (cx + 150, cy + 50)  # 2%3
                ]
                s["x"] = coords[i][0]
                s["y"] = coords[i][1]
            else:
                angle = start_angle + (2 * math.pi * i / n)
                s["x"] = round(cx + radius * math.cos(angle))
                s["y"] = round(cy + radius * math.sin(angle))
    elif layout_type == "grid_2x2":
        cx, cy = width / 2, height / 2
        coords = [
            (cx - 100, cy - 60), # EE
            (cx + 100, cy - 60), # EO
            (cx - 100, cy + 60), # OE
            (cx + 100, cy + 60)  # OO
        ]
        for i, s in enumerate(states):
            if i < len(coords):
                s["x"] = coords[i][0]
                s["y"] = coords[i][1]
    else:
        margin_x = 120
        span_x = width - 2 * margin_x
        step_x = span_x / (n - 1) if n > 1 else 0
        y = height / 2
        for i, s in enumerate(states):
            s["x"] = round(margin_x + i * step_x)
            s["y"] = round(y)

    return spec

def main():
    parser = argparse.ArgumentParser(description="Render academic TikZ-style DFA diagrams")
    parser.add_argument("--spec", required=True, help="Path to DFA JSON specification")
    parser.add_argument("--out", required=True, help="Path for output HTML artifact")
    parser.add_argument("--svg", help="Optional path for output SVG")
    parser.add_argument("--layout", default="auto", choices=["auto", "linear", "circle", "grid_2x2"], help="Layout strategy")
    args = parser.parse_args()

    with open(args.spec, "r", encoding="utf-8") as f:
        spec = json.load(f)

    spec = auto_layout(spec, args.layout)
    compile_dfa(spec, args.out, args.svg)

if __name__ == "__main__":
    main()
