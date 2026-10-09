# Theory of Computation (ToC) Automata Pipeline & DFA/NFA Visual Toolkit

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Dependencies: Zero](https://img.shields.io/badge/Dependencies-Zero%20(Stdlib%20Only)-brightgreen.svg?style=flat-square)](scripts/render_automaton.py)
[![Theory: Formal Automata](https://img.shields.io/badge/Theory-Formal%20Automata%20%26%20Proofs-purple.svg?style=flat-square)](.agents/skills/automata-pipeline/references/dfa_formalism_and_proofs.md)
[![Aesthetic: Dark-Mode TikZ](https://img.shields.io/badge/Aesthetic-Academic%20Dark--Mode%20TikZ-0d1117.svg?style=flat-square)](scripts/render_automaton.py)
[![Automated Tests: 100% Passed](https://img.shields.io/badge/Tests-100%25%20Passed-brightgreen.svg?style=flat-square)](scripts/test_pipeline.py)

A modular formal automata toolkit and AI agent skill for **DFA**, **NFA**, **$\epsilon$-NFA**, **product automata**, **regular expressions**, and **pumping-lemma/nonregularity proofs**, with academic diagrams and interactive machine simulators.

The skill incorporates Chapter 1 of the supplied `regular_Sept_30.pdf`, including ε-union, concatenation, star, reversal, regex conversions in both directions, the lecture's numbered-state recurrence, and pumping proofs. The [lecture context](.agents/skills/automata-pipeline/references/lecture_context.md) maps sections and exercises and records apparent formula corrections. The source PDF is not bundled; these references are self-contained summaries.

For practice, request a topic or exercise number. The [practice workflow](.agents/skills/automata-pipeline/references/practice_workflow.md) supports one exercise at a time, incremental hints, and checking an attempt before revealing a full solution. Nonregularity proofs use proof guidance rather than a recognizing simulator.

---

## Table of Contents

- [Architectural & Visual Showcase](#architectural--visual-showcase)
  - [Academic Dark-Mode TikZ Aesthetic](#academic-dark-mode-tikz-aesthetic)
  - [Interactive String Tape Simulator](#interactive-string-tape-simulator)
- [Core Automata Workflows](#core-automata-workflows)
  - [Workflow 1: Single DFA Formal Design & Interactive Rendering](#workflow-1-single-dfa-formal-design--interactive-rendering)
  - [Workflow 2: Multi-DFA Cartesian Product Construction ($M_1 \times M_2$)](#workflow-2-multi-dfa-cartesian-product-construction-m_1-times-m_2)
  - [Workflow 3: NFA & Powerset Subset Construction (Theorem 1.2.1)](#workflow-3-nfa--powerset-subset-construction-theorem-121)
- [Skill Hierarchy & Agent Architecture](#skill-hierarchy--agent-architecture)
  - [Master Entrypoint Router](#master-entrypoint-router)
  - [Modular Reference Library](#modular-reference-library)
- [Quickstart CLI Reference](#quickstart-cli-reference)
  - [Vector Diagram & HTML Simulator Compilation (`render_automaton.py`)](#vector-diagram--html-simulator-compilation-render_automatonpy)
  - [Automated Verification Harness (`test_pipeline.py`)](#automated-verification-harness-test_pipelinepy)
- [Specification Schema Reference](#specification-schema-reference)
  - [Interface Contract](#interface-contract)
  - [Canonical JSON Specification Example](#canonical-json-specification-example)
- [Repository Structure](#repository-structure)
- [Verification & Quality Assurance](#verification--quality-assurance)
- [License](#license)

---

## Architectural & Visual Showcase

The toolkit bridges rigorous mathematical automata theory with modern interactive web visualization, requiring **zero external Python libraries** and compiling self-contained, offline-first artifacts.

```
       +-----------------------------------------------------------+
       |                 JSON Specification                        |
       |     States, Transitions (with ε), Invariants, Tests       |
       +-----------------------------------------------------------+
                                     |
                                     v
       +-----------------------------------------------------------+
       |            render_automaton.py Layout & Render Engine           |
       |   - Adaptive Radius r = max(26, 10 + 3*len)               |
       |   - Responsive Font Sizing (Zero Label Clipping)          |
       |   - Generalized R x C Grid & Circular Topology            |
       |   - LaTeX Normalization (\epsilon -> ε)                   |
       |   - DOM ID Sanitization & SVG Geometry Compiler           |
       +-----------------------------------------------------------+
                        /                         \
                       v                           v
+-----------------------------+     +-------------------------------+
|     Vector SVG Diagram      |     |  Standalone HTML Simulator    |
| - Pure Dark-Mode TikZ Style |     | - Real-Time Tape Head Display |
| - Double Accepting Circles  |     | - Bi-Directional Step Engine  |
| - Cubic Bezier Arcs & Loops |     | - Active-State Set Tracking   |
| - LaTeX Serif Typography    |     | - Instant Formal Yield Trace  |
+-----------------------------+     +-------------------------------+
```

### Academic Dark-Mode TikZ Aesthetic
- **Canvas Environment**: Deep matte dark canvas (`#0d1117` / `#07090e`) engineered for readability and high contrast.
- **Node Geometry**: Crisp circular contours (`#f0f6fc`) over dark card backings (`#161b22`). Final and accepting states ($F$) render with strict **concentric double circles**.
- **Adaptive Sizing Engine**: Node radii dynamically scale ($r = \max(26, 10 + \text{round}(3.0 \times |\text{label}|))$) alongside responsive font scaling to prevent label clipping on composite states such as `(p0, q0)` or `{q0, q1, q2}`.
- **Directed Bezier Transitions**: Forward and backward arcs between state pairs are rendered with symmetrically curved cubic Bezier splines. Orthogonal self-loops cleanly emerge from designated perimeter cardinals (`top`, `bottom`, `left`, `right`).
- **Typography**: Academic math serif styling (`STIX Two Text`, `Latin Modern`, `Computer Modern`, serif) with clean grouping for multi-symbol alphabets (`0, 1` or `a, b`).

### Interactive String Tape Simulator
- **Zero-Dependency Single-File Artifact**: Every HTML simulator embeds the complete CSS, SVG diagram, and pure JavaScript execution engine into a single file with zero external CDN dependencies.
- **Bi-Directional Execution Controls**: Forward single-stepping (`Step`), full backwards history rewind (`Back`), auto-play with adjustable speed, pause, and instantaneous reset.
- **Real-Time Tape Visualization**: Interactive tape cell tracker distinguishing consumed historical symbols from upcoming tape symbols, highlighting the active read head.
- **Active-State Set Tracking ($S \subseteq Q$)**: Full support for both deterministic scalar states ($q \in Q$) and non-deterministic active sets ($S \subseteq Q$) with live multi-state SVG glow highlights (`#58a6ff` active, `#3fb950` accepted, `#f85149` rejected).
- **Formal Configuration Trace**: Step-by-step mathematical yield derivations displayed in real time:
  $$(s, w) \vdash_M (q_1, w') \vdash_M \dots \vdash_M (q_f, \epsilon)$$

---

## Core Automata Workflows

### Workflow 1: Single DFA Formal Design & Interactive Rendering

Every single DFA solution must satisfy the **5-part academic lecture standard**:

1. **State Intuition & Invariants**: Explicit formal operational meaning $I(q)$ for every state $q \in Q$.
   $$\forall w \in \Sigma^*, \quad \hat{\delta}(s, w) = q \iff P(w)$$
2. **Visual Diagram Artifact Link**: Direct relative link to the compiled interactive HTML simulator.
3. **Formal Mathematical Quintuple**: Explicit 5-tuple:
   $$M = (Q, \Sigma, \delta, s, F)$$
4. **Complete Transition Table**: Total tabular representation of $\delta: Q \times \Sigma \to Q$.
5. **Step-by-Step Configuration Traces**: Formal configuration yield derivations for accepted and rejected words:
   $$(s, w) \vdash_M^* (q, \epsilon)$$

#### DFA Totality & Dead State Rigor
- **Completeness**: The transition function $\delta$ must be total. Partial transitions are strictly forbidden.
- **Trap States**: Any path leading to permanent rejection must transition to an explicit trap state ($R$, $q_{\text{trap}}$, or $\emptyset$) with self-loops on all symbols:
  $$\forall \sigma \in \Sigma, \quad \delta(R, \sigma) = R$$

#### Compilation Command:
```bash
python scripts/render_automaton.py --spec specs/decimal_mod4.json --out artifacts/dfa_decimal_mod4.html --svg artifacts/dfa_decimal_mod4.svg
```

---

### Workflow 2: Multi-DFA Cartesian Product Construction ($M_1 \times M_2$)

When establishing the closure of regular languages under Boolean operations (Union, Intersection, Complement, Set Difference, Symmetric Difference), the toolkit constructs the Cartesian product machine:

$$M = M_1 \times M_2 = (Q_1 \times Q_2, \Sigma, \delta, (s_1, s_2), F_{\text{op}})$$

where joint transitions process input symbols simultaneously across both coordinate machines:
$$\delta((p, q), \sigma) = (\delta_1(p, \sigma), \delta_2(q, \sigma))$$

#### The 5 Regular Closure Criteria:
| Operation | Language Property | Accepting State Formulation $F_{\text{op}}$ | Lecture Reference |
|---|---|---|---|
| **Union** | $L(M_1) \cup L(M_2)$ | $F_\cup = (F_1 \times Q_2) \cup (Q_1 \times F_2)$ | Theorem 1.1.8 |
| **Intersection** | $L(M_1) \cap L(M_2)$ | $F_\cap = F_1 \times F_2$ | Theorem 1.1.9 |
| **Complement** | $\overline{L(M_1)}$ | $F_{\text{comp}} = Q_1 \setminus F_1$ | Proposition 1.1.7 |
| **Set Difference** | $L(M_1) \setminus L(M_2)$ | $F_\setminus = F_1 \times (Q_2 \setminus F_2)$ | Corollary 1.1.10 |
| **Symmetric Difference** | $L(M_1) \Delta L(M_2)$ | $F_\Delta = (F_1 \times \overline{F_2}) \cup (\overline{F_1} \times F_2)$ | Exercise 1.1.11 |

#### Product-construction artifacts:
For binary Boolean operations using a product DFA, generate and link **three interactive HTML artifacts**:
1. **Component DFA $M_1$**: `artifacts/<problem>_m1.html`
2. **Component DFA $M_2$**: `artifacts/<problem>_m2.html`
3. **Combined Product DFA $M_1 \times M_2$**: `artifacts/<problem>_product.html`

For ε-NFA union or concatenation, use two component NFAs and their combined ε-NFA instead. Star and reversal are unary transformations; complement requires one complete DFA. The skill preserves the construction method requested in the exercise.

#### Canonical Figure 1.10 Walkthrough:
- $M_1$: Accepts binary strings containing at least one `'1'` ($Q_1 = \{p_0, p_1\}$, $s_1 = p_0$, $F_1 = \{p_1\}$).
- $M_2$: Accepts binary strings starting with `'0'` ($Q_2 = \{q_0, q_1, q_2\}$, $s_2 = q_0$, $F_2 = \{q_1\}$).
- Product Machine $M_1 \times M_2$: 6 composite states arranged on an automated $2 \times 3$ grid (`grid_2x3`):
  $$Q = \{(p_0, q_0), (p_0, q_1), (p_0, q_2), (p_1, q_0), (p_1, q_1), (p_1, q_2)\}$$

```bash
# Render component M1
python scripts/render_automaton.py --spec specs/fig1_10_m1.json --out artifacts/fig1_10_m1.html

# Render component M2
python scripts/render_automaton.py --spec specs/fig1_10_m2.json --out artifacts/fig1_10_m2.html

# Render combined Cartesian product DFA (2x3 grid)
python scripts/render_automaton.py --spec specs/fig1_10_union.json --out artifacts/fig1_10_union.html --layout grid_2x3
```

---

### Workflow 3: NFA & Powerset Subset Construction (Theorem 1.2.1)

#### Formal NFA Definition
A Non-Deterministic Finite Automaton (NFA) with $\epsilon$-transitions is formalized as:
$$N = (Q, \Sigma, \delta, s, F)$$
where the transition function maps states and alphabet symbols (including $\epsilon$) to sets of destination states:
$$\delta: Q \times (\Sigma \cup \{\epsilon\}) \to \mathcal{P}(Q)$$

#### $\epsilon$-Closure Computation
For any state $q \in Q$, its $\epsilon$-closure $E(q)$ is the set of all states reachable from $q$ via zero or more $\epsilon$-transitions:
$$E(q) = \{p \in Q : (q, \epsilon) \vdash_N^* (p, \epsilon)\}$$
For a subset $P \subseteq Q$, $E(P) = \bigcup_{q \in P} E(q)$.

#### Powerset Construction Algorithm (Theorem 1.2.1)
The equivalent deterministic finite automaton $M' = (Q', \Sigma, \delta', s', F')$ is constructed as follows:
1. **Deterministic Start State**:
   $$s' = E(s)$$
2. **Transition Function**: For any subset $P \subseteq Q$ and symbol $\sigma \in \Sigma$:
   $$\delta'(P, \sigma) = \bigcup_{p \in P} \bigcup_{r \in \delta(p, \sigma)} E(r)$$
3. **Accepting States**: Any subset containing at least one original accepting state:
   $$F' = \{P \subseteq Q : P \cap F \neq \emptyset\}$$
4. **Lazy Exploration & Dead State Elimination**: Generate only states reachable from $s'$. If $\delta'(P, \sigma) = \emptyset$, route to the explicit dead state $\emptyset$ (`id: "empty"`, `label: "∅"`).

#### Lecture Benchmark Automata:
- **Figure 1.11 (p. 13 & 16)**: NFA for $L = \{aba, ab\}^*$ with nondeterministic branching on symbol `'b'`, and its 5-state determinized DFA.
- **Figure 1.12 (p. 14 & 17)**: $\epsilon$-NFA accepting strings containing substrings `'101'` or `'11'` with $\delta(q_1, \epsilon) = \{q_2\}$, and its 6-state determinized DFA.
- **Figure 1.14 (p. 19-23)**: NFA regular operations (Union, Concatenation, Kleene Star, and Reversal via Theorem 1.2.3).

#### Interactive NFA Powerset Simulator:
When simulating NFAs, the embedded simulator tracks the live **active state set** $S \subseteq Q$:
- Initial state set: $S_0 = E(s)$.
- On input symbol $\sigma$: $S_{i+1} = \bigcup_{q \in S_i} E(\delta(q, \sigma))$.
- The SVG diagram simultaneously illuminates all states in $S$ with dynamic active badges (`Active: {q0, q1}`).
- Final verdict is **ACCEPTED** if and only if $S \cap F \neq \emptyset$.

```bash
# Render NFA with epsilon transitions and multi-target branching
python scripts/render_automaton.py --spec specs/fig1_12_epsilon_nfa.json --out artifacts/fig1_12_epsilon_nfa.html --svg artifacts/fig1_12_epsilon_nfa.svg

# Render equivalent determinized DFA
python scripts/render_automaton.py --spec specs/fig1_12_dfa_converted.json --out artifacts/fig1_12_dfa_converted.html --svg artifacts/fig1_12_dfa_converted.svg
```

---

## Skill Hierarchy & Agent Architecture

The repository acts as a specialized AI agent skill under `.agents/skills/automata-pipeline/`. It employs a clean, two-layer architecture separating workflow routing from specialized mathematical reference manuals.

```
.agents/skills/automata-pipeline/
├── SKILL.md                                 # Master Router & Execution Protocols (< 120 lines)
└── references/                              # Modular Theoretical Reference Manuals
    ├── closure_and_product_construction.md  # Cartesian products, 5 closure criteria, Fig 1.10
    ├── nfa_and_epsilon_transitions.md       # NFA quintuple, ε-closure, regular operations
    ├── subset_construction.md               # Theorem 1.2.1 determinization, reachability, Fig 1.11 & 1.12
    ├── dfa_formalism_and_proofs.md          # 5-part standard, invariants, inductive proofs
    ├── rendering_and_artifacts.md           # Visual aesthetic rules, JSON schema, layouts
    ├── regular_expressions.md               # Semantics, identities, regex ↔ automata
    ├── pumping_lemma_and_nonregularity.md    # Quantifiers, witnesses, closure reductions
    ├── practice_workflow.md                 # Exercises, incremental hints, answer checking
    └── lecture_context.md                  # PDF sections, exercise map, corrections
```

### Master Entrypoint Router (`SKILL.md`)
- Maintains a compact footprint (< 120 lines).
- Implements the Master Routing Table mapping tasks directly to reference guides.
- Applies the five-part format to full machine solutions, preserves the requested closure method, and routes regex answers, nonregularity proofs, and guided practice to their appropriate formats.

### Modular Reference Library
1. **`closure_and_product_construction.md`**: Complete Cartesian state space formulations, Boolean closure accepting sets ($F_\cup, F_\cap, F_{\text{comp}}, F_\setminus, F_\Delta$), Figure 1.10 walkthrough.
2. **`nfa_and_epsilon_transitions.md`**: Non-deterministic transition relations, computation trees, $\epsilon$-closure fixpoints, regular operations constructions (Union, Concatenation, Kleene Star, Reversal).
3. **`subset_construction.md`**: Formal powerset determinization algorithm (Theorem 1.2.1), lazy state reachability, empty subset trap state routing, step-by-step conversions for Figures 1.11 and 1.12.
4. **`dfa_formalism_and_proofs.md`**: Invariant definition templates, induction on string length $|w|$, configuration yield relations $(s, w) \vdash_M^* (q, \epsilon)$.
5. **`rendering_and_artifacts.md`**: TikZ visual rules, RGB color variables, DOM ID sanitization, dynamic $R \times C$ product grid calculations, markdown linking conventions.
6. **`regular_expressions.md`**: Academic regex syntax and precedence, identities, structural regex → ε-NFA → DFA, DFA → regex recurrence, and GNFA alternative.
7. **`pumping_lemma_and_nonregularity.md`**: Quantifier order, arbitrary decompositions, worked witnesses, and closure reductions.
8. **`practice_workflow.md`**: One-at-a-time exercises, progressive hints, and checking equivalent answers.
9. **`lecture_context.md`**: Source page map, exercise anchors, notation, and corrections.

### ε-construction examples

The renderer accepts machine JSON; it does not parse raw regex or automatically perform conversions. New fixtures include `concat_epsilon.json`, `star_incoming_start.json`, `reverse_epsilon.json`, and `regex_optional_a_b_star.json`. Each contains all 63 words over `{a,b}` through length five as independent membership checks. The existing `fig1_14_regular_ops.json` supplies ε-union.

```bash
python scripts/render_automaton.py --spec scripts/examples/regex_optional_a_b_star.json --out artifacts/regex_optional_a_b_star.html --svg artifacts/regex_optional_a_b_star.svg
python scripts/test_pipeline.py
```

---

## Quickstart CLI Reference

### Vector Diagram & HTML Simulator Compilation (`render_automaton.py`)

The renderer operates strictly via standard library Python (3.10+) with zero external package installations.

```bash
python scripts/render_automaton.py --spec <spec.json> --out <artifact.html> [--svg <diagram.svg>] [--layout <strategy>]
```

The canonical Python API is `compile_automaton(spec, out_html_path, out_svg_path=None)` in `scripts/render_automaton.py`. Existing `python scripts/render_dfa.py ...` commands and `from render_dfa import compile_dfa` imports remain supported by a thin compatibility wrapper. New integrations should use the automaton names. DFA-specific machine types, filenames for determinized examples, and theory references retain their meaningful DFA names.

#### Command-Line Arguments:
| Flag | Type | Required | Description |
|---|---|:---:|---|
| `--spec` | Path | **Yes** | Path to the machine JSON specification file |
| `--out` | Path | **Yes** | Output destination path for the standalone HTML simulator |
| `--svg` | Path | No | Optional destination path to export raw standalone SVG vector diagram |
| `--layout` | String | No | Layout strategy: `auto` (default), `linear`, `circle`, `grid_2x2`, `grid_2x3`, `grid_3x3`, `grid_RxC` |

#### Layout Strategies:
- `auto`: Automatically selects grid layout for product DFAs (e.g. 6 states -> `grid_2x3`, 4 states -> `grid_2x2`), circular layout for 3, 5, 7, 8 states, or linear horizontal layout.
- `linear`: Arranges states horizontally with proportional spacing.
- `circle`: Positions states in a circle; ideal for modulo / clock state machines (e.g., decimal modulo 3).
- `grid_RxC` (e.g., `grid_2x2`, `grid_2x3`, `grid_3x3`): Explicitly arranges states on a uniform grid with $R$ rows and $C$ columns.

---

### Automated Verification Harness (`test_pipeline.py`)

A comprehensive verification test suite validating schema compliance, SVG vector integrity, HTML artifact compilation, and simulator execution across all repository specifications.

```bash
# Run full test suite across all specifications
python scripts/test_pipeline.py

# Verbose output with per-test trace reporting
python scripts/test_pipeline.py --verbose

# Fast mode (in-process compilation plus smoke CLI checks)
python scripts/test_pipeline.py --fast

# Canonical/legacy renderer CLI and Python API compatibility
python scripts/test_renderer.py
```

#### Pipeline Test Stages:
1. **Stage 1: JSON Schema & Mathematical Integrity**: Checks state IDs, start state uniqueness, alphabet and transition fields, endpoint containment, transition symbols, and test-case field types. DFA determinism and totality remain construction requirements to check separately.
2. **Stage 2: Batch HTML & SVG Compilation**: Compiles every specification through `scripts/render_automaton.py`, checking exit code 0, artifact size, and required HTML/SVG structure.
3. **Stage 3: Simulator Logic Verification**: Simulates all defined `test_cases` against the internal transition engine (scalar for DFA, powerset $\epsilon$-closure for NFA), asserting 100% agreement with expected acceptance outcomes.
4. **Stage 4: CLI Interface Verification**: Exercises CLI arguments, error exit codes on malformed inputs, and layout engine overrides.

---

## Specification Schema Reference

Automata specifications are declared in standardized JSON format.

### Interface Contract

| Field | Type | Description |
|---|---|---|
| `name` / `title` | `string` | Machine identifier and academic exercise title |
| `subtitle` | `string` | Mathematical language description (e.g., $L = \{w : \dots\}$) |
| `type` | `string` | Machine category: `"dfa"`, `"nfa"`, `"epsilon_nfa"`, or `"product_dfa"` |
| `alphabet` | `list[string]` | Alphabet symbols (e.g. `["0", "1"]` or `["a", "b"]`) |
| `width` | `integer` | Canvas viewport width in pixels (default: `800`) |
| `height` | `integer` | Canvas viewport height in pixels (default: `380`) |
| `sample_input` | `string` | Default input tape loaded into simulator |
| `states` | `list[object]` | List of state objects: `id`, `label`, `x`, `y`, `is_start`, `is_accept` |
| `transitions` | `list[object]` | List of transitions: `from`, `to`, `symbols`, `curve`, `label_offset`, `loop` |
| `test_cases` | `list[object]` | Test vectors: `input` (string), `expected` (boolean) |

### Canonical JSON Specification Example

```json
{
  "name": "even_zeros",
  "type": "dfa",
  "title": "Exercise 1.1: Even Number of Zeros",
  "subtitle": "Language L = {w \u2208 {0, 1}* : w contains an even number of 0s}",
  "sample_input": "1001",
  "alphabet": ["0", "1"],
  "width": 720,
  "height": 320,
  "states": [
    {
      "id": "q_even",
      "label": "q_even",
      "x": 240,
      "y": 160,
      "is_start": true,
      "is_accept": true
    },
    {
      "id": "q_odd",
      "label": "q_odd",
      "x": 480,
      "y": 160,
      "is_start": false,
      "is_accept": false
    }
  ],
  "transitions": [
    {
      "from": "q_even",
      "to": "q_even",
      "symbols": ["1"],
      "loop": "top"
    },
    {
      "from": "q_even",
      "to": "q_odd",
      "symbols": ["0"],
      "curve": -28,
      "label_offset": -16
    },
    {
      "from": "q_odd",
      "to": "q_even",
      "symbols": ["0"],
      "curve": -28,
      "label_offset": -16
    },
    {
      "from": "q_odd",
      "to": "q_odd",
      "symbols": ["1"],
      "loop": "top"
    }
  ],
  "test_cases": [
    {"input": "", "expected": true},
    {"input": "1", "expected": true},
    {"input": "0", "expected": false},
    {"input": "00", "expected": true},
    {"input": "10101", "expected": true},
    {"input": "000", "expected": false}
  ]
}
```

---

## Repository Structure

```
.
├── .agents/                               # Multi-agent system orchestration
│   └── skills/
│       └── automata-pipeline/             # AI Agent Automata Skill
│           ├── SKILL.md                   # Master Router (< 120 lines)
│           └── references/                # Modular Reference Manuals
│               ├── closure_and_product_construction.md
│               ├── dfa_formalism_and_proofs.md
│               ├── nfa_and_epsilon_transitions.md
│               ├── rendering_and_artifacts.md
│               ├── subset_construction.md
│               ├── regular_expressions.md
│               ├── pumping_lemma_and_nonregularity.md
│               ├── practice_workflow.md
│               └── lecture_context.md
├── scripts/                               # Core Tooling & Verification
│   ├── render_automaton.py                # Canonical DFA/NFA/ε-NFA SVG/HTML renderer
│   ├── render_dfa.py                      # Legacy CLI and compile_dfa API wrapper
│   ├── test_pipeline.py                   # Automated E2E verification test harness
│   ├── test_renderer.py                   # Renderer command and API compatibility checks
│   └── examples/                          # Canonical distribution examples
│       ├── decimal_mod3.json
│       ├── no_three_bs.json
│       ├── sum_mod3.json
│       ├── fig1_10_product_union.json
│       ├── fig1_11_nfa.json
│       ├── fig1_11_dfa_converted.json
│       ├── fig1_12_epsilon_nfa.json
│       ├── fig1_12_dfa_converted.json
│       ├── fig1_14_regular_ops.json
│       ├── concat_epsilon.json
│       ├── star_incoming_start.json
│       ├── reverse_epsilon.json
│       └── regex_optional_a_b_star.json
├── specs/                                 # Practice specifications; new files ignored by Git
│   └── sigma_plus.json                    # Bundled DFA for nonempty strings
├── artifacts/                             # HTML/SVG outputs; new files ignored by Git
├── AGENTS.md                              # Mandatory agent behavioral & visual rules
├── GEMINI.md                              # Synchronized rules for Gemini models
├── LICENSE                                # MIT License (Copyright 2026 Daiwik Chilukuri)
└── README.md                              # Repository Documentation
```

---

## Verification & Quality Assurance

The verification harness checks specification fields and references, compiles every JSON fixture, verifies emitted HTML/SVG structure, and evaluates each fixture's expected string memberships using ε-closure simulation. The renderer compatibility suite also exercises both CLI names, both module entry points, and both Python compiler APIs.

These checks do not automatically prove arbitrary language equivalence, perform pixel-level layout audits, or convert raw regex. The skill supplies mathematical construction and proof procedures; inspect generated diagrams when preparing a full solution.

Run the test harness to verify your environment:
```bash
python scripts/test_pipeline.py
python scripts/test_renderer.py
```

---

## License

This project is open-source software licensed under the **[MIT License](LICENSE)**.  
Copyright &copy; 2026 Daiwik Chilukuri. All rights reserved.
