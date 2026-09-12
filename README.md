# Theory of Computation (ToC) Transition Diagram Skill & DFA Pipeline

A complete pipeline and agent skill designed for solving, formalizing, and visually rendering **Deterministic Finite Automata (DFA)**, **NFAs**, and **Regular Languages** following rigorous academic lecture standards.

## Key Features

- **Academic TikZ Aesthetic**:
  - Dark mode canvas (`#0d1117` / `#07090e`).
  - Crisp white circular nodes with double circles for final/accepting states ($F$).
  - Directed Bezier curves, self-loops, and free-floating start arrow.
  - Academic math serif typography (Computer Modern / Latin Modern / Times).
- **Interactive String Simulator**:
  - Compiles to standalone interactive HTML.
  - Real-time tape cell tracker with consumed history and head position.
  - Step-by-step playback, auto-play, pause, and live state highlights.
  - Instant acceptance/rejection detection including empty-string ($\epsilon$) evaluation.
- **Strict Mathematical Formalism**:
  - State intuition & invariant definitions.
  - Formal 5-tuple quintuple: $M = (Q, \Sigma, \delta, s, F)$.
  - Complete transition tables.
  - Step-by-step configuration yield proofs: $(q_0, w) \vdash_M^* (q_f, \epsilon)$.
  - DFA completeness and explicit trap/dead state routing.

---

## Repository Structure

```
.
+-- .agents/
¦   +-- skills/
¦       +-- automata-pipeline/
¦           +-- SKILL.md          # Skill definition for AI agents
+-- scripts/
¦   +-- render_dfa.py             # Pure Python vector & HTML generator (no external dependencies)
¦   +-- examples/
¦       +-- decimal_mod3.json     # DFA: Decimal value congruent to 2 mod 3
¦       +-- no_three_bs.json      # DFA: Strings not containing 'bbb'
¦       +-- sum_mod3.json         # DFA: Sum of binary digits congruent to 2 mod 3
+-- specs/
¦   +-- sigma_plus.json           # DFA: Language \Sigma^+ (all non-empty strings)
+-- artifacts/
¦   +-- dfa_sigma_plus.html       # Compiled interactive HTML simulator
¦   +-- dfa_sigma_plus.svg        # Standalone vector SVG diagram
+-- AGENTS.md                     # Agent behavior and visual aesthetic rules
+-- GEMINI.md                     # Gemini rules and guidelines
+-- README.md
```

---

## Quickstart & Usage

### 1. Rendering a DFA Diagram & Simulator

Generate a standalone HTML interactive simulator and an SVG diagram from a JSON specification:

```bash
python scripts/render_dfa.py --spec specs/sigma_plus.json --out artifacts/dfa_sigma_plus.html --svg artifacts/dfa_sigma_plus.svg
```

### 2. Layout Strategies

The renderer supports automated layout calculation:

```bash
# Linear horizontal layout
python scripts/render_dfa.py --spec spec.json --out out.html --layout linear

# Circular layout (ideal for modulo / clock state machines)
python scripts/render_dfa.py --spec spec.json --out out.html --layout circle

# 2x2 Grid (ideal for 2-bit parities like EE, EO, OE, OO)
python scripts/render_dfa.py --spec spec.json --out out.html --layout grid_2x2
```

---

## JSON Specification Format

```json
{
  "title": "Exercise 1.1.15: DFA for \u03a3\u207a",
  "subtitle": "Language L = \u03a3\u207a = {w \u2208 \u03a3* : |w| \u2265 1}",
  "sample_input": "101",
  "alphabet": ["0", "1"],
  "width": 720,
  "height": 340,
  "states": [
    {"id": "q0", "label": "q0", "x": 250, "y": 190, "is_start": true, "is_accept": false},
    {"id": "q1", "label": "q1", "x": 490, "y": 190, "is_start": false, "is_accept": true}
  ],
  "transitions": [
    {"from": "q0", "to": "q1", "symbols": ["0", "1"], "curve": 0, "label_offset": -18},
    {"from": "q1", "to": "q1", "symbols": ["0", "1"], "loop": "top"}
  ]
}
```

---

## License

MIT License.
