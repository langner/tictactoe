"""An analysis of tic-tac-toe.

The goal here is to simply iterate over all possible valid states in the
game of tic-tac-toe and perform some basic analyses such the number of
unique valid states and optimal moves for each state.

This implementation uses no classes, which would structure the code more,
although Python lists are flexible enough to make this imperative version
quite terse and easy to understand.

A state is represented by a tuple with nine integer values -- 0, 1 or 2,
where zero means a square is unoccupied and 1/2 denotes a player. We also
pass around wich player's turn it is for convenience, but this could be
derived from the state (sum, modulo 2, plus one).

There is no player code here, although it would be easy to add it. 
"""

def get_child_states(state, turn):
    """Get all possible new states for a given state and turn."""
    for ic, c in enumerate(state):
        if c == 0:
            yield tuple(state[:ic] + (turn,) + state[ic+1:])

def check_won(state, turn):
    """Check if state is won on this turn."""
    streak = (turn,) * 3
    rows = [state[3*i:3*(i+1)] for i in range(3)]
    cols = [state[i::3] for i in range(3)]
    for i in range(3):
        if (rows[i] == streak) or (cols[i] == streak):
            return True
    if rows[0][0] == rows[1][1] == rows[2][2] == turn:
        return True
    if rows[0][2] == rows[1][1] == rows[2][0] == turn:
        return True
    return False

# The root node is all zeros, and the tree is implemented by lists
# containing states and indices for children and parents.
root = (0,) * 9
states = [root]
children = [[]]
parents = [[]]

# Keep track of which player's turn it is for each state.
turn = [1]

# Keep track of whether a state is finished (no more possible moves),
# is a draw or won by either player (zero means undetermined). Later,
# we will propogate these values up the tree to determine them for
# each state given optimal moves for each state.
finished = [False]
draw = [False]
won = [0]

# Iterate over all possible states using a FIFO queue.
queue = [0]
while len(queue) > 0:

    i = queue.pop(0)
    for child in get_child_states(states[i], turn[i]):

        if not child in states:

            ic = len(states)
            states.append(child)
            children.append([])
            parents.append([i])
            turn.append((turn[i] - 1) or 2)
            won.append(turn[i] * check_won(child, turn[i]))
            finished.append(won[ic] != 0 or child.count(0) == 0)
            draw.append(finished[ic] and won[ic] == 0)

            if not finished[ic] and won[ic] == 0:
                queue.append(ic)

        else:
            ic = states.index(child)
            parents[ic].append(i)
        children[i].append(ic)

# This list will hold all optimal moves for a given state.
optimal = [None] * len(states)

# Propogate draws/wins from the bottom of the tree, which means we
# need to iterate backwards over the list of states, whose order
# will guaranty there is never an undetermined state.
for istate in range(len(states))[::-1]:

    if finished[istate] or won[istate] != 0:
        continue

    winning = [ic for ic in children[istate] if won[ic] == turn[istate]]
    if len(winning) > 0:
        won[istate] = turn[istate]
        optimal[istate] = winning
    elif all([won[ic] == ((turn[istate] - 1) or 2) for ic in children[istate]]):
        won[istate] = (turn[istate] - 1) or 2
    else:
        draws = [ic for ic in children[istate] if draw[ic]]
        if len(draws) > 0:
            draw[istate] = True
            optimal[istate] = draws
        else:
            print "Found a node with undetermined state"
            print "That should not happend"
            print "State:", states[istate]

# Some simple testing.
assert won[states.index((1,1,1,2,0,0,2,0,0))] == 1
assert won[states.index((1,2,0,1,0,2,1,0,0))] == 1
assert won[states.index((1,2,0,2,1,0,0,0,1))] == 1

print "Total number of states:", len(states)
print "Total number of drawn states:", sum(draw)
print "Total number of won states for player 1:", len([w for w in won if w == 1])
print "Total number of won states for player 2:", len([w for w in won if w == 2])

print "Root state is drawn:", draw[0]
print "Number of optimal moves in root state:", len(optimal[0])
print "Avg. number of optimal in second state: %.2f" % (1.0 * sum([len(optimal[i]) for i in optimal[0]]) / len(optimal[0]))
