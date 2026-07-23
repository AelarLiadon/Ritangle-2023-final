# Ritangle 2023 - Stage 3 Solution + Write-up

Upload of my solution to the final question ([Stage 3 Question](https://meirezblobs.blob.core.windows.net/f6ea1a95-8924-4c0c-9f88-08dbfd70a5db/Stage%203%20Question.pdf)) of the Ritangle 2023 mathematics competition. I reframed the question as a linear integer optimisation problem and solved it using Google OR-Tools' CP-SAT Solver.

The solution found was optimal and earnt the Tiffin School team a runner-up position: https://mei.org.uk/ritangle-2023-champions.

## Question Description

The final stage question was a constrained combinatorial optimisation problem.
The task was to find the optimal scheduling of a "jamboree" chess tournament such that the objective functions given were minimised.

In a ‘jamboree’ chess tournament, $N$ teams, of $B$ players each, play $R$ rounds, of $B$ boards each. 

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

# Solution Write-up
