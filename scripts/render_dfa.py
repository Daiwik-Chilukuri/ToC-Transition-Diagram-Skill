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
import re
import sys

def sanitize_dom_id(state_id):
    """
    Sanitizes state ID for valid HTML/SVG ID and querySelector safety.
    Example: '(p0, q0)' -> 'p0_q0', '{q0, q1}' -> 'q0_q1', '0%3' -> '0_3'
    """
    cleaned = re.sub(r'[^a-zA-Z0-9_-]', '_', str(state_id))
    cleaned = re.sub(r'_+', '_', cleaned).strip('_')
    return cleaned if cleaned else "state"

def compute_node_radius_and_font(label, user_radius=None):
    """
    Calculates adaptive node radius and font size based on label length.
    Guarantees that composite labels like (p0, q0) and {q0, q1, q2} do not clip.
    """
    lbl_len = len(str(label))
    base_r = int(user_radius) if (user_radius and int(user_radius) > 0) else 26
    
    # Adaptive radius: r = max(base_r, 10 + round(3.0 * len))
    r = max(base_r, int(round(10 + 3.0 * lbl_len)))
    
    # Responsive font sizing
    if lbl_len <= 4:
        font_size = 16.0
    elif lbl_len <= 6:
        font_size = 15.0
    elif lbl_len <= 8:
        font_size = 13.5
    elif lbl_len <= 11:
        font_size = 12.0
    else:
        font_size = max(10.0, 16.0 - 0.5 * (lbl_len - 3))
        
    return r, font_size

def normalize_symbol(sym):
    r"""
    Normalizes transition symbols:
    - Strips whitespace
    - Normalizes LaTeX and text epsilon variants to Unicode Greek small letter epsilon 'ε' (U+03B5).
    - Recognizes: '\\epsilon', r'\epsilon', 'epsilon', 'eps', '\\varepsilon', r'\varepsilon', 'ε'.
    """
    s = str(sym).strip()
    if s in ("\\epsilon", r"\epsilon", "epsilon", "eps", "\\varepsilon", r"\varepsilon", "ε"):
        return "ε"
    return s

