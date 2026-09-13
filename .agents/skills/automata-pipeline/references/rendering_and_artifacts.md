# Visual Artifact Rendering and Specification Guide

This guide establishes the rendering standards, CLI tooling, JSON specification schema, geometric layout algorithms, and response markdown linking rules for creating interactive dark-mode automata simulators.

---

## 1. Visual Rendering Philosophy: The Professor's TikZ Aesthetic
Visual outputs must strictly adhere to the academic dark-mode style:
- **Canvas**: Dark background (`#0d1117` or `#07090e`) with high-contrast elements.
- **States (Nodes)**:
  - Crisp circle stroke in pure white / light gray (`#f0f6fc`), stroke width 2px.
  - Fill in `#161b22` (or transparent/card background).
  - Accepting states: Concentric double circle (outer radius $r$, inner radius $r - 4.5$px).
  - Node radius: Adaptive ($r \ge 26$px) to prevent label clipping on composite IDs.
- **Start Arrow**: Floating incoming arrow from the left, unattached to any source node, labeled with "start" or unlabeled.
- **Transitions (Edges)**:
  - Directed edges with crisp arrowheads (`marker-end`).
  - Straight lines for unidirectional adjacent transitions.
  - Smooth Bezier curves for bidirectional pairs and long jumps.
  - Neat circular self-loops above or below states.
- **Typography**: LaTeX / Computer Modern math serif font (`STIX Two Text`, `Times New Roman`, serif) in `#f0f6fc`.
- **Zero Clutter**: No distracting rainbow colors; semantic colors reserved for simulation states (active state `#58a6ff`, accept badge `#3fb950`, reject badge `#f85149`).


---

## 2. Mandatory Rendering Instructions & CLI Usage

#### Standard CLI Command
```bash
python scripts/render_dfa.py --spec <path_to_spec.json> --out <path_to_artifact.html>
```

#### CLI Options
| Flag | Required | Default | Description |
|---|---|---|---|
| `--spec` | Yes | - | Path to input machine JSON specification file |
| `--out` | Yes | - | Path for output standalone interactive HTML artifact |
| `--svg` | No | None | Optional path to export raw standalone SVG diagram |
| `--layout` | No | `auto` | Layout algorithm: `auto`, `linear`, `circle`, `grid_2x2`, `grid_2x3` |

#### Mandatory Rendering Rules for Closure Operations (Rule R2)
When solving operations on two languages $L_1$ and $L_2$ (Union, Intersection, Set Difference, Symmetric Difference):
1. **Component DFA 1 ($M_1$)**: Render `specs/<problem>_m1.json` $\to$ `artifacts/<problem>_m1.html`.
2. **Component DFA 2 ($M_2$)**: Render `specs/<problem>_m2.json` $\to$ `artifacts/<problem>_m2.html`.
3. **Product DFA ($M_1 \times M_2$)**: Render `specs/<problem>_product.json` $\to$ `artifacts/<problem>_product.html`.
4. **Markdown Response**: All three artifacts must be rendered and explicitly linked in the user response.


---

## 3. Complete JSON Specification Schema Reference

#### Top-Level Schema
```jsonc
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "name": "mod3_zeros",                 // Machine identifier string
  "type": "dfa",                        // "dfa" | "nfa" | "epsilon_nfa" | "product_dfa"
  "title": "DFA: Strings with Number of Zeros Divisible by 3", // Human-readable diagram title
  "subtitle": "L = {w \u2208 {0, 1}* : #0(w) \u2261 0 (mod 3)}", // Subtitle / formal description
  "sample_input": "10010",              // Default string loaded in simulator tape
  "alphabet": ["0", "1"],               // Array of valid symbol strings
  "width": 800,                         // Optional SVG canvas width (default: 800)
  "height": 360,                        // Optional SVG canvas height (default: 360)
  "node_radius": 28,                    // Optional manual node radius override
  "states": [ ... ],                    // Array of State Objects (required)
  "transitions": [ ... ],               // Array of Transition Objects (required)
  "test_cases": [ ... ],                // Array of Test Case Objects (recommended)
  "product_meta": { ... }               // Optional product metadata
}
```

