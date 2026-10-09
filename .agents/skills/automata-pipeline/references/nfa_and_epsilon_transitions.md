# Non-Deterministic Finite Automata (NFAs) and $\epsilon$-Transitions

This guide provides the authoritative mathematical formalism, execution semantics, computation tree properties, $\epsilon$-closure algorithms, and regular operation constructions for NFAs, based on Chapter 1 (Section 1.2, Definitions 1.2.1--1.2.4, Theorem 1.2.3, and Figures 1.11--1.14) of the lecture notes.

---

## 1. Mathematical Formalism

### 1.1 Formal Quintuple Definition (Definition 1.2.1)
A Non-Deterministic Finite Automaton (NFA) is a 5-tuple:
$$N = (Q, \Sigma, \delta, s, F)$$
where:
1. **$Q$**: A finite set of states.
2. **$\Sigma$**: A finite input alphabet (e.g. $\{0, 1\}$ or $\{a, b\}$).
3. **$s \in Q$**: The initial/start state.
4. **$F \subseteq Q$**: The set of final (accepting) states.
5. **$\delta$**: The transition function mapping each state and input symbol (or the empty string $\epsilon$) to a subset of states (powerset $\mathcal{P}(Q) = 2^Q$):
   $$\delta: Q \times (\Sigma \cup \{\epsilon\}) \to \mathcal{P}(Q)$$

### 1.2 Fundamental Differences from DFAs
| Property | DFA ($M$) | NFA ($N$) |
| :--- | :--- | :--- |
| Next State Type | Single scalar state $q' \in Q$ | Set of states $P \in \mathcal{P}(Q)$ |
| Missing Transitions | Forbidden (strictly total) | Permitted ($\delta(q, \sigma) = \emptyset$, branch aborts) |
| Non-Determinism | Exactly 1 transition per symbol | $0, 1,$ or multiple transitions per symbol |
| $\epsilon$-Transitions | Not allowed | Permitted (can change state without consuming input) |
| String Acceptance | Unique trace ends in $q \in F$ | $\ge 1$ computation path ends in $q \in F$ |

---

## 2. Execution Semantics & Computation Trees

### 2.1 Configuration and Yield Relation (Definitions 1.2.2--1.2.3)
- **Configuration**: An ordered pair $(q, w) \in Q \times \Sigma^*$ where $q$ is the current state and $w$ is the remaining input string.
- **One-Step Yield Relation ($\vdash_N$)**:
  $$(q, w) \vdash_N (q', w') \iff \exists u \in \Sigma \cup \{\epsilon\} \text{ such that } w = uw' \text{ and } q' \in \delta(q, u)$$
- **Reflexive Transitive Closure ($\vdash_N^*$)**: Zero or more steps of $\vdash_N$.
- **Language Acceptance (Definition 1.2.4)**:
  A string $w \in \Sigma^*$ is accepted by $N$ if and only if there exists some state $q \in F$ such that:
  $$(s, w) \vdash_N^* (q, \epsilon)$$
  The language of $N$ is $\mathcal{L}(N) = \{w \in \Sigma^* : (s, w) \vdash_N^* (q, \epsilon) \text{ for some } q \in F\}$.

