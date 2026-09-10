import math
import pandas as pd

from ortools.sat.python import cp_model

N = 12
B = 10
R = 3

games_each = [math.floor((R*B)//(N-1)), math.ceil((R*B)/(N-1))]
max_floats = 2 + math.floor((R*B) // (2*N))
model = cp_model.CpModel()

def var_str(team_num, board_num, round_num, varType=0):
    name = "T" + str(team_num) + "B" + str(board_num) + "R" + str(round_num)
    if varType == 0:
        return name + "PAIR"
    elif varType == 1:
        return name + "SIDE"
    elif varType == 2:
        return name + "BOARD"
    elif varType == 3:
        return name + "INDEX"


df = pd.DataFrame(columns=['Team','Player','Round/Side', 'IntVar'])
for t in range(N):
    for b in range(B):
        for r in range(R):
            enemy = model.NewIntVar(0, N-1, var_str(t,b,r, varType=0))
            side = model.NewBoolVar(var_str(t,b,r, varType=1))
            board = model.NewIntVar(0, B-1, var_str(t,b,r, varType=2))
            enemy_index = model.NewIntVar(0, N*B-1, var_str(t,b,r, varType=3))

            model.Add(enemy_index == enemy*B + board)
            model.Add(enemy != t) # Can't play own team
            is_upfloat = model.NewBoolVar("is_upfloat")
            model.Add(board < b).OnlyEnforceIf(is_upfloat)
            model.Add(board >= b).OnlyEnforceIf(is_upfloat.Not())
            model.Add(side == True).OnlyEnforceIf(is_upfloat) # Force white if up-float

            df.loc[t*B*R*4 + b*R*4 + r] = [t,b,r, enemy]
            df.loc[t*B*R*4 + b*R*4 + r + R] = [t,b,r+R, side]
            df.loc[t*B*R*4 + b*R*4 + r + 2*R] = [t,b,r+2*R, board]
            df.loc[t*B*R*4 + b*R*4 + r + 3*R] = [t,b,r+3*R, enemy_index]

        
df.sort_index(inplace=True)
print(df.head(10)) 
print(df.shape)


##!SECTION Constraints

for i in range(N):
    for j in range(B): # For each player
        player_start_index = i*B*R*4 + j*R*4
        games = df.iloc[player_start_index:player_start_index + R]["IntVar"].tolist()
        model.AddAllDifferent(games) # No player plays the same team twice

        is_white = df.iloc[player_start_index + R:player_start_index + 2*R]["IntVar"].tolist()
        model.AddForbiddenAssignments(is_white, [(0,0,0), (1,1,1)]) # No player plays all white or all black

        enemy_board = df.iloc[player_start_index + 2*R:player_start_index + 3*R]["IntVar"].tolist()

        # No player can up or downfloat more than once
        if N % 2 == 1:
            if j % 2 == 0: # Down float
                    model.Add(sum(enemy_board) <= R*j + 1)
            else: # Up float
                    model.Add(sum(enemy_board) >= R*j - 1)

        for e in enemy_board:
            if N % 2 == 0:
                model.Add(e == j) # Players must player on their own board
            else:
                # Players must player on either their own board, or up/down float
                if j % 2 == 0: # Down 
                    model.Add(e <= j+1)
                    model.Add(e >= j)
                else: # Up float
                    model.Add(e >= j-1)
                    model.Add(e <= j)


for r in range(R):
    for b in range(B):
        enemy_boards = df.query("Player == " + str(b) + " & `Round/Side` == " + str(r+2*R))["IntVar"].tolist()
        if N % 2 == 1: # Only one upfloat or downfloat per round per board
            if b % 2 == 0:
                model.Add(b*N + 1 == sum(enemy_boards)) # 1 Downfloat
            if b % 2 == 1:
                model.Add(b*N - 1 == sum(enemy_boards)) # 1 Upfloat
                    

# Ensures players play each other
for r in range(R):
    enemy_index = df.query("`Round/Side` == " + str(r+3*R))["IntVar"].tolist()
    sides = df.query("`Round/Side` == " + str(r+R))["IntVar"].tolist()
    model.AddInverse(enemy_index, enemy_index)

    # Ensures one white, one black
    for index, side in zip(enemy_index, sides):
            opposite_side = model.NewBoolVar("opposite_side")
            model.Add(opposite_side != side)
            model.AddElement(index, sides, opposite_side)

y = []

# Each team plays each other team games_each[0] to games_each[1] times
for t in range(N):
    number_of_plays_per_team = {
        i: model.NewIntVar(games_each[0], games_each[1], f"{t}count_of_plays_against{i}")
        for i in range(0,N)
    }
    games = df.query("Team == " + str(t) + "& `Round/Side` < 3")["IntVar"].tolist()
    for key, val in number_of_plays_per_team.items():
        if key != t:
            count = []
            for enemy_team in games:
                is_equal = model.NewBoolVar("is_equal")
                model.Add(enemy_team == key).OnlyEnforceIf(is_equal)
                model.Add(enemy_team != key).OnlyEnforceIf(is_equal.Not())
                count.append(is_equal)
            model.Add(val == sum(count))


    # Contrains max upfloats and downfloats
    number_of_upfloats_per_team = model.NewIntVar(0, max_floats, f"{t}count_of_upfloats")
    number_of_downfloats_per_team = model.NewIntVar(0, max_floats, f"{t}count_of_downfloats")

    upfloat_count = []
    downfloat_count = []
    for b in range(B):
        enemy_boards = df.query("Team == " + str(t) + " & Player == " + str(b) + " & `Round/Side` > 5" + " & `Round/Side` < 9")["IntVar"].tolist()
        for e in enemy_boards:
            is_upfloat = model.NewBoolVar("is_upfloat")
            model.Add(e < b).OnlyEnforceIf(is_upfloat)
            model.Add(e >= b).OnlyEnforceIf(is_upfloat.Not())
            upfloat_count.append(is_upfloat)

            is_downfloat = model.NewBoolVar("is_downfloat")
            model.Add(e > b).OnlyEnforceIf(is_downfloat)
            model.Add(e <= b).OnlyEnforceIf(is_downfloat.Not())
            downfloat_count.append(is_downfloat)

    model.Add(number_of_upfloats_per_team == sum(upfloat_count))
    model.Add(number_of_downfloats_per_team == sum(downfloat_count))
    
    y.append(model.NewIntVar(0, max_floats, "y"+str(t)))
    model.Add(y[t] >= number_of_upfloats_per_team - number_of_downfloats_per_team)
    model.Add(y[t] >= -(number_of_upfloats_per_team - number_of_downfloats_per_team))

    # Each is white for half their games
    isWhite = df.query("Team == " + str(t) + "& `Round/Side` > 2" + "& `Round/Side` < 6")["IntVar"].tolist()
    model.Add(sum(isWhite) == R*B//2)

##!SECTION Objectives

# X
x = []
for t in range(N):
    for r in range(R):
        per_team_per_round = df.query("Team == " + str(t) + "& `Round/Side` == " + str(r+3))["IntVar"].tolist()
        x.append(model.NewIntVar(0, B, "x" + str(t) + str(r)))
        model.Add(x[t*R + r] >= B - 2*sum(per_team_per_round))
        model.Add(x[t*R + r] >= -(B - 2*sum(per_team_per_round)))

x_upper_bound = N*R*B
x_sum = model.NewIntVar(0, x_upper_bound, "x_sum")
model.Add(x_sum == cp_model.LinearExpr.Sum(x))

# Y
y_upper_bound = N*max_floats
y_sum = model.NewIntVar(0, y_upper_bound, "y_sum")
model.Add(y_sum == cp_model.LinearExpr.Sum(y))

# Z
z = []
for t in range(N):
    side_across_rounds = df.query("Team == " + str(t) + "& `Round/Side` > 2" + "& `Round/Side` < 6")["IntVar"].tolist()
    weighted_sum = cp_model.LinearExpr.WeightedSum(side_across_rounds, [4*(i//R) + 4 for i in range(R*B)])
    z.append(model.NewIntVar(0, R*B*(B+1), "z" + str(t)))
    model.Add(z[t] >= (R*B*(B+1)) - weighted_sum)
    model.Add(z[t] >= -((R*B*(B+1)) - weighted_sum))

z_upper_bound = N*R*B*(B+1)
z_sum = model.NewIntVar(0, z_upper_bound, "z_sum")
model.Add(z_sum == cp_model.LinearExpr.Sum(z))

q_upper_bound = R*B*(B+1)*(x_upper_bound + y_upper_bound) + z_upper_bound
q = model.NewIntVar(0, q_upper_bound, "q")
model.Add(q == R*B*(B+1)*x_sum + R*B*(B+1)*y_sum + z_sum)
model.Minimize(q)

##!SECTION Solve

teams = "ABCDEFGHIJKL"

def str_player(team, board):
    real_board = board + 1
    if real_board < 10:
        str_board = "0" + str(real_board)
    else:
        str_board = str(real_board)
    return teams[team] + "." + str_board

player2_team_lookup = {}
player2_board_lookup = {}
player1_side_lookup = {}
for r in range(R):
    for b in range(B):
        for t in range(N):
            player2_team_lookup[(t,b,r)] = df.query("Player == " + str(b) + " & `Round/Side` == " + str(r) + " & Team == " + str(t))["IntVar"].tolist()[0]
            player2_board_lookup[(t,b,r)] = df.query("Player == " + str(b) + " & `Round/Side` == " + str(r+2*R) + " & Team == " + str(t))["IntVar"].tolist()[0]
            player1_side_lookup[(t,b,r)] = df.query("Player == " + str(b) + " & `Round/Side` == " + str(r+R) + " & Team == " + str(t))["IntVar"].tolist()[0]

def format_output(solver):
  for r in range(R):
      pairs = []
      for b in range(B):
          for t in range(N):
              player1 = str_player(t, b)
              player2_team = solver.Value(player2_team_lookup[(t,b,r)])
              player2_board = solver.Value(player2_board_lookup[(t,b,r)])
              player2 = str_player(player2_team, player2_board)
              player1_side = solver.Value(player1_side_lookup[(t,b,r)])
              pairs.append(",".join([player1, player2][::player1_side*2-1]))
      
      pairs = list(set(pairs))
      pairs.sort(key=lambda x: int(x.split(',')[0].split('.')[1]))
      for p in pairs:
          print(str(r+1) + "," + p)

class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self):#, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        #self.__variables = variables
        self.__solution_count = 0

    def on_solution_callback(self):
        self.__solution_count += 1
        print("X:", sum([self.Value(i) for i in x]))
        print("Y:", sum([self.Value(i) for i in y]))
        print("Z:", sum([self.Value(i) for i in z]))
        print("Q:", self.Value(q))
        print("Q Real:", self.Value(q) / (R*B*(B+1)))
        print("Solution:", self.__solution_count)
        # format_output(self)
        # for v in self.__variables:
        #     print(f"{v}={self.Value(v)}", end=" ")
        # print()

    def solution_count(self):
        return self.__solution_count

# Create a solver and solve.
solver = cp_model.CpSolver()
solution_printer = VarArraySolutionPrinter()
solver.parameters.max_time_in_seconds = 120.0
# # Enumerate all solutions.
# solver.parameters.enumerate_all_solutions = True

print("Solving...")
status = solver.Solve(model, solution_printer)
print(solver.StatusName(status))
print(f"Number of solutions found: {solution_printer.solution_count()}")

##!SECTION Output
            
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    format_output(solver)


    print("X:", sum([solver.Value(i) for i in x]))
    print("Y:", sum([solver.Value(i) for i in y]))
    print("Z:", sum([solver.Value(i) for i in z]))
    print("Q:", solver.Value(q))
    print("Q Real:", solver.Value(q) / (R*B*(B+1)))
