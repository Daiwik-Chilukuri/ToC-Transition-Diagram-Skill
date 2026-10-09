# Pumping lemma and nonregular languages

Lecture basis: Section 1.4, pp. 32–34 of `regular_Sept_30.pdf`, Theorem 1.4.1, Figure 1.16, Examples 1.4.1–1.4.4, Exercise 1.4.5. Use p for pumping length and i for repetition to keep them separate from a language's exponents.

## Statement and proof idea

If L is regular, then:
$$∃p≥1\;∀w∈L,\quad |w|≥p\Rightarrow
∃x,y,z\;(w=xyz\land |y|>0\land |xy|≤p\land ∀i≥0,\ xy^iz∈L).$$

An accepting computation of a p-state DFA visits p+1 states while consuming the first p symbols. Two state visits coincide by pigeonhole. The nonempty segment between them is y; its loop may be skipped or repeated without changing the eventual accepting result. The states repeat, not necessarily the entire configurations (which have different unread suffixes).

This is a necessary condition for regularity. Proving that some strings can be pumped does not prove regularity. Finite languages satisfy the condition vacuously for p above their maximum length.

## Nonregularity proof recipe

To refute the condition, establish:
$$∀p≥1\;∃w∈L,\ |w|≥p:\quad
∀x,y,z\;(w=xyz\land |y|>0\land |xy|≤p)
\Rightarrow ∃i≥0,\ xy^iz∉L.$$

1. Assume L regular and let p be its arbitrary pumping length.
2. Choose a witness w depending on p; explicitly prove membership and sufficient length.
3. Consider **any** legal decomposition. Derive its possible form from $|xy|≤p$ and $|y|>0$; use exhaustive cases if y can span different regions.
4. Choose i (it may depend on the decomposition) and show the pumped word violates L's defining condition.
5. Conclude a contradiction for every legal split, hence L is not regular.

The adversary chooses the split; the prover chooses w and, after seeing the split, i. One failed split is insufficient. Values i=0 and i=2 are convenient, not mandatory. Values i=1 never change the witness.

## Worked proofs and witness choices

### Equal blocks (Example 1.4.1)

For $L=\{a^nb^n:n≥0\}$, choose $w=a^pb^p$. Every legal y has form $a^t$ with $1≤t≤p$. At i=0, $xz=a^{p-t}b^p$ has unequal counts, so is outside L. This covers every decomposition.

### Prime unary lengths (Example 1.4.2)

For $L=\{a^r:r\text{ prime}\}$, choose a prime $r≥p$. Then every split has $y=a^t$, $1≤t≤p$. Choose $i=r+1$. The pumped length is $r+rt=r(1+t)$, a product of integers greater than 1, so it is composite. The existence of arbitrarily large primes supplies the witness. This equivalent argument makes the witness and quantifier order explicit.

### Palindromes (Example 1.4.4)

For $L=\{w∈\{a,b\}^*:w=w^R\}$, choose $w=a^pbba^p$. Again y=$a^t$ with $1≤t≤p$. Pumping down leaves $a^{p-t}bba^p$, whose outer a-block lengths differ; it is not a palindrome. Use a separator so unequal blocks cannot collapse into the same unary word.

### Square unary lengths (Exercise 1.4.5.1)

For $L=\{1^{m^2}:m≥1\}$, choose $w=1^{p^2}$. Every legal y has length t with $1≤t≤p$. Pumping up gives length $p^2+t$, strictly between $p^2$ and $(p+1)^2$, hence not a square. Compare against consecutive valid lengths rather than asserting “the length changed.”

## Closure reductions (Example 1.4.3 and Exercise 1.4.5)

When direct pumping creates messy splits, assume the target regular and combine it with known regular languages to obtain a known nonregular one. Identify the precise equality and the closure theorem.

- Equal counts in arbitrary order: intersect $L=\{w:\#a(w)=\#b(w)\}$ with regular $a^*b^*$ to obtain equal blocks.
- Unequal counts in arbitrary order: complement relative to $\{a,b\}^*$ to obtain the equal-count language.
- Unequal ordered blocks: if $U=\{a^ib^j:i≠j\}$ were regular, then $a^*b^*\setminus U$ would be the nonregular equal-block language. Complements alone include unordered strings, so keep the regular filter.
- Nonpalindromes: complement relative to the stated alphabet gives palindromes.

Having a nonregular subset does not by itself prove a language nonregular. The subset must arise via an operation whose closure would force regularity under the assumption.

## Impossible construction requests

NFAs and ε-NFAs have the same expressive power as DFAs. Nondeterminism does not provide unbounded counting or copying memory. For a nonregular target, explain impossibility and give a proof; do not create a finite-state “solution” that only tests bounded examples.

Check quantified definitions carefully. For example, $\{uvu^R:u∈\{a,b\}^+,v∈\{a,b\}^*\}$ is regular: taking u to be one symbol shows it is exactly the strings of length at least two with matching endpoints. In contrast, $\{ww:w∈\{a,b\}^*\}$ is not regular. Its witness $a^pba^pb$ pumps only the first a-block; a square with exactly two b's and ending in b must have equal a-block lengths, which pumping down destroys.

## Practice and answer checking

For a submitted proof, check witness membership/length, split universality, bound use, nonempty y, pumping exponent, and actual nonmembership. Identify the first logical gap and repair it; do not replace a sound alternative witness with a memorized template. Use [practice workflow](practice_workflow.md) for hints.

A finite pumping demo can illustrate a split, but does not decide regularity or replace a quantified proof. No recognizing automaton, quintuple, transition table, or simulator is required for a nonregularity proof.