def parse_and_normalize_symbols(symbols):
    """
    Parses symbols from a transition entry and normalizes each symbol.
    Handles list of strings, comma-separated string, or single string.
    Returns list of normalized symbol strings.
    """
    if isinstance(symbols, str):
        raw_list = [s.strip() for s in symbols.split(",")]
    elif isinstance(symbols, (list, tuple)):
        raw_list = [str(s).strip() for s in symbols]
    else:
        raw_list = [str(symbols).strip()]
    return [normalize_symbol(s) for s in raw_list if s]


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
        <button id="btnBack" class="btn">Back</button>
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
    let activeStates = new Set();
    let history = [];
    let inputString = "";
    let headPos = 0;
    let isRunning = false;
    let timer = null;
    let traceSteps = [];

    const strInput = document.getElementById("strInput");
    const btnBack = document.getElementById("btnBack");
    const btnStep = document.getElementById("btnStep");
    const btnAuto = document.getElementById("btnAuto");
    const btnReset = document.getElementById("btnReset");
    const tapeDisplay = document.getElementById("tapeDisplay");
    const stepTrace = document.getElementById("stepTrace");
    const statusBadge = document.getElementById("statusBadge");

    function sanitizeId(id) {
      const cleaned = String(id).replace(/[^a-zA-Z0-9_-]/g, '_').replace(/_+/g, '_').replace(/^_+|_+$/g, '');
      return cleaned || 'state';
    }

    function getLabel(id) {
      return (DFA_SPEC.label_map && DFA_SPEC.label_map[id]) || id;
    }

    function formatStateSet(stateSet) {
      if (!stateSet || stateSet.size === 0) return "∅";
      const sorted = Array.from(stateSet).sort();
      if (sorted.length === 1 && DFA_SPEC.type !== "nfa" && DFA_SPEC.type !== "epsilon_nfa") {
        return getLabel(sorted[0]);
      }
      return "{" + sorted.map(id => getLabel(id)).join(", ") + "}";
    }

    function getTransitions(state, symbol) {
      const flatKey = `${state},${symbol}`;
      let targets = undefined;
      if (DFA_SPEC.transition_map) {
        targets = DFA_SPEC.transition_map[flatKey];
        if (targets === undefined && DFA_SPEC.transition_map[state]) {
          targets = DFA_SPEC.transition_map[state][symbol];
        }
      }
      if (targets === undefined || targets === null) return [];
      if (Array.isArray(targets)) return targets;
      return [targets];
    }

    function getEpsilonTargets(state) {
      if (DFA_SPEC.epsilon_map && DFA_SPEC.epsilon_map[state]) {
        return DFA_SPEC.epsilon_map[state];
      }
      const t1 = getTransitions(state, "ε");
      const t2 = getTransitions(state, "\\epsilon");
      const t3 = getTransitions(state, "epsilon");
      return Array.from(new Set([...t1, ...t2, ...t3]));
    }

    function epsilonClosure(stateSet) {
      const closure = new Set(stateSet);
      const queue = Array.from(stateSet);
      while (queue.length > 0) {
        const curr = queue.pop();
        const epsNext = getEpsilonTargets(curr);
        for (const nxt of epsNext) {
          if (!closure.has(nxt)) {
            closure.add(nxt);
            queue.push(nxt);
          }
        }
      }
      return closure;
    }

    function stepSetOnSymbol(currentActiveSet, symbol) {
      const directTargets = new Set();
      for (const q of currentActiveSet) {
        const targets = getTransitions(q, symbol);
        for (const tgt of targets) {
          directTargets.add(tgt);
        }
      }
      return epsilonClosure(directTargets);
    }

    function highlightActiveStates(stateSet) {
      document.querySelectorAll(".node-group").forEach(el => {
        el.classList.remove("active");
      });
      for (const sid of stateSet) {
        const sanitized = sanitizeId(sid);
        const target = document.getElementById("node-" + sanitized);
        if (target) {
          target.classList.add("active");
        }
      }
    }

    function highlightState(stateOrSet) {
      if (stateOrSet instanceof Set) {
        highlightActiveStates(stateOrSet);
      } else if (Array.isArray(stateOrSet)) {
        highlightActiveStates(new Set(stateOrSet));
      } else {
        highlightActiveStates(new Set(stateOrSet ? [stateOrSet] : []));
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

    function updateStatus(stateClass, text) {
      statusBadge.className = `status-badge badge-${stateClass}`;
      statusBadge.textContent = text;
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

      activeStates = epsilonClosure([DFA_SPEC.start_state]);
      currentState = activeStates.size > 0 ? Array.from(activeStates)[0] : null;

      const setStr = formatStateSet(activeStates);
      traceSteps = [`( ${setStr}, "${inputString || "\\u03B5"}" )`];

      highlightActiveStates(activeStates);
      renderTape();

      if (DFA_SPEC.type === "nfa" || DFA_SPEC.type === "epsilon_nfa") {
        updateStatus("ready", `Active: ${setStr}`);
      } else {
        updateStatus("ready", "Ready");
      }
      stepTrace.innerHTML = `Start state: <strong>${setStr}</strong>`;

      history = [{
        activeStates: Array.from(activeStates),
        headPos: 0,
        traceSteps: [...traceSteps],
        statusClass: statusBadge.className,
        statusText: statusBadge.textContent,
        traceHtml: stepTrace.innerHTML
      }];

      if (inputString.length === 0) {
        evaluateFinal();
        history[0].statusClass = statusBadge.className;
        history[0].statusText = statusBadge.textContent;
        history[0].traceHtml = stepTrace.innerHTML;
      }
    }

    function stepSimulation() {
      if (headPos >= inputString.length) {
        evaluateFinal();
        return false;
      }

      const symbol = inputString[headPos];
      const nextActive = stepSetOnSymbol(activeStates, symbol);

      headPos++;
      activeStates = nextActive;
      currentState = activeStates.size > 0 ? Array.from(activeStates)[0] : null;

      highlightActiveStates(activeStates);
      renderTape();

      const remaining = inputString.slice(headPos) || "\\u03B5";
      const setStr = formatStateSet(activeStates);
      traceSteps.push(`( ${setStr}, "${remaining}" )`);
      stepTrace.innerHTML = traceSteps.join(" &vdash; ");

      if (activeStates.size === 0) {
        updateStatus("rejected", "Active: ∅ (Dead)");
        stepTrace.innerHTML += ` &rarr; <span style="color:#f85149; font-weight:bold;">&cross; Stuck / Dead (\\u2205)</span>`;
        if (timer) {
          clearInterval(timer);
          timer = null;
          isRunning = false;
          btnAuto.textContent = "Play";
        }
        history.push({
          activeStates: [],
          headPos: headPos,
          traceSteps: [...traceSteps],
          statusClass: statusBadge.className,
          statusText: statusBadge.textContent,
          traceHtml: stepTrace.innerHTML
        });
        if (headPos >= inputString.length) {
          evaluateFinal();
        }
        return false;
      }

      let statusClass = "running";
      let statusText = (DFA_SPEC.type === "nfa" || DFA_SPEC.type === "epsilon_nfa")
        ? `Active: ${setStr}`
        : `Reading "${inputString[headPos - 1]}"`;
      updateStatus(statusClass, statusText);

      history.push({
        activeStates: Array.from(activeStates),
        headPos: headPos,
        traceSteps: [...traceSteps],
        statusClass: statusBadge.className,
        statusText: statusBadge.textContent,
        traceHtml: stepTrace.innerHTML
      });

      if (headPos >= inputString.length) {
        evaluateFinal();
        const lastIdx = history.length - 1;
        history[lastIdx].statusClass = statusBadge.className;
        history[lastIdx].statusText = statusBadge.textContent;
        history[lastIdx].traceHtml = stepTrace.innerHTML;
        return false;
      }

      return true;
    }

    function stepBackward() {
      if (history.length <= 1) {
        return false;
      }

      if (timer) {
        clearInterval(timer);
        timer = null;
        isRunning = false;
        btnAuto.textContent = "Play";
      }

      history.pop();
      const prev = history[history.length - 1];

      activeStates = new Set(prev.activeStates);
      currentState = activeStates.size > 0 ? Array.from(activeStates)[0] : null;
      headPos = prev.headPos;
      traceSteps = [...prev.traceSteps];

      highlightActiveStates(activeStates);
      renderTape();
      stepTrace.innerHTML = prev.traceHtml;
      statusBadge.className = prev.statusClass;
      statusBadge.textContent = prev.statusText;

      return true;
    }

    function evaluateFinal() {
      const acceptList = DFA_SPEC.accept_states || [];
      const acceptingInSet = Array.from(activeStates).filter(q => acceptList.includes(q));
      const isAccept = acceptingInSet.length > 0;
      const setStr = formatStateSet(activeStates);

      if (isAccept) {
        const acceptLabels = acceptingInSet.map(q => getLabel(q)).join(", ");
        if (DFA_SPEC.type === "nfa" || DFA_SPEC.type === "epsilon_nfa") {
          updateStatus("accepted", `ACCEPTED (${setStr})`);
          stepTrace.innerHTML += ` &rarr; <span style="color:#3fb950; font-weight:bold;">&check; Accepted via ${acceptLabels} in ${setStr}</span>`;
        } else {
          updateStatus("accepted", "ACCEPTED");
          stepTrace.innerHTML += ` &rarr; <span style="color:#3fb950; font-weight:bold;">&check; Accepted in ${setStr}</span>`;
        }
      } else {
        if (DFA_SPEC.type === "nfa" || DFA_SPEC.type === "epsilon_nfa") {
          updateStatus("rejected", `REJECTED (${setStr})`);
          stepTrace.innerHTML += ` &rarr; <span style="color:#f85149; font-weight:bold;">&cross; Rejected in ${setStr}</span>`;
        } else {
          updateStatus("rejected", "REJECTED");
          stepTrace.innerHTML += ` &rarr; <span style="color:#f85149; font-weight:bold;">&cross; Rejected in ${setStr}</span>`;
        }
      }

      if (timer) {
        clearInterval(timer);
        timer = null;
        isRunning = false;
        btnAuto.textContent = "Play";
      }
    }

    if (btnBack) {
      btnBack.addEventListener("click", stepBackward);
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
    - Crisp circular nodes (adaptive radius R >= 26)
    - Double circle for accepting states (inner radius R - 4.5)
    - Free incoming arrow from left for start state
    - Directed quadratic/cubic Bezier curves with stealth arrowheads
    - Clean LaTeX math serif typography
    """
    states = spec.get("states", [])
    transitions = spec.get("transitions", [])
    width = spec.get("width", 800)
    height = spec.get("height", 360)

    # Compute diagram-wide default radius and per-node metrics
    user_radius = spec.get("node_radius", None)
    calculated_radii = [compute_node_radius_and_font(s.get("label", s["id"]), user_radius)[0] for s in states] or [26]
    default_node_radius = max(calculated_radii)

    for s in states:
        lbl = s.get("label", s["id"])
        r_calc, f_calc = compute_node_radius_and_font(lbl, user_radius)
        s["_radius"] = s.get("radius", default_node_radius)
        s["_font_size"] = s.get("font_size", f_calc)

    state_map = {s["id"]: s for s in states}

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

    # Render Transitions
    svg_lines.append('  <!-- Transitions -->')
    svg_lines.append('  <g class="transitions-layer">')

    for t in transitions:
        src_id = t["from"]
        dst_id = t["to"]
        if src_id not in state_map or dst_id not in state_map:
            continue

        src = state_map[src_id]
        dst = state_map[dst_id]
        r_src = src.get("_radius", default_node_radius)
        r_dst = dst.get("_radius", default_node_radius)

        symbols = parse_and_normalize_symbols(t.get("symbols", []))
        sym_str = ", ".join(symbols)

        x1, y1 = src["x"], src["y"]
        x2, y2 = dst["x"], dst["y"]

        if src_id == dst_id:
            # Self-loop
            loop = t.get("loop", "top" if y1 < height / 2 else "bottom")
            r = r_src
            if loop == "top":
                p1_x, p1_y = x1 - 10, y1 - r
                p2_x, p2_y = x1 + 10, y1 - r
                c1_x, c1_y = x1 - 26, y1 - r - 42
                c2_x, c2_y = x1 + 26, y1 - r - 42
                lbl_x, lbl_y = x1, y1 - r - 32
                svg_lines.append(f'    <path d="M {p1_x} {p1_y} C {c1_x} {c1_y}, {c2_x} {c2_y}, {p2_x} {p2_y}" class="trans-edge" />')
                svg_lines.append(f'    <text x="{lbl_x}" y="{lbl_y}" class="trans-label">{sym_str}</text>')
            elif loop == "left":
                p1_x, p1_y = x1 - r, y1 + 10
                p2_x, p2_y = x1 - r, y1 - 10
                c1_x, c1_y = x1 - r - 42, y1 + 26
                c2_x, c2_y = x1 - r - 42, y1 - 26
                lbl_x, lbl_y = x1 - r - 32, y1
                svg_lines.append(f'    <path d="M {p1_x} {p1_y} C {c1_x} {c1_y}, {c2_x} {c2_y}, {p2_x} {p2_y}" class="trans-edge" />')
                svg_lines.append(f'    <text x="{lbl_x}" y="{lbl_y}" class="trans-label">{sym_str}</text>')
            elif loop == "right":
                p1_x, p1_y = x1 + r, y1 - 10
                p2_x, p2_y = x1 + r, y1 + 10
                c1_x, c1_y = x1 + r + 42, y1 - 26
                c2_x, c2_y = x1 + r + 42, y1 + 26
                lbl_x, lbl_y = x1 + r + 32, y1
                svg_lines.append(f'    <path d="M {p1_x} {p1_y} C {c1_x} {c1_y}, {c2_x} {c2_y}, {p2_x} {p2_y}" class="trans-edge" />')
                svg_lines.append(f'    <text x="{lbl_x}" y="{lbl_y}" class="trans-label">{sym_str}</text>')
            else:
                # Default: loop bottom
                p1_x, p1_y = x1 + 10, y1 + r
                p2_x, p2_y = x1 - 10, y1 + r
                c1_x, c1_y = x1 + 26, y1 + r + 42
                c2_x, c2_y = x1 - 26, y1 + r + 42
                lbl_x, lbl_y = x1, y1 + r + 32
                svg_lines.append(f'    <path d="M {p1_x} {p1_y} C {c1_x} {c1_y}, {c2_x} {c2_y}, {p2_x} {p2_y}" class="trans-edge" />')
                svg_lines.append(f'    <text x="{lbl_x}" y="{lbl_y}" class="trans-label">{sym_str}</text>')

        else:
            # Directed edge between distinct nodes
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

            curve = t.get("curve", 0)
            # Automatic curve determination if curve is 0
            if curve == 0:
                # 1. Check for bidirectional edge where both are unbent
                has_reverse = any(other["from"] == dst_id and other["to"] == src_id for other in transitions)
                has_reverse_unbent = any(other["from"] == dst_id and other["to"] == src_id and other.get("curve", 0) == 0 for other in transitions)
                if has_reverse_unbent:
                    curve = 32.0
                elif not has_reverse:
                    # 2. Check for intermediate node collision
                    for sid, other in state_map.items():
                        if sid == src_id or sid == dst_id:
                            continue
                        ox, oy = other["x"], other["y"]
                        pox = ox - x1
                        poy = oy - y1
                        proj = pox * ux + poy * uy
                        if 20 < proj < dist - 20:
                            perp_dist = abs(pox * nx + poy * ny)
                            r_other = other.get("_radius", default_node_radius)
                            if perp_dist < r_other + 15:
                                # Collision detected: curve outward away from center
                                mid_y = (y1 + y2) / 2
                                curve = 65.0 if mid_y >= height / 2 else -65.0
                                break

            # Normalize relative float curvature to pixels
            if 0.0 < abs(curve) <= 1.0:
                curve = curve * dist

            if curve == 0:
                p1_x = x1 + ux * r_src
                p1_y = y1 + uy * r_src
                p2_x = x2 - ux * (r_dst + 1)
                p2_y = y2 - uy * (r_dst + 1)

                lbl_offset = t.get("label_offset", 14)
                lbl_x = (p1_x + p2_x) / 2 + nx * lbl_offset
                lbl_y = (p1_y + p2_y) / 2 + ny * lbl_offset

                svg_lines.append(f'    <line x1="{p1_x:.1f}" y1="{p1_y:.1f}" x2="{p2_x:.1f}" y2="{p2_y:.1f}" class="trans-edge" />')
                svg_lines.append(f'    <text x="{lbl_x:.1f}" y="{lbl_y:.1f}" class="trans-label">{sym_str}</text>')
            else:
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                ctrl_x = mid_x + nx * curve
                ctrl_y = mid_y + ny * curve

                # Start and end intersection with circles
                ang1 = math.atan2(ctrl_y - y1, ctrl_x - x1)
                p1_x = x1 + math.cos(ang1) * r_src
                p1_y = y1 + math.sin(ang1) * r_src

                ang2 = math.atan2(ctrl_y - y2, ctrl_x - x2)
                p2_x = x2 + math.cos(ang2) * (r_dst + 1)
                p2_y = y2 + math.sin(ang2) * (r_dst + 1)

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
        r_s = s.get("_radius", default_node_radius)
        font_size = s.get("_font_size", 16.0)
        is_start = s.get("is_start", False)
        is_accept = s.get("is_accept", False)

        dom_id = "node-" + sanitize_dom_id(sid)
        escaped_sid = str(sid).replace('"', '&quot;')
        svg_lines.append(f'    <g class="node-group" id="{dom_id}" data-state-id="{escaped_sid}">')
        
        # Start state arrow
        if is_start:
            start_x = x - r_s - 26
            target_x = x - r_s - 1
            svg_lines.append(f'      <line x1="{start_x:.1f}" y1="{y}" x2="{target_x:.1f}" y2="{y}" class="start-arrow" />')

        # Outer circle
        svg_lines.append(f'      <circle cx="{x}" cy="{y}" r="{r_s}" class="state-circle" />')

        # Inner circle for accepting state
        if is_accept:
            svg_lines.append(f'      <circle cx="{x}" cy="{y}" r="{r_s - 4.5}" class="state-circle-inner" />')

        # State label with responsive font size
        svg_lines.append(f'      <text x="{x}" y="{y + 0.5}" class="state-label" style="font-size: {font_size}px;">{lbl}</text>')
        svg_lines.append('    </g>')

    svg_lines.append('  </g>')
    svg_lines.append('</svg>')

    return "\n".join(svg_lines)

def build_simulation_data(spec):
    """
    Prepares structured transition, epsilon, and label maps for simulation.
    Supports both DFAs and NFAs (including epsilon-transitions).
    Maps (src, symbol) -> list of target state IDs [dst1, dst2, ...].
    Builds epsilon_map: state_id -> list of epsilon targets [dst1, ...].
    """
    trans_map = {}
    epsilon_map = {}
    label_map = {}

    for s in spec.get("states", []):
        label_map[s["id"]] = s.get("label", s["id"])
        epsilon_map[s["id"]] = []

    for t in spec.get("transitions", []):
        src = t["from"]
        dst_raw = t["to"]
        dst_list = dst_raw if isinstance(dst_raw, list) else [dst_raw]
        symbols = parse_and_normalize_symbols(t.get("symbols", []))

        for s in symbols:
            key = f"{src},{s}"
            if key not in trans_map:
                trans_map[key] = []
            for dst in dst_list:
                if dst not in trans_map[key]:
                    trans_map[key].append(dst)

            if s == "ε":
                if src not in epsilon_map:
                    epsilon_map[src] = []
                for dst in dst_list:
                    if dst not in epsilon_map[src]:
                        epsilon_map[src].append(dst)

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
        "epsilon_map": epsilon_map,
        "label_map": label_map,
        "alphabet": spec.get("alphabet", ["0", "1"]),
        "type": spec.get("type", "dfa")
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
    start_lbl = sim_data["label_map"].get(sim_data["start_state"], sim_data["start_state"] or "q0")

    html = HTML_TEMPLATE
    html = html.replace("__TITLE__", title)
    html = html.replace("__SUBTITLE__", subtitle)
    html = html.replace("__SAMPLE_INPUT__", sample_input)
    html = html.replace("__START_STATE__", start_lbl)
    html = html.replace("__SVG_CONTENT__", svg_content)
    html = html.replace("__DFA_SPEC_JSON__", json.dumps(sim_data))

    os.makedirs(os.path.dirname(os.path.abspath(out_html_path)), exist_ok=True)
    with open(out_html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Successfully generated DFA artifact:\n  HTML: {out_html_path}")
    if out_svg_path:
        print(f"  SVG:  {out_svg_path}")

def apply_grid_layout(spec, rows, cols):
    """Positions states in a clean R x C matrix layout."""
    states = spec.get("states", [])
    if not states:
        return spec

    width = spec.get("width", 840 if cols >= 3 else 800)
    height = spec.get("height", 420 if rows >= 3 else (380 if rows == 2 else 360))
    spec["width"] = width
    spec["height"] = height

    margin_x = 140
    margin_y = 90

    step_x = (width - 2 * margin_x) / (cols - 1) if cols > 1 else 0
    step_y = (height - 2 * margin_y) / (rows - 1) if rows > 1 else 0

    for i, s in enumerate(states):
        if "grid_pos" in s:
            r, c = s["grid_pos"]
        elif "row" in s and "col" in s:
            r, c = s["row"], s["col"]
        else:
            r = i // cols
            c = i % cols

        s["x"] = round(margin_x + c * step_x)
        s["y"] = round(margin_y + r * step_y)

    return spec

def auto_layout(spec, layout_type="linear"):
    """Applies auto coordinates if missing or if layout explicitly specified."""
    states = spec.get("states", [])
    n = len(states)
    if n == 0:
        return spec

    # Check if all states already have coordinates AND layout was not explicitly overridden
    has_coords = all("x" in s and "y" in s for s in states)
    if has_coords and layout_type == "auto":
        return spec

    width = spec.get("width", 800)
    height = spec.get("height", 360)

    # Dynamic R x C grid layout check
    grid_match = re.match(r"^grid_(\d+)x(\d+)$", layout_type)
    if grid_match:
        rows = int(grid_match.group(1))
        cols = int(grid_match.group(2))
        return apply_grid_layout(spec, rows, cols)
    elif layout_type == "grid_2x2":
        return apply_grid_layout(spec, 2, 2)
    elif layout_type == "grid_2x3":
        return apply_grid_layout(spec, 2, 3)
    elif layout_type == "auto" and (spec.get("type") == "product_dfa" or "product_meta" in spec or n == 6):
        if n == 6:
            return apply_grid_layout(spec, 2, 3)
        elif n == 9:
            return apply_grid_layout(spec, 3, 3)
        elif n == 4:
            return apply_grid_layout(spec, 2, 2)

    if layout_type == "circle" or (layout_type == "auto" and n in [3, 5, 7, 8]):
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
    parser.add_argument("--layout", default="auto", help="Layout strategy: auto, linear, circle, grid_2x2, grid_2x3, grid_3x3, grid_RxC")
    args = parser.parse_args()

    with open(args.spec, "r", encoding="utf-8") as f:
        spec = json.load(f)

    spec = auto_layout(spec, args.layout)
    compile_dfa(spec, args.out, args.svg)

if __name__ == "__main__":
    main()
