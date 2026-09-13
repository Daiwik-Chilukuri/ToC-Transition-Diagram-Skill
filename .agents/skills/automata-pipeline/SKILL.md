---
name: automata-pipeline
description: Complete pipeline to design, solve, determinize, and visually render Deterministic Finite Automata (DFA), Non-deterministic Finite Automata (NFA), and Regular Languages following academic lecture standards. Generates dark-mode TikZ-style SVG diagrams, interactive HTML tape simulators, transition tables, configuration proofs, product constructions, and subset determinization.
---

# Automata Pipeline: Master Solver & Visualizer Router

Use this skill whenever addressing questions, exercises, proofs, or design tasks related to Deterministic Finite Automata (DFA), Non-deterministic Finite Automata (NFA), Regular Languages, or Automata Visualization.

---

## 1. Master Routing Table

Consult the dedicated reference file in `references/` based on the specific task type:

| Task Type / Problem Domain | Theoretical Mechanism & Key Topics | Reference Guide |
|---|---|---|
| **Single DFA Design & Proofs** | 5-part solution structure, state invariants, inductive equivalence proofs ($L \subseteq \mathcal{L}(M)$ and $\mathcal{L}(M) \subseteq L$), configuration yield relations $(q, w) \vdash_M^* (q', \epsilon)$ | `references/dfa_formalism_and_proofs.md` |
| **Closure Operations & Product DFA** | Cartesian product space $Q_1 \times Q_2$, joint transitions $\delta((p,q), \sigma)$, acceptance criteria for Union, Intersection, Complement, Set Difference, Symmetric Difference; Figure 1.10 walkthrough | `references/closure_and_product_construction.md` |
| **NFA & $\epsilon$-Transitions** | Formal quintuple $(Q, \Sigma, \delta, s, F)$ with $\delta: Q \times (\Sigma \cup \{\epsilon\}) \to \mathcal{P}(Q)$, computation trees, branching paths, $\epsilon$-closure $E(q)$, Theorem 1.2.3 / Figure 1.14 regular operations (Union, Concat, Star, Reversal) | `references/nfa_and_epsilon_transitions.md` |
| **Subset / Powerset Construction** | Theorem 1.2.1 determinization, $\epsilon$-closure start $E(s)$, subset transitions, lazy reachability exploration, trap state $\emptyset$, elimination of unreachable/redundant states; Figures 1.11 & 1.12 | `references/subset_construction.md` |
| **Rendering, JSON Spec & Artifacts** | Standalone HTML tape simulator generation via `scripts/render_dfa.py`, dark-mode TikZ styling, JSON spec schema, layout engines (`linear`, `circle`, `grid_2x2`, `grid_2x3`), composite state ID sanitization, markdown linking | `references/rendering_and_artifacts.md` |

---

## 2. Core Execution Protocols

Every automata solution MUST adhere to these mandatory protocols:

### Protocol 1: 5-Part Academic Solution Standard
Every formal automata solution must deliver all five components:
1. **State Intuition & Invariants**: Precise operational semantics and invariant $I(q)$ for every state $q \in Q$.
2. **Visual Diagram Artifact**: Dark-mode TikZ-style interactive HTML simulator generated via `scripts/render_dfa.py` and linked directly in the markdown response.
3. **Formal Quintuple**: Explicit mathematical specification $M = (Q, \Sigma, \delta, s, F)$ (or $N$ for NFAs).
4. **Transition Table**: Complete tabular representation of $\delta$ across all states $\times$ alphabet symbols.
5. **Step-by-Step Configuration Traces**: Explicit yield derivations $(s, w) \vdash^* (q, \epsilon)$ for at least one accepted string and one rejected string.

### Protocol 2: Mandatory Multi-DFA Rendering for Closure Operations
When solving Union ($L_1 \cup L_2$), Intersection ($L_1 \cap L_2$), Set Difference ($L_1 \setminus L_2$), or Symmetric Difference ($L_1 \oplus L_2$):
1. Construct and independently render interactive HTML artifacts for component $M_1$ and component $M_2$.
2. Construct and render the combined Cartesian product DFA $M = M_1 \times M_2$.
3. Link all three generated artifacts in the markdown response with interactive testing instructions.

### Protocol 3: Strict DFA Totality & Dead States
- All DFAs must be total: $\delta(q, \sigma)$ must be defined for every $q \in Q$ and $\sigma \in \Sigma$.
- Any condition leading to permanent rejection must route to an explicit trap/dead state ($R$ or $q_{\text{trap}}$) with self-loops on all symbols in $\Sigma$.

### Protocol 4: Professor's Dark-Mode TikZ Aesthetic
- Canvas: Dark background (`#0d1117` or `#07090e`).
- Nodes: Crisp circles with light stroke (`#f0f6fc`), fill `#161b22`, radius $r \ge 26\text{px}$ (scaled for labels).
- Accepting States: Concentric double circles.
- Start State: Free-floating incoming arrow from the left with no source node.
- Edges: Symmetrically curved Bezier paths or straight lines; self-loops neatly positioned.
- Typography: LaTeX-style math serif (`STIX Two Text`, `Times New Roman`, serif); clean symbol groupings (e.g. `0, 1`). No neon clutter.

### Protocol 5: Artifact CLI Generation
```bash
python scripts/render_dfa.py --spec <machine_spec.json> --out <artifact_path.html>
```
Sanitize composite state IDs (e.g., `id: "p0_q0"`, `label: "(p0, q0)"`) to ensure DOM and CSS stability.