#### State Object Schema
```jsonc
{
  "id": "q0",            // String identifier (e.g. "q0", "(p0, q0)", "{q0, q1}", "0%3")
  "label": "q0",         // Text rendered inside node (e.g. "q0", "(p0, q0)", "0%3")
  "x": 160,              // Optional float X coordinate (calculated by auto_layout if omitted)
  "y": 180,              // Optional float Y coordinate (calculated by auto_layout if omitted)
  "is_start": true,      // Boolean: true if this is the start state s
  "is_accept": true      // Boolean: true if this state is in F
}
```

**State ID DOM Sanitization Rule**:
State IDs may contain parentheses, braces, commas, and percentage signs (e.g. `(p0, q0)`, `{q0, q1}`, `0%3`). To prevent DOM query errors in JavaScript (`document.querySelector`) and invalid XML attributes:
- The SVG element ID is sanitized: `id="node-" + re.sub(r'[^a-zA-Z0-9_-]', '_', state_id)`.
- The display text inside `<text class="state-label">` remains unaltered.
- The simulator tracks state identity via a data attribute: `data-state-id="{state_id}"`.

#### Transition Object Schema
```jsonc
{
  "from": "q0",          // String matching source state id
  "to": "q1",            // String matching target state id
  "symbols": ["0"],      // Array of symbols (or comma-separated string "0, 1")
  "curve": 0.35,         // Optional float curvature bias:
                         //   0.0 = straight line
                         //  >0.0 = counterclockwise arc (curves right relative to direction)
                         //  <0.0 = clockwise arc (curves left relative to direction)
  "label_offset": -14    // Optional float perpendicular pixel offset for text label
}
```

**Symbol Normalization Rule**:
Transition symbols specifying epsilon (e.g. `"\epsilon"`, `"\\epsilon"`, `"eps"`, `"epsilon"`) are automatically normalized to the Unicode Greek letter `ε` (`\u03B5`) during rendering and simulation.

#### Test Case Object Schema
```jsonc
{
  "input": "10010",      // Input string tape
  "expected": true       // Boolean: true if accepted, false if rejected
}
```


---

## 4. Layout Strategies & Geometric Positioning

The renderer provides explicit geometric coordinate generation algorithms for each layout strategy:

#### 1. Linear Layout (`linear`)
- **Use Cases**: Sequential string matchers, substring recognition, counting up to $k$, left-to-right state progressions.
- **Algorithm**:
  - Horizontal margin: `margin_x = 120`
  - Vertical center: `y = height / 2`
  - Step distance: `step_x = (width - 2 * margin_x) / (n - 1)`
  - State $i$ coordinate: $(x_i, y_i) = (\text{margin\_x} + i \cdot \text{step\_x}, y)$
- **Edge Curvature Conventions**:
  - Adjacent forward edge ($i \to i+1$): `curve: 0.0` (straight).
  - Adjacent backward edge ($i+1 \to i$): `curve: 0.35` (below/counterclockwise).
  - Jump edges ($i \to i+k, k \ge 2$): `curve: -0.45` (arched above).
  - Self-loops: Rendered as circular loops placed above the state (`cy - radius - 20`).

