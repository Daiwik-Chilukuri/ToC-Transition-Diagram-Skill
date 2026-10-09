# Practice workflow

Use the lecture map in [lecture context](lecture_context.md) to select a topic or resolve an exercise number. Preserve any requested method and the user's desired amount of help.

## Interaction

- “Solve”, “show the construction”, or “full solution”: give a complete solution using the relevant theory reference.
- “Practice”, “quiz me”, or “let me try”: give one exercise at a time and wait for the attempt. State the alphabet and task; withhold the solution and answer-revealing artifacts.
- “Hint”: give one next-step hint at the requested depth.
- “Check my answer/proof”: evaluate the submitted work, identify the first substantive error, and explain a local repair. Accept equivalent regexes and different valid state names/graphs.
- When no practice topic is chosen, begin with an ε-union exercise, then progress to concatenation, star/reversal, determinization, regex conversions, and pumping proofs. Adapt the next exercise to what the attempt demonstrates.

Use conceptual hint → structural hint → worked step → full solution as increasing levels, advancing only when requested. For example, an equal-block pumping hint can first ask which prefix the pumping bound confines y to, before revealing y's form or the exponent.

## Check constructions

Verify alphabet and ε status, unique start, final-state choices, disjoint component copies, and preserved old transitions. Test ε and short boundaries. For NFA rejection, compute all active states after each symbol and ε-closure; one stuck branch is insufficient.

Distinguish state renaming and reachable-state pruning from minimization. If a student simplifies a structural construction, check language equivalence and whether the exercise requires showing the original procedure.

## Check regex answers

State what binary + means, parse precedence, distinguish ∅ from ε, and check whole-string semantics. For a claimed identity, use a shortest distinguishing example if false. For a recurrence answer, verify diagonal ε, previous-layer indices, final-state extraction, and simplification identities.

## Check proofs

Check quantifiers and both directions of construction equivalence. For pumping proofs, use the checklist in [pumping lemma](pumping_lemma_and_nonregularity.md). Short tests support examples, not universal proofs.

## Complete solution reveal

When revealing a machine solution, retain the five-part academic format from SKILL.md and generate the interactive diagram. For a regex-only answer or nonregularity proof, use its appropriate mathematical format. Link actual generated files, and explain the simulator input/step controls briefly.

Keep practice conversational; do not assign every exercise listed in the source or begin a long course unless requested.
