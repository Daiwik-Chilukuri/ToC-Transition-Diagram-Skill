# Automata Design & DFA Visualization Rules

Always follow these rules when answering questions, exercises, or homework related to Formal Languages, Automata Theory, DFAs, NFAs, or Regular Expressions:

1. **Active Skill**: Always utilize the `automata-pipeline` skill.
2. **Visuals First**: Always generate a clean, dark-mode TikZ-style visual DFA diagram with the interactive string tester using `python scripts/render_dfa.py --spec <spec.json> --out <artifact_path.html>`. Provide the link to the generated artifact directly in the response.
3. **Professor's Aesthetic**:
   - Dark canvas (#0d1117 / #07090e).
   - Crisp white circular nodes.
   - Double circles for all accepting / final states ($F$).
   - Free incoming start arrow pointing to initial state ($s$).
   - Clean curved Bezier arrows for bidirectional or non-adjacent edges.
   - Academic math serif typography (Computer Modern / Times style).
   - NO multi-colored neon clutter.
4. **Complete Mathematical Formalism**: Every solution must include:
   - State Intuition & Invariant
   - Visual Diagram Artifact
   - Formal Quintuple $M = (Q, \Sigma, \delta, s, F)$
   - Transition Table
   - Step-by-step configuration traces $(q_0, w) \vdash_M^* (q, \epsilon)$ for test strings.
5. **DFA Totality**: DFAs must be strictly deterministic and complete: every state must handle every alphabet symbol, including explicit trap/dead states ($R$, $q_{\text{trap}}$) when strings are rejected.