### 2.2 Computation Tree Branching Paths (Figure 1.13)
The evaluation of an NFA on an input string forms a directed computation tree rooted at $(s, w)$:
1. **Accepting Path**: A finite path reaching $(q_f, \epsilon)$ where all input has been consumed and $q_f \in F$. It need not be a leaf: outgoing $\epsilon$-edges do not prevent acceptance. One accepting path suffices.
2. **Rejecting Path**: A leaf node $(q_r, \epsilon)$ where all input has been consumed but $q_r \notin F$, and no $\epsilon$-transitions can reach $F$.
3. **Stuck Path**: A node $(q, aw')$ where $a \in \Sigma$, $\delta(q, a) = \emptyset$, and no $\epsilon$-transitions can be taken. This branch terminates without accepting.

An $\epsilon$-cycle can produce an infinite computation branch; it does not block another finite accepting path. Simulate sets with a visited-state closure traversal instead of enumerating an infinite tree. Reject only when the final active set is disjoint from $F$.

---

## 3. $\epsilon$-Closure Definition and Fixed-Point Algorithm

### 3.1 Mathematical Definition
For any state $q \in Q$, the $\epsilon$-closure $E(q)$ is the set of all states reachable from $q$ by zero or more $\epsilon$-transitions:
$$E(q) = \{p \in Q : (q, \epsilon) \vdash_N^* (p, \epsilon)\}$$
For a set of states $P \subseteq Q$:
$$E(P) = \bigcup_{p \in P} E(p)$$

### 3.2 Formal Properties
1. **Reflexivity**: $q \in E(q)$ for every state $q \in Q$.
2. **Idempotence**: $E(E(P)) = E(P)$ for all $P \subseteq Q$.
3. **Monotonicity**: $P_1 \subseteq P_2 \implies E(P_1) \subseteq E(P_2)$.

### 3.3 Iterative Graph Traversal Algorithm
To prevent infinite looping in the presence of $\epsilon$-cycles (e.g. $q_0 \xrightarrow{\epsilon} q_1 \xrightarrow{\epsilon} q_0$), use an explicit `visited` set:

```python
def compute_epsilon_closure(states, delta):
    """
    Computes the epsilon-closure of a set of states.
    delta is a dict: (state, symbol) -> set of next states.
    """
    closure = set(states)
    stack = list(states)
    
    while stack:
        current = stack.pop()
        eps_targets = delta.get((current, "ε"), set()) | delta.get((current, "\\epsilon"), set())
        for nxt in eps_targets:
            if nxt not in closure:
                closure.add(nxt)
                stack.append(nxt)
                
    return frozenset(closure)
```

---

## 4. Constructions for Regular Operations (Theorem 1.2.3 & Figure 1.14)

Let $N_1 = (Q_1, \Sigma, \delta_1, s_1, F_1)$ and $N_2 = (Q_2, \Sigma, \delta_2, s_2, F_2)$ be two NFAs with disjoint state sets ($Q_1 \cap Q_2 = \emptyset$).

### 4.1 Union ($L_1 \cup L_2$)
Introduce a new initial state $s_0 \notin Q_1 \cup Q_2$ with $\epsilon$-transitions branching to both component start states:
- $Q = Q_1 \cup Q_2 \cup \{s_0\}$
- $s = s_0$
- $F = F_1 \cup F_2$
- Transition function $\delta$:
  $$\delta(s_0, \epsilon) = \{s_1, s_2\}, \quad \delta(s_0, \sigma) = \emptyset \quad \forall \sigma \in \Sigma$$
  $$\delta(q, u) = \delta_i(q, u) \quad \forall q \in Q_i, u \in \Sigma \cup \{\epsilon\}$$

### 4.2 Concatenation ($L_1 L_2$)
Link all accepting states of $N_1$ to the initial state of $N_2$ via $\epsilon$-transitions. The accepting states of $N_1$ lose their accepting status:
- $Q = Q_1 \cup Q_2$
- $s = s_1$
- $F = F_2$
- Transition function $\delta$:
  - For $q \in Q_1 \setminus F_1$: $\delta(q, u) = \delta_1(q, u)$
  - For $q \in F_1$: $\delta(q, \sigma) = \delta_1(q, \sigma)$ for $\sigma \in \Sigma$, and $\delta(q, \epsilon) = \delta_1(q, \epsilon) \cup \{s_2\}$
  - For $q \in Q_2$: $\delta(q, u) = \delta_2(q, u)$

### 4.3 Kleene Star ($L_1^*$)
Introduce a new initial state $s_0$ that is also accepting (recognizing $\epsilon$). Add an $\epsilon$-transition from $s_0$ to $s_1$, and loopback $\epsilon$-transitions from each state in $F_1$ back to $s_1$:
- $Q = Q_1 \cup \{s_0\}$
- $s = s_0$
- $F = F_1 \cup \{s_0\}$
- Transition function $\delta$:
  - $\delta(s_0, \epsilon) = \{s_1\}$; $\delta(s_0, \sigma) = \emptyset$ for $\sigma \in \Sigma$
  - For $q \in Q_1 \setminus F_1$: $\delta(q, u) = \delta_1(q, u)$
  - For $q \in F_1$: $\delta(q, \sigma) = \delta_1(q, \sigma)$ for $\sigma \in \Sigma$, and $\delta(q, \epsilon) = \delta_1(q, \epsilon) \cup \{s_1\}$

*Crucial Caveat (Exercise 1.2.9)*: Making $s_1$ accepting directly without creating $s_0$ is flawed if $s_1$ has incoming transitions from inside $N_1$, as it may accept invalid strings that loop into $s_1$ prematurely.

### 4.4 Reversal ($L_1^R$)
Reverse the direction of every transition arrow. Introduce a new initial state $s_0$ with $\epsilon$-transitions to every state in $F_1$. The sole accepting state becomes the original start state $s_1$:
- $Q = Q_1 \cup \{s_0\}$
- $s = s_0$
- $F = \{s_1\}$
- Transition function $\delta$:
  - $\delta(s_0, \epsilon) = F_1$; $\delta(s_0, \sigma) = \emptyset$ for $\sigma \in \Sigma$
  - For $q \in Q_1$ and **every** $u \in \Sigma \cup \{\epsilon\}$: $\delta(q,u) = \{p \in Q_1 : q \in \delta_1(p,u)\}$.

This reverses existing $\epsilon$-edges as well as symbol edges. The lecture's p. 21 construction starts from a DFA, so its old-state $\epsilon$-sets are empty. They are not empty in general when the input is an $\epsilon$-NFA (Exercise 1.2.10). Example: reversing $s \xrightarrow{\epsilon} t \xrightarrow{a} f$ gives $s_0 \xrightarrow{\epsilon} f \xrightarrow{a} t \xrightarrow{\epsilon} s$, with only $s$ accepting.

## 5. Construction discipline and empty-string cases

Before combining components, rename each entire state set to disjoint IDs (e.g., `left_q0`, `right_q0`), updating all edges, starts, and finals. Preserve the old labels separately if useful. Use the common alphabet $\Sigma_1\cup\Sigma_2$; an NFA's undefined symbol moves become $\emptyset$, rather than requiring DFA trap states. Allocate fresh states outside both component sets.

For a component DFA, read each scalar transition as a singleton NFA target and supply empty $\epsilon$-sets. Preserve all old edges when adding links: union with $\{s_2\}$ or $\{s_1\}$, never overwrite an existing $\epsilon$ target set.

| Operation | Empty-string criterion | Why the construction is correct |
|---|---|---|
| $L_1\cup L_2$ | Either component accepts $\epsilon$ | Choose either component; every accepting path stays in its selected component after the new start |
| $L_1L_2$ | Both components accept $\epsilon$ | Cross a final-to-start link after a prefix $x\in L_1$; accept after a suffix $y\in L_2$, so $w=xy$ |
| $L_1^*$ | Always accepts $\epsilon$, including $L_1=\emptyset$ | New final start realizes zero factors; links between child runs realize finitely many factors in $L_1$ |
| $L_1^R$ | Exactly when $L_1$ accepts $\epsilon$ | Reverse a finite accepting path, retaining the order-reversal of consumed symbols and all zero-symbol steps |

In concatenation, old $F_1$ states cease to be final but retain outgoing edges. An accepting path can continue in the first machine or cross to the second, allowing every possible split. Empty factors are handled by closure, not by forcing a consumed boundary symbol.

For Exercise 1.2.9, the fresh star start prevents accepting prefixes merely because they return to the old start. Counterexample: old start $s$, final $f$, edges $s\xrightarrow{a}s$ and $s\xrightarrow{b}f$ recognize $a^*b$. Making $s$ final accepts `a`, which is outside $(a^*b)^*$. Retain $s$ as nonfinal and add a fresh final start with an $\epsilon$-edge to $s$.

## 6. One accepting state (Exercise 1.2.8)

Add fresh $f_\text{new}$, make it the only final state, and add an $\epsilon$-edge from **every** old final to it. Keep all old transitions; give the new final no outgoing edges. An old accepting path can finish by taking that edge, and every path to the new final must first reach an old final. This also preserves $\epsilon$ acceptance and works when the old final set is empty (the new final is unreachable).

## 7. Set traces and verification

For $w=a_1\cdots a_n$, compute $A_0=E(\{s\})$ and $A_{i+1}=E(\bigcup_{q\in A_i}\delta(q,a_{i+1}))$. Accept iff $A_n\cap F\ne\emptyset$. An individual configuration trace may show symbol and $\epsilon$ moves separately; an $\epsilon$ move preserves the unread suffix. Use a set trace to certify rejection of all branches.

Test empty components, components accepting $\epsilon$, multiple finals, pre-existing $\epsilon$ links, and cycles. The fixtures `concat_epsilon.json`, `star_incoming_start.json`, `reverse_epsilon.json`, and `regex_optional_a_b_star.json` in `scripts/examples/` exercise these cases. For regex structural recursion, read [regular expressions](regular_expressions.md); to determinize, read [subset construction](subset_construction.md).
