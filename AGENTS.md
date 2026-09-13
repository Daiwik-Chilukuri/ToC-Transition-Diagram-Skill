# Automata Design & DFA Visualization Rules

Always follow these rules when answering questions, exercises, or homework related to Formal Languages, Automata Theory, DFAs, NFAs, or Regular Expressions:

1. **Active Skill & Modular Architecture**:
   - Always utilize the `automata-pipeline` skill for any questions, exercises, proofs, or design tasks related to Formal Languages, Automata Theory, DFAs, NFAs, Regular Expressions, or State Machines.
   - Consult modular reference guides in `.agents/skills/automata-pipeline/references/` for detailed theoretical definitions, construction algorithms, proof templates, and rendering specifications (`closure_and_product_construction.md`, `nfa_and_epsilon_transitions.md`, `subset_construction.md`, `dfa_formalism_and_proofs.md`, `rendering_and_artifacts.md`).

2. **Visuals First & Mandatory Artifact Generation**:
   - Always generate a clean, dark-mode TikZ-style visual automata diagram with the interactive string tester using:
     `python scripts/render_dfa.py --spec <spec.json> --out <artifact_path.html> [--svg <diagram.svg>]`
   - Generate and verify interactive artifacts prior to writing final solution text.
   - Provide direct relative links to all generated HTML artifacts in the response along with explicit instructions for user interaction (e.g., entering input strings, stepping through the tape, observing state transitions).

3. **Mandatory Multi-DFA Visualizations for Closure Operations**:
   - Whenever solving a problem involving regular closure operations (Union, Intersection, Set Difference, Symmetric Difference, or Cartesian Product Construction):
     a. **Component DFA $M_1$**: Formulate the JSON spec (`specs/<problem>_m1.json`) and independently render the interactive HTML artifact (`artifacts/<problem>_m1.html`).
     b. **Component DFA $M_2$**: Formulate the JSON spec (`specs/<problem>_m2.json`) and independently render the interactive HTML artifact (`artifacts/<problem>_m2.html`).
     c. **Combined Product DFA ($M = M_1 \times M_2$)**: Construct the Cartesian product machine with state space $Q_1 \times Q_2$, joint transitions $\delta((p,q), \sigma) = (\delta_1(p,\sigma), \delta_2(q,\sigma))$, and the designated accepting state criterion ($F_\cup, F_\cap, F_\setminus, F_\Delta$). Formulate the product spec (`specs/<problem>_product.json`) and render the combined interactive HTML artifact (`artifacts/<problem>_product.html`).
     d. **Response Artifact Linking**: Explicitly link all three generated HTML artifacts in the response with clear guidance on how the user can interactively test the component machines against the combined product machine.

4. **NFA & Powerset Simulator Support**:
   - For Non-deterministic Finite Automata (NFAs), model transitions using $\delta: Q \times (\Sigma \cup \{\epsilon\}) \to \mathcal{P}(Q)$. Support $\epsilon$-transitions using `"ε"` or `"\epsilon"`, and multi-target transitions for identical symbols.
   - For subset / powerset constructions converting NFAs to DFAs:
     a. Compute the $\epsilon$-closure $E(s)$ for the start state and $E(\bigcup_{p \in P} \delta(p, \sigma))$ for subset transitions.
     b. Render the determinized DFA using sanitized composite state identifiers (e.g., `id: "q0_q1"`, `label: "{q0, q1}"`) and explicit dead states for empty subsets (`id: "empty"`, `label: "∅"`).
     c. Eliminate unreachable subset states to ensure concise and readable diagrams.

5. **Professor's Aesthetic**:
   - Strictly adhere to academic dark-mode presentation:
     - **Canvas**: Dark background (`#0d1117` / `#07090e`).
     - **Nodes**: Crisp white circular borders (`#f0f6fc`), filled with dark card background (`#161b22`), adaptive radius ($r \ge 26\text{px}$) preventing label clipping on composite IDs.
     - **Accepting States**: Concentric double circles for all final states ($F$).
     - **Start State**: Free-floating incoming arrow from the left pointing directly to initial state ($s$).
     - **Transitions**: Smooth curved Bezier arrows for bidirectional pairs or non-adjacent jumps; clean self-loops; straight lines for adjacent unidirectional edges.
     - **Typography**: Academic math serif typography (`STIX Two Text`, Computer Modern, Times style).
     - **Clutter Elimination**: NO multi-colored neon clutter. Semantic colors strictly reserved for simulator state tracking (active `#58a6ff`, accepted `#3fb950`, rejected `#f85149`).

6. **Complete Mathematical Formalism**:
   - Every automata solution must deliver the complete 5-part academic lecture standard:
     1. **State Intuition & Invariant**: Formal operational meaning and invariant $I(q)$ for every state $q \in Q$.
     2. **Visual Diagram Artifact Link(s)**: Working link(s) to generated interactive HTML artifact(s).
     3. **Formal Mathematical Quintuple**: Explicit mathematical specification $M = (Q, \Sigma, \delta, s, F)$ (or NFA 5-tuple).
     4. **Transition Table**: Total, explicit Markdown table across all states $\times$ alphabet symbols.
     5. **Step-by-Step Configuration Traces**: Explicit yield derivations $(s, w) \vdash^* (q, \epsilon)$ for at least one accepted string ($w \in L$) and one rejected string ($w \notin L$).

7. **DFA Totality & Dead State Rigor**:
   - DFAs must be strictly deterministic and complete: every state must handle every alphabet symbol ($\delta: Q \times \Sigma \to Q$ is a total function).
   - Partial transitions are strictly forbidden. Any condition leading to permanent rejection must route to an explicit trap/dead state ($R$, $q_{\text{trap}}$, or $\emptyset$) with self-loops on all symbols in $\Sigma$.
   - Verify complete determinism before performing complementation or Cartesian product constructions.
