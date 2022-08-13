# Constrain-Satisfaction

My program is a generalized constraint satisfaction problem solver applied to two different problem spaces: (a) map coloring and (b) circuit board building. The main CSP solver for both programs is a general backtracking algorithm, and each invokes three heuristics: minimum remaining value, degree heuristic, and least constraining value. They also both leverage an arc consistency algorithm (AC3).

I began with the map problem. The task was to color a map (in this case of Australia) such that no neighboring regions are the same color. I first wrote the backtracking algorithm. It picks a variable, picks a value, and checks if assigning that value to that variable is allowed, taking into account the other variables that have already been assigned. If it is allowed, then it recurses and moves on to the next variable, otherwise it undoes that assignment and chooses a new value for the same variable.

I then implemented some heuristics to help the CSP choose the most advantageous variable to pick a value for next. The first, the minimum remaining value heuristic simply chooses the variable that has the fewest remaining potential values left. The second, the degree heuristic, elects the variable that is involved in the largest number of constraints on other unassigned variables. These heuristics are used interchangeably, or, the degree heuristic can be used as a tie breaker for the minimum remaining value heuristic.

Next, I implemented a heuristic to choose the best next possible value to try assigning to the current variable of choice. This is colloquially known as the least constraining value heuristic. It chooses the value that rules out the smallest number of values in variables connected to the current variable by constraints. With these heuristics implemented, the algorithm was choosing values and variables intelligently.

To finish off the map problem, I implemented an arc consistency method that forward-checks to prune inconsistent values from variables' domains before those variables are even considered for assignment. In this way, the algorithm can avoid excess computational cost and also foresee potential failures before it's costly to backtrack.

I then moved on to the circuit board problem. I implemented an identical backtracking algorithm, arc consistency method, and minimum remaining value heuristic, while I had to make some slight changes to the degree heuristic and least constraining value heuristics to account for the novel problem space.
