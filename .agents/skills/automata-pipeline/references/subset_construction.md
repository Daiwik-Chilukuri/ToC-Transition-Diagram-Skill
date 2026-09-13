# Powerset / Subset Construction (NFA to DFA Determinization)

This guide provides the complete algorithm, theoretical equivalence proof, lazy reachability engine, and benchmark walkthroughs for converting Non-Deterministic Finite Automata (NFAs) and $\epsilon$-NFAs into equivalent Deterministic Finite Automata (DFAs), based on Chapter 1 (Theorem 1.2.1, Figures 1.11 and 1.12) of the lecture notes.

---

## 1. Theorem 1.2.1 & Powerset Formalism

### 1.1 Theorem Statement
For every Non-Deterministic Finite Automaton $N = (Q, \Sigma, \delta, s, F)$, there exists an equivalent Deterministic Finite Automaton $M = (Q', \Sigma, \delta', s', F')$ such that:
$$\mathcal{L}(M) = \mathcal{L}(N)$$

### 1.2 Mathematical Formulation of Target DFA
1. **State Space ($Q'$)**: Each state in the DFA represents a subset of NFA states:
   $$Q' \subseteq \mathcal{P}(Q) = 2^Q$$
2. **Initial State ($s'$)**: The $\epsilon$-closure of the NFA start state:
   $$s' = E(s) \in Q'$$
3. **Accepting States ($F'$)**: Any subset containing at least one NFA final state:
   $$F' = \{P \in Q' : P \cap F \neq \emptyset\}$$
4. **Transition Function ($\delta'$)**: For any subset $P \subseteq Q$ and symbol $\sigma \in \Sigma$, transition to the $\epsilon$-closure of all states reachable on $\sigma$:
   $$\delta'(P, \sigma) = E\left(\bigcup_{p \in P} \delta(p, \sigma)\right) = \bigcup_{p \in P} \bigcup_{q \in \delta(p, \sigma)} E(q)$$

---

## 2. Lazy Reachability Exploration & Trap State Handling

### 2.1 The Powerset State Explosion Problem
The full powerset has $2^{|Q|}$ states (e.g. 16 states for a 4-state NFA, 1024 for a 10-state NFA). However, the vast majority of these theoretical subsets are completely unreachable from the initial subset $s'$.
- **Lazy Exploration**: A breadth-first search (BFS) queue is used to instantiate ONLY subsets reachable from $s'$.
- **Dead / Trap State ($\emptyset$)**: If a subset $P$ has no outgoing transitions on symbol $\sigma$, $\delta'(P, \sigma) = \emptyset$. Because DFAs must be strictly complete, the empty set $\emptyset$ becomes an explicit sink state:
  $$\delta'(\emptyset, \sigma) = \emptyset \quad \forall \sigma \in \Sigma$$
  Since $\emptyset \cap F = \emptyset$, the state $\emptyset$ is strictly non-accepting ($ \emptyset \notin F'$).

### 2.2 Algorithm Implementation (BFS Lazy Powerset)

```python
def subset_construction(nfa_states, alphabet, delta, start_state, final_states):
    """
    Determinizes an NFA/epsilon-NFA into an equivalent complete DFA.
    """
    from collections import deque

    def eps_closure(state_set):
        closure = set(state_set)
        stack = list(state_set)
        while stack:
            curr = stack.pop()
            eps_moves = delta.get((curr, "ε"), set()) | delta.get((curr, "\\epsilon"), set())
            for nxt in eps_moves:
                if nxt not in closure:
                    closure.add(nxt)
                    stack.append(nxt)
        return frozenset(closure)

    start_subset = eps_closure({start_state})
    visited = {start_subset}
    queue = deque([start_subset])
    
    dfa_transitions = {}
    
    while queue:
        P = queue.popleft()
        for sigma in alphabet:
            # Gather all raw transitions on symbol sigma
            raw_next = set()
            for p in P:
                raw_next |= delta.get((p, sigma), set())
            # Apply epsilon-closure
            next_subset = eps_closure(raw_next)
            
            dfa_transitions[(P, sigma)] = next_subset
            if next_subset not in visited:
                visited.add(next_subset)
                queue.append(next_subset)

    dfa_states = list(visited)
    dfa_accept = [P for P in dfa_states if any(q in final_states for q in P)]
    
    return dfa_states, start_subset, dfa_accept, dfa_transitions
```

---

## 3. Canonical Walkthrough 1: Figure 1.11 (NFA without $\epsilon$)

### 3.1 NFA Specification ($L = \{aba, ab\}^*$)
- $Q = \{q_0, q_1, q_2\}$, $\Sigma = \{a, b\}$, $s = q_0$, $F = \{q_0\}$
- Transitions:
  - $\delta(q_0, a) = \{q_1\}$, $\delta(q_0, b) = \emptyset$
  - $\delta(q_1, a) = \emptyset$, $\delta(q_1, b) = \{q_0, q_2\}$
  - $\delta(q_2, a) = \{q_0\}$, $\delta(q_2, b) = \emptyset$

### 3.2 Full Powerset vs Lazy Reachability Analysis
Total powerset size: $2^3 = 8$ states.
Lazy reachability BFS from $\{q_0\}$:
1. $P_0 = \{q_0\}$ (Start, Accept):
   - On $a \to \{q_1\}$
   - On $b \to \emptyset$ (Trap)
2. $P_1 = \{q_1\}$:
   - On $a \to \emptyset$
   - On $b \to \{q_0, q_2\}$
3. $P_{\emptyset} = \emptyset$:
   - On $a \to \emptyset$
   - On $b \to \emptyset$
4. $P_2 = \{q_0, q_2\}$ (Accept, contains $q_0$):
   - On $a \to \delta(q_0, a) \cup \delta(q_2, a) = \{q_1\} \cup \{q_0\} = \{q_0, q_1\}$
   - On $b \to \delta(q_0, b) \cup \delta(q_2, b) = \emptyset \cup \emptyset = \emptyset$
5. $P_3 = \{q_0, q_1\}$ (Accept, contains $q_0$):
   - On $a \to \delta(q_0, a) \cup \delta(q_1, a) = \{q_1\} \cup \emptyset = \{q_1\}$
   - On $b \to \delta(q_0, b) \cup \delta(q_1, b) = \emptyset \cup \{q_0, q_2\} = \{q_0, q_2\}$

### 3.3 State Elimination & Pruning Summary
- **Reachable States (5)**: $\{q_0\}, \{q_1\}, \{q_0, q_2\}, \{q_0, q_1\}, \emptyset$.
- **Pruned Unreachable States (3)**: $\{q_2\}, \{q_1, q_2\}, \{q_0, q_1, q_2\}$.

---

## 4. Canonical Walkthrough 2: Figure 1.12 ($\epsilon$-NFA)

### 4.1 $\epsilon$-NFA Specification
- $Q = \{q_0, q_1, q_2, q_3\}$, $\Sigma = \{0, 1\}$, $s = q_0$, $F = \{q_3\}$
- Transitions:
  - $\delta(q_0, 0) = \{q_0\}$, $\delta(q_0, 1) = \{q_0, q_1\}$, $\delta(q_0, \epsilon) = \emptyset$
  - $\delta(q_1, 0) = \{q_2\}$, $\delta(q_1, 1) = \emptyset$, $\delta(q_1, \epsilon) = \{q_2\}$
  - $\delta(q_2, 0) = \emptyset$, $\delta(q_2, 1) = \{q_3\}$, $\delta(q_2, \epsilon) = \emptyset$
  - $\delta(q_3, 0) = \{q_3\}$, $\delta(q_3, 1) = \{q_3\}$, $\delta(q_3, \epsilon) = \emptyset$
- $\epsilon$-Closures:
  - $E(q_0) = \{q_0\}$
  - $E(q_1) = \{q_1, q_2\}$
  - $E(q_2) = \{q_2\}$
  - $E(q_3) = \{q_3\}$

### 4.2 Reachable Powerset States (6 of 16 States)
Total powerset size: $2^4 = 16$ states.
Lazy reachability BFS starting from $s' = E(q_0) = \{q_0\}$:
1. $S_0 = \{q_0\}$ (Start):
   - On $0 \to E(\delta(q_0, 0)) = E(\{q_0\}) = \{q_0\} = S_0$
   - On $1 \to E(\delta(q_0, 1)) = E(\{q_0, q_1\}) = \{q_0, q_1, q_2\} = S_1$
2. $S_1 = \{q_0, q_1, q_2\}$:
   - On $0 \to E(\{q_0, q_2\}) = \{q_0, q_2\} = S_2$
   - On $1 \to E(\{q_0, q_1, q_3\}) = \{q_0, q_1, q_2, q_3\} = S_3$
3. $S_2 = \{q_0, q_2\}$:
   - On $0 \to E(\{q_0\}) = \{q_0\} = S_0$
   - On $1 \to E(\{q_0, q_1, q_3\}) = \{q_0, q_1, q_2, q_3\} = S_3$
4. $S_3 = \{q_0, q_1, q_2, q_3\}$ (Accept, contains $q_3$):
   - On $0 \to E(\{q_0, q_2, q_3\}) = \{q_0, q_2, q_3\} = S_4$
   - On $1 \to E(\{q_0, q_1, q_3\}) = \{q_0, q_1, q_2, q_3\} = S_3$
5. $S_4 = \{q_0, q_2, q_3\}$ (Accept, contains $q_3$):
   - On $0 \to E(\{q_0, q_3\}) = \{q_0, q_3\} = S_5$
   - On $1 \to E(\{q_0, q_1, q_3\}) = \{q_0, q_1, q_2, q_3\} = S_3$
6. $S_5 = \{q_0, q_3\}$ (Accept, contains $q_3$):
   - On $0 \to E(\{q_0, q_3\}) = \{q_0, q_3\} = S_5$
   - On $1 \to E(\{q_0, q_1, q_3\}) = \{q_0, q_1, q_2, q_3\} = S_3$

### 4.3 Pruned Unreachable States (10 States)
The following 10 theoretical subsets are never enqueued because no transition sequence from $\{q_0\}$ leads to them:
$$\emptyset, \{q_1\}, \{q_2\}, \{q_3\}, \{q_0, q_1\}, \{q_1, q_2\}, \{q_1, q_3\}, \{q_2, q_3\}, \{q_0, q_1, q_3\}, \{q_1, q_2, q_3\}$$
Pruning these 10 states reduces the visual and operational complexity of the recognizer by 62.5%.
