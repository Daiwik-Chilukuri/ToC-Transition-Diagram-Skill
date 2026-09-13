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
1. **Accepting Path**: A leaf node $(q_f, \epsilon)$ where all input has been consumed and $q_f \in F$. If at least one leaf is accepting, the string is accepted.
2. **Rejecting Path**: A leaf node $(q_r, \epsilon)$ where all input has been consumed but $q_r \notin F$, and no $\epsilon$-transitions can reach $F$.
3. **Stuck / Non-Halting Path**: A node $(q, aw')$ where $a \in \Sigma$, $\delta(q, a) = \emptyset$, and no $\epsilon$-transitions can be taken. This branch terminates immediately without accepting.

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
  - For $q \in Q_1, \sigma \in \Sigma$: $\delta(q, \sigma) = \{p \in Q_1 : \delta_1(p, \sigma) \ni q\}$
  - $\delta(q, \epsilon) = \emptyset$ for $q \in Q_1$
