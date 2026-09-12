---
name: automata-pipeline
description: Complete pipeline to design, solve, and visually render Deterministic Finite Automata (DFA) and regular languages following academic lecture standards. Generates dark-mode TikZ-style SVG diagrams, interactive string simulators, transition tables, and configuration proofs.
---

# Automata Pipeline: DFA Solving & Visualization Skill

Use this skill whenever the user asks exercise questions, homework problems, or design tasks related to Deterministic Finite Automata (DFA), Non-deterministic Finite Automata (NFA), or Regular Languages.

---

## 1. Ground Rules & Mathematical Rigor (from Lecture PDF)

### Formal Quintuple Definition
Every DFA $M$ is formally defined as a 5-tuple:
$$M = (Q, \Sigma, \delta, s, F)$$
1. **$Q$**: The finite set of states.
2. **$\Sigma$**: The finite input alphabet (defaults to $\{0, 1\}$ or $\{a, b\}$).
3. **$s \in Q$**: The initial/start state (usually $q_0$ or semantic start like $0\%3$ or $OP$).
4. **$F \subseteq Q$**: The set of final (accepting) states.
5. **$\delta: Q \times \Sigma \to Q$**: The transition function (must be total and deterministic).

### Strict Completeness & Trap States
- **Total Function**: For every state $q \in Q$ and every symbol $\sigma \in \Sigma$, $\delta(q, \sigma)$ must be explicitly defined.
- **Explicit Rejection / Trap States**: If a condition causes permanent rejection (e.g. invalid prefix, sequence violation), route to a dead state (e.g. $R$, $q_{\text{trap}}$) with self-loops on all symbols in $\Sigma$.
- **Grouped Parallel Transitions**: Multiple symbols pointing to the same next state must be grouped as comma-separated labels (e.g. `0, 1` or `a, b`).

### State Naming Guidelines
- **Modulo / Congruence problems**: Use remainder labels `$0\%3$`, `$1\%3$`, `$2\%3$`.
- **Parity problems**: Use 2-letter binary states `$EE$`, `$EO$`, `$OE$`, `$OO$`.
- **Sequential / Substring / KMP**: Use indexed states `$q_0$`, `$q_1$`, `$q_2$`, $\dots$.
- **Structural / Position rules**: Use semantic labels `$OP$` (odd position), `$EP$` (even position), `$R$` (rejection).

---

## 2. Solution Response Standard

Every response to a DFA exercise must follow this 5-part structure:

### Part 1: Intuition & State Semantics
Explain the logic of the machine and the exact invariant represented by each state.

### Part 2: Visual DFA Diagram & Interactive Tester
Invoke `scripts/render_dfa.py` to create a dedicated HTML artifact:
```bash
python scripts/render_dfa.py --spec <dfa_spec.json> --out <artifact_path.html>
```
Present the diagram to the user with a direct artifact link and brief guidance on testing strings.

### Part 3: Formal Mathematical Quintuple
State $M = (Q, \Sigma, \delta, s, F)$ with explicit sets.

### Part 4: Transition Table
Present $\delta$ as a clean Markdown table:
| Current State ($q$) | Input Symbol ($\sigma$) | Next State ($\delta(q, \sigma)$) |
| :---: | :---: | :---: |
| $q_0$ | $0$ | $q_1$ |
| $q_0$ | $1$ | $q_0$ |

### Part 5: Step-by-Step Configuration Traces
Demonstrate acceptance and rejection using configuration yield notation $\vdash_M$:
$$(s, w) \vdash_M (q_1, w') \vdash_M^* (q_f, \epsilon)$$
- Provide at least one valid accepting string trace ending in $q_f \in F$.
- Provide at least one invalid rejecting string trace ending in $q_r \notin F$.

---

## 3. Visual Artifact Rendering Guidelines

The visual diagram must strictly follow the professor's TikZ aesthetic:
- **Canvas**: Dark background (`#0d1117` or `#07090e`).
- **Nodes**: Crisp circles with white/light stroke (`#f0f6fc`).
- **Accepting States**: Concentric double circles.
- **Start State**: Floating left-to-right incoming arrow with no source node.
- **Edges**: Smooth Bezier curves (opposing edges curved symmetrically) or straight lines. Self-loops placed neatly above/below.
- **Typography**: LaTeX/Computer Modern math serif font (`STIX Two Text`, `Times New Roman`, serif).
- **Interactive Simulator**: Included in the artifact, enabling step-by-step playback, active state glow, and tape tracking.

---

## 4. Upgrading for Future Topics (NFAs, RegEx, Minimization)
When newer PDFs and NFA exercises are provided:
- Allow non-deterministic mappings $\delta: Q \times (\Sigma \cup \{\epsilon\}) \to 2^Q$.
- Provide powerset subset construction ($2^Q$) for NFA to DFA determinization.
- Support $\epsilon$-transitions (marked with $\epsilon$).