#### 2. Circular Layout (`circle`)
- **Use Cases**: Modulo arithmetic ($n \pmod k$), cyclic counters, rotational symmetry.
- **Algorithm**:
  - Center: $(c_x, c_y) = (\text{width}/2, \text{height}/2 + 10)$
  - Circle radius: $R = \min(\text{width}, \text{height}) \times 0.35$
  - Angle for state $i \in \{0, \dots, n-1\}$:
    $$\theta_i = -\frac{\pi}{2} + \frac{2\pi i}{n} \quad \text{(start at 12 o'clock, clockwise)}$$
  - State $i$ coordinate:
    $$x_i = c_x + R \cos\theta_i, \quad y_i = c_y + R \sin\theta_i$$
- **Special 3-State Equilateral Triangle** (for Modulo 3):
  - State $0\%3$: $(c_x - 150, c_y + 60)$ (bottom-left)
  - State $1\%3$: $(c_x, c_y - 90)$ (top-center)
  - State $2\%3$: $(c_x + 150, c_y + 60)$ (bottom-right)

#### 3. $2 \times 2$ Grid Layout (`grid_2x2`)
- **Use Cases**: Parity problems over two independent binary variables (e.g. $EE, EO, OE, OO$).
- **Algorithm**:
  - Center: $(c_x, c_y) = (\text{width}/2, \text{height}/2)$
  - Offsets: $\Delta x = 110$, $\Delta y = 70$
  - States:
    - $q_{0,0} \ (EE)$: $(c_x - \Delta x, c_y - \Delta y)$ (top-left)
    - $q_{0,1} \ (EO)$: $(c_x + \Delta x, c_y - \Delta y)$ (top-right)
    - $q_{1,0} \ (OE)$: $(c_x - \Delta x, c_y + \Delta y)$ (bottom-left)
    - $q_{1,1} \ (OO)$: $(c_x + \Delta x, c_y + \Delta y)$ (bottom-right)

#### 4. Generalized $R \times C$ Product Grid Layout (`grid_2x3`, `grid_3x3`, `grid_RxC`)
- **Use Cases**: Cartesian product DFAs $M_1 \times M_2$ where $|Q_1| = R$ and $|Q_2| = C$ (e.g., Figure 1.10: 2 rows $\times$ 3 cols).
- **Algorithm**:
  - Margin: $\text{margin\_x} = 140, \text{margin\_y} = 80$
  - Step distances:
    $$\text{step\_x} = \frac{\text{width} - 2 \times \text{margin\_x}}{C - 1}, \quad \text{step\_y} = \frac{\text{height} - 2 \times \text{margin\_y}}{R - 1}$$
  - For state $(p_r, q_c)$ at row $r \in \{0, \dots, R-1\}$ and column $c \in \{0, \dots, C-1\}$:
    $$x(r, c) = \text{margin\_x} + c \cdot \text{step\_x}, \quad y(r, c) = \text{margin\_y} + r \cdot \text{step\_y}$$
  - Unreachable states (e.g. $(p_0, q_2)$ and $(p_1, q_0)$ in Figure 1.10) retain their grid positions to preserve Cartesian alignment.

#### 5. Adaptive Node Radius Mathematics
To guarantee zero label clipping for composite labels (e.g. `(p0, q0)`, `{q0, q1, q2}`):
$$r_{\text{adaptive}} = \max\left(26, \left\lfloor\frac{\text{len}(\text{label}) \times \text{font\_size} \times 0.58}{2}\right\rfloor + 10\right)$$
- Length $\le 3$ (`"q0"`): $r = 26$px
- Length 6 (`"(A, C)"`): $r = 30$px
- Length 8 (`"(p0, q0)"`): $r = 34$px
- Length 12 (`"{q0, q1, q2}"`): $r = 42$px


---

## 5. Rules for Linking Artifacts in Markdown Responses

#### Single-DFA Markdown Link Template
```markdown
### Interactive DFA Simulator
The complete formal automaton has been designed and rendered as a standalone interactive simulator:
- **Interactive Simulator**: [Open Interactive DFA Simulator](artifacts/<spec_name>.html)
- **JSON Specification**: `specs/<spec_name>.json`

#### Simulator Instructions:
1. Open `artifacts/<spec_name>.html` in any web browser or IDE preview tab.
2. Enter an input string into the **Input String** field (or click one of the preloaded test cases).
3. Click **Step** to trace the computation symbol by symbol, watching the active state glow and tape advance.
4. Click **Play** for automated animation, or **Reset** to return to start state.
5. The status banner dynamically displays **ACCEPTED** (green) or **REJECTED** (red) upon tape exhaustion.
```

#### Multi-DFA Closure Operations Markdown Link Template
```markdown
### Interactive Automata Simulators
This closure operation includes three interactive visual simulators:
1. **Component DFA $M_1$ ($L_1$)**: [Open $M_1$ Simulator](artifacts/<name>_m1.html) — Recognizes language $L_1$.
2. **Component DFA $M_2$ ($L_2$)**: [Open $M_2$ Simulator](artifacts/<name>_m2.html) — Recognizes language $L_2$.
3. **Product DFA $M = M_1 \times M_2$**: [Open Product Simulator](artifacts/<name>_product.html) — Simulates the combined Cartesian machine recognizing $L_1 \cup L_2$ (or $L_1 \cap L_2$).
```

---
