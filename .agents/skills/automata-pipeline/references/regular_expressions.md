# Regular expressions: semantics and automata conversion

Lecture basis: Sections 1.3–1.3.3, pp. 24–32 of `regular_Sept_30.pdf`; Definitions 1.3.1, Theorems 1.3.1 and 1.3.2, Figure 1.15. Consult [lecture context](lecture_context.md) for notation and source corrections.

## Parse before constructing

The inductive grammar is $R ::= ∅ | ε | a | (R+R) | (RR) | R^*$, where $a∈Σ$.
These denote, respectively, the empty language, the singleton empty-string language, a singleton symbol language, union, concatenation, and Kleene star.

Precedence is parentheses, star, concatenation, union. Thus $ab+c^*$ means $(ab)+(c^*)$; $a+bc$ means $a+(bc)$.
Binary `+` is union in the lecture, not the programming quantifier “one or more.” A language superscript $L^+$ means $LL^*$, which excludes a zero-factor concatenation (but can contain ε when $ε∈L$). Spell out context if notation is ambiguous. $Σ$ is shorthand for the union of the alphabet's symbols.

Keep expression syntax distinct from its denoted language: $L(ε)=\{ε\}$, $L(∅)=∅$, $L(a)=\{a\}$. The lecture underlines expression symbols to make this distinction; explain it when useful without requiring underlines in every answer.

Formal-language membership concerns the entire string. Programming search semantics, anchors, backreferences, lookaround, and engine-specific features are outside this grammar. Never pass the lecture's expression directly to Python `re` as if `+` meant union.

## Regex → ε-NFA (Theorem 1.3.1)

Parse a syntax tree and recurse, allocating fresh state IDs for each occurrence, including repeated copies of the same subexpression.

| Expression | Base/recursive construction |
|---|---|
| ∅ | One start, no finals, all transition sets empty |
| ε | One start that is final, all transition sets empty |
| Symbol $a$ | Start $u$, final $v$, $δ(u,a)=\{v\}$, all other sets empty |
| $R_1+R_2$ | Disjoint child NFAs, fresh start with ε-arrows to both starts, union of child finals |
| $R_1R_2$ | Child NFAs, ε-arrows from every first final to the second start, only second finals accepting |
| $R_1^*$ | Fresh accepting start with ε-arrow into the child; every child final ε-links back to its start; retain child finals |

Preserve all existing transitions. Exact formulas and empty-language cases are in [NFA constructions](nfa_and_epsilon_transitions.md). This is the lecture's structural construction; a Thompson variant with one final per fragment is also valid, but identify the convention and use it consistently.

Show important intermediate fragments when explaining the construction. For a DFA request, apply [subset construction](subset_construction.md) afterwards, including initial and post-symbol ε-closure. Render JSON only after defining the automaton; the repository supplies a renderer, not an automatic regex compiler.

**Worked example:** $(a+ε)b^*$ denotes $b^*∪ab^*$. Build the union of the $a$ and ε fragments, build the star of a fresh $b$ fragment, then concatenate. A compact equivalent NFA has start $u$, final $v$, $u\xrightarrow{a,ε}v$, $v\xrightarrow{b}v$. It accepts ε, a, b, abb; rejects aa, ba, aba. Do not present the compact graph as the unsimplified structural construction.

Correctness is structural induction: prove the three bases, then show the construction realizes each operator. Union selects a branch; concatenation guesses a split; star partitions into finitely many factors including zero.

## Identities for simplification (Section 1.3.2)

Equality of expressions below means equality of their languages.

| Law | Identity |
|---|---|
| Union | $R+S=S+R$; $(R+S)+T=R+(S+T)$; $R+R=R$; $R+∅=R$ |
| Concatenation | $(RS)T=R(ST)$; $εR=Rε=R$; $∅R=R∅=∅$ |
| Distribution | $R(S+T)=RS+RT$; $(S+T)R=SR+TR$ |
| Star | $(R^*)^*=R^*$; $(ε+R)^*=R^*$; $∅^*=ε$; $ε^*=ε$ |
| Unfolding | $ε+RR^*=R^*$; $ε+R^*R=R^*$ |

Concatenation is generally noncommutative: $ab≠ba$. Also $(R+S)^*$ generally differs from $R^*+S^*$ (e.g. ab), and $(RS)^*$ generally differs from $R^*S^*$ (e.g. a).

## DFA → regex: lecture recurrence (Theorem 1.3.2)

Use this method when the problem specifies the theorem, $R_{ij}^{(k)}$, or numbered intermediate states. For $Q=\{q_1,…,q_n\}$, define $R_{ij}^{(k)}$ to denote all labels of paths from $q_i$ to $q_j$ whose **internal** states have indices at most $k$. Endpoints are not restricted by $k$.

Initialize $R_{ij}^{(0)}$ as the union of direct transition labels from $q_i$ to $q_j$. Add ε when $i=j$ for the length-zero path; use ∅ when there are no labels and $i≠j$.

For $k=1,…,n$:
$$R_{ij}^{(k)}=R_{ij}^{(k-1)}+R_{ik}^{(k-1)}(R_{kk}^{(k-1)})^*R_{kj}^{(k-1)}.$$

All right-hand entries come from the previous layer. Compute a new matrix, rather than overwriting the previous one during the same layer. Justify the recurrence by splitting paths into those avoiding $q_k$ internally and those going through it, possibly looping there.

For start $q_s$ the result is $\sum_{q_j∈F}R_{sj}^{(n)}$, where the sum means union. An empty final set gives ∅. With an accepting start, the result includes ε. A full table contains $(n+1)n^2$ indexed expressions including the base layer; there are $n^3$ recurrence updates. This counts entries/updates, not constant-time operations: expression sizes can grow substantially.

### Worked recurrence: odd number of b's (Example 1.3.6)

Over $Σ=\{a,b\}$, $q_1$ is even/start, $q_2$ is odd/final. Symbol a preserves the state, b toggles it.

$$R^{(0)}=\begin{pmatrix}ε+a&b\\b&ε+a\end{pmatrix}.$$

The entries needed for $R_{12}^{(2)}$ after allowing state 1 are:
$$R_{12}^{(1)}=b+(ε+a)(ε+a)^*b=a^*b,$$
$$R_{22}^{(1)}=ε+a+b(ε+a)^*b=ε+a+ba^*b.$$

Then:
$$R_{12}^{(2)}=R_{12}^{(1)}+R_{12}^{(1)}(R_{22}^{(1)})^*R_{22}^{(1)}
=a^*b(a+ba^*b)^*.$$

An equivalent expression is $a^*b(a^*ba^*b)^*a^*$. Explain the odd initial b and subsequent paired b's; ε and bb reject, b and aba accept. For Example 1.3.7 (at least two 1's), a concise equivalent expression is $0^*10^*1(0+1)^*$.

## State elimination alternative and equivalence checks

If no particular conversion method is specified, GNFA elimination is another option: add a fresh start and final, ε-link to the old start and from old finals, union parallel edge labels, label absent edges ∅. Eliminating $r$ updates surviving pairs by $R_{ij}←R_{ij}+R_{ir}(R_{rr})^*R_{rj}$ using the pre-elimination labels, then removes r. Do not confuse this convention with the diagonal ε initialization of the numbered recurrence.

For a rigorous equivalence check, construct complete DFAs for both expressions and search their reachable product for a pair where exactly one component accepts. Such a pair yields a distinguishing word; no such reachable pair proves equivalence. Short-string enumeration alone is a sanity check.
