---
name: automata-pipeline
description: Use when solving or practicing formal-language problems involving DFA, NFA, epsilon transitions, regular closure operations, regular expressions, automata conversion, pumping lemma, or nonregularity proofs. Applies to academic regex semantics, not general programming regex troubleshooting.
---

# Automata Pipeline

Choose a mathematically valid construction or proof before rendering. Follow the lecture's notation and requested method; DFA, NFA, and regular expressions describe exactly the regular languages.

## Task routing

Read only the references needed for the problem. Paths below are relative to this skill.

| Task | Reference |
|---|---|
| DFA design, state invariants, configurations, induction | [DFA formalism](references/dfa_formalism_and_proofs.md) |
| Product DFA: union, intersection, difference, symmetric difference; complement | [Closure and products](references/closure_and_product_construction.md) |
| NFA semantics, ε-closure, ε-union, concatenation, star, reversal, single final state | [NFAs and ε-transitions](references/nfa_and_epsilon_transitions.md) |
| NFA → DFA, reachable subsets, equivalence proof | [Subset construction](references/subset_construction.md) |
| Regex meaning, precedence, identities, regex → NFA → DFA, DFA → regex | [Regular expressions](references/regular_expressions.md) |
| Pumping lemma, quantifiers, witnesses, closure-based nonregularity | [Pumping lemma](references/pumping_lemma_and_nonregularity.md) |
| Guided practice, hints, answer checking, lecture exercise selection | [Practice](references/practice_workflow.md) |
| Lecture sections, exercise numbers, notation and corrections | [Lecture context](references/lecture_context.md) |
| JSON specs, dark-mode diagrams, interactive HTML/SVG | [Rendering](references/rendering_and_artifacts.md) |

## Choose the method

1. State the alphabet, language, empty-string behavior, and requested representation. In these notes binary `+` means union, and ε is an empty string, never an input symbol.
2. Check regularity before attempting a machine. An exercise titled “design an NFA” is not evidence that a language is regular. For a nonregular language, provide a proof instead of a fictitious automaton.
3. For **ε-NFA union**, branch from a fresh start to disjoint copies of the components. For **concatenation**, link each first-component final to the second start. For **star**, use a fresh accepting start and final-to-start links. Preserve existing ε-edges. Read the NFA reference for precise accepting sets and reversal.
4. For **product DFA problems**, run two complete DFAs over the same alphabet. Render both components and the product. Union can use either construction; follow a requested ε-NFA method without imposing a product DFA. When no method is specified, use ε-union for NFA inputs and product union for DFA inputs.
5. For **complement**, determinize and complete first. Flip finals only in a complete DFA, relative to the stated alphabet.
6. For **regex**, parse by parentheses → star → concatenation → union. Derive from the syntax tree, or use the lecture's $R_{ij}^{(k)}$ recurrence for DFA → regex. The renderer accepts machine JSON, not raw regex.
7. For **nonregularity**, choose pumping or a closure reduction. Use the universal-decomposition argument in the pumping reference. A finite collection of experiments supports checking, not a proof.

## Deliver the requested solution

For a complete machine construction, supply:

1. State intuition and invariant/reachable-prefix meaning for each state. NFA predicates may overlap.
2. A generated interactive diagram with tested inputs.
3. The quintuple $(Q,Σ,δ,s,F)$.
4. A complete transition table: scalar targets for DFA; sets, including ∅ and an ε column, for ε-NFA.
5. Configuration traces: an accepting witness path and a rejecting all-branches/set trace for NFA; the unique trace for DFA. Include accepted and rejected examples when those classes exist. Do not invent a rejected string for $Σ^*$ or an accepted string for ∅.

Give soundness and completeness when proving a construction. For regex-only questions, provide the expression, semantics, derivation, and relevant checks; generate a machine when requested or needed for conversion. For pumping proofs, provide the lemma instantiation, witness, arbitrary split, pumping choice, and contradiction. A quintuple and recognizing simulator are inapplicable to a nonregular language.

For guided practice or hint-only requests, use the practice reference and reveal only the requested amount. Full artifact generation applies when revealing the complete machine solution, not when posing an exercise or checking one proof step.

## Rendering and verification

Run from the repository root:

```bash
python scripts/render_automaton.py --spec specs/<problem>.json --out artifacts/<problem>.html --svg artifacts/<problem>.svg
python scripts/test_pipeline.py
```

Keep the academic dark canvas, serif labels, white state outlines, double-circle finals, and floating start arrow. Use unique safe IDs with separate mathematical labels. Put ε on an edge, excluding it from `alphabet`; an empty simulator input is `""`.

For binary closure constructions, render the two components and combined machine using the chosen method. For a unary construction, show the original and result when useful for explaining the transformation. Verify ε, boundary cases, and representative accepted/rejected strings before linking generated artifacts. Use absolute local Markdown links in Codex; use relative repository links in portable documentation.

Existing renderer examples are in `scripts/examples/`, including union, concatenation with ε, star with an incoming start edge, reversal preserving ε, and a compositional regex NFA. These are machine fixtures, not a regex parser or automatic converter.

## Common mistakes

- Disjointly rename component states before joining machines; repeated `q0` labels must not merge states.
- NFA rejection requires exhausting all reachable states, not one failing branch.
- ε-closure includes its seeds, handles cycles, and applies initially and after each consumed symbol.
- Unreachable-state removal and minimization are distinct operations.
- Pumping proves nonregularity by violating a necessary condition; it cannot certify regularity.
