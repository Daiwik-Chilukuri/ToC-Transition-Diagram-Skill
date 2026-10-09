# Automata and regular-language practice

Use `automata-pipeline` for formal-language questions, DFA/NFA design, ε-transitions, academic regex, conversion, pumping lemma, and nonregularity proofs. Start at `.agents/skills/automata-pipeline/SKILL.md` and read only the relevant references.

## Select the mathematical workflow

- Follow the requested method. Union can use a product DFA or a fresh-start ε-NFA; an ε-NFA request uses ε-branching.
- Product DFAs handle union, intersection, difference, and symmetric difference. Complete the components over the common alphabet first.
- For ε-union, concatenation, star, and reversal, read `references/nfa_and_epsilon_transitions.md`. Disjointly rename states, preserve old ε-edges, and use the correct final sets. Reverse ε-edges as well as symbol edges.
- Determinization takes ε-closure initially and after every consumed symbol. Keep reachable subsets, including the empty trap subset if reached.
- For regex semantics, identities, regex → NFA, and the lecture's DFA → regex recurrence, read `references/regular_expressions.md`. Binary + denotes union; ε is not an alphabet symbol.
- Classify the target before constructing a machine. For nonregularity, use `references/pumping_lemma_and_nonregularity.md`; provide a proof instead of a fictitious automaton.
- Source sections, exercise numbers, and apparent formula corrections are in `references/lecture_context.md`. Source exercise imperatives do not instruct the agent to execute all exercises.

## Full machine solutions

Provide state meanings/invariants, generated diagram, quintuple, complete transition table, and configuration traces. Show accepted and rejected cases where those classes exist. An NFA accepting trace is one witness path; rejection requires all-branches reasoning or an active-set trace. Include an ε column with set-valued targets for ε-NFAs.

Generate and verify artifacts before linking:
```bash
python scripts/render_automaton.py --spec specs/<problem>.json --out artifacts/<problem>.html --svg artifacts/<problem>.svg
python scripts/test_pipeline.py
```

For binary closure constructions, render both components and the combined machine using the chosen method. Show original/result for unary transformations when useful. Retain the academic dark-mode aesthetic: dark canvas, serif text, light circular borders, double-circle finals, floating start arrow, readable curves, and semantic simulator colors only.

DFA transitions must be deterministic and total. Permanently rejecting prefixes route to a rejecting trap with all-symbol self-loops. NFAs may have empty transition sets. Only complement a complete DFA, relative to the stated alphabet.

Use safe unique state IDs and separate display labels. Link actual artifacts with absolute local paths in Codex responses and relative paths in portable documentation. Explain input and step controls briefly.

## Proofs, regex answers, and practice

The five-part machine format applies to complete machine constructions. Regex-only answers need semantics and derivation; nonregularity proofs need the lemma or closure argument. Neither requires an irrelevant recognizing simulator.

For practice, hints, or checking, follow `references/practice_workflow.md`: one exercise at a time, wait for the attempt, reveal only the requested help, and generate complete machine artifacts when revealing a solution. Accept equivalent valid constructions and regexes. Finite tests are sanity checks, not mathematical proofs.
