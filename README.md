# Ritangle 2023 - Stage 3 Solution + Write-up

Upload of my solution to the final question ([Stage 3 Question](https://meirezblobs.blob.core.windows.net/f6ea1a95-8924-4c0c-9f88-08dbfd70a5db/Stage%203%20Question.pdf)) of the Ritangle 2023 mathematics competition. I reframed the question as a linear integer optimisation problem and solved it using Google OR-Tools' CP-SAT Solver.

The solution found was optimal and earnt the Tiffin School team a runner-up position: https://mei.org.uk/ritangle-2023-champions.

## Question Description

The final stage question was a constrained combinatorial optimisation problem.
The task was to find the optimal scheduling of a *jamboree* chess tournament such that the detriment given was minimised.

In a *jamboree* chess tournament, $N$ teams, of $B$ players each, play $R$ rounds, of $B$ boards each. Within a team, players are ordered by strength (board 1 = strongest).

### Constraints

1. Nobody plays the same opponent twice, nor twice against opponents from the same team.
2. Nobody plays a team-mate.
3. Each pair of teams meets either $\left\lfloor \dfrac{RB}{N-1} \right\rfloor$ or $\left\lceil \dfrac{RB}{N-1} \right\rceil$ times.
4. On any given board, at most one up-float or down-float per round.
5. No player has more than one up-float or more than one down-float (across all rounds).
6. All up-floats play as White.
7. Per player, blacks and whites played differ by at most 1.
8. Per team, over all rounds, blacks and whites played differ by at most 1.

### Objective Functions

The total detriment $Q$ is the sum of three individual detriment measures:

$$Q = Q_X + Q_Y + Q_Z$$

---

#### $Q_X$: Balance of White/Black Games per Team per Round

$$Q_X = \sum_{i=1}^{N} \sum_{k=1}^{R} \left| w_{ik} - b_{ik} \right|$$

Where:
- $w_{ik}$ = number of white games for team $i$ in round $k$
- $b_{ik}$ = number of black games for team $i$ in round $k$

---

#### $Q_Y$: Balance of Up-Floats and Down-Floats per Team

$$Q_Y = \sum_{i=1}^{N} \left| \sum_{k=1}^{R} u_{ik} - \sum_{k=1}^{R} d_{ik} \right|$$

Where:
- $u_{ik}$ = number of up-floats for team $i$ in round $k$
- $d_{ik}$ = number of down-floats for team $i$ in round $k$

---

#### $Q_Z$: Even Distribution of White Games Across Boards

$$Q_Z = \sum_{i=1}^{N} \left| 1 - \frac{4}{R B (B + 1)} \sum_{l=1}^{B} l w_{il} \right|$$

Where:
- $w_{il}$ = number of white games for the player on board $l$ of team $i$
- The target board count for whites is $\frac{R}{2} \cdot \frac{B+1}{2} \cdot B$, and the factor $\frac{4}{R B (B+1)}$ normalises this to $1$