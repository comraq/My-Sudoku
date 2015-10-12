"""Terminology and Definitions:
size n - Dimensions for the Sudoku, typically n=3 but can be resized 
Square - Individual block occupied by each value 
Unit - a collection of n^2 squares either in the same box, column or row as a particular Square, that are filled with permutations of values 0 to 2^n - 1  
Peer -  The squares belonging to the same unit as the Square, there are 2*(n^2 -1) + 2^(n-1) peers for each Square
Grid - Synonomous with the Sudoku board, grid represent the current Sudoku board
"""

import string

from random import randrange
from copy import deepcopy
from time import sleep

# Dimensions of Sudoku specificed by size n
n = 3 # n = int(input('Enter the desired size n: '))

# Verbose flag
verbose = False

# Flag raised while in process of generating a Sudoku
generating = False

def cross(A, B):
  # Returning the Cross Product of elements in A and of elements in B as a list
  return [a+b for a in A for b in B]

digits = [ str(i+1) for i in range(n**2) ]
rows = [ r for r in string.ascii_letters[:n**2] ]
cols = rows
# Define squares as a list for Squares
squares = cross(rows, cols)
unitList = ([cross(rows, c) for c in cols] +
            [cross(r, cols) for r in rows] +
	    [cross(rb, cb) for rb in [ ''.join( rows[i*n : (i+1)*n] ) for i in range(n) ] for cb in [ ''.join( cols[i*n : (i+1)*n] ) for i in range(n) ]])
# Define units and peers as a list stored in a dict that can be accessed by using Square as the key
units = dict((s, [u for u in unitList if s in u]) for s in squares)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in squares)

def parse_grid(grid):
  """This converts grid into a dict holding its possible values in the format of {square: values}. Otherwise, this will return false"""
  # We start with all values being appropriate for each square
  values = dict((s, list(digits)) for s in squares)
  for s,d in grid_values(grid).items():
    if d in digits and not assign(values, s, d):
      return False #This is an indication that we cannot assign digit d into square s
  return values

def convert_grid(grid):
  """Same as parse grid except without any preliminary contraint propagation"""
  values = dict((s, list(digits)) for s in squares)
  for s,d in grid_values(grid).items():
    if not d in digits:
      values[s] = ' '
    else:
      values[s] = d
  return values
  
def grid_values(grid):
  """This converts grid into a dict of {square: char} with '.' or '0' for empty squares and returns it"""
  chars = [c for c in grid if c in digits or c in '.0']
  assert len(chars) == (n**4)
  return dict(zip(squares, chars))

def values_grid(values):
  """Reverse of grid_values + convert/parse_grid, taking a dict of values as parameter and returns the sudoku board (grid) as a string"""
  grid = ''
  for s in squares:
    if len(values[s]) > 1:
      grid += '.'
    else:
      grid += ''.join(values[s])
  return grid

def display(values):
  """This will display the values and the grid on the console in the traditional 2-D box formats"""
  if values != 'multi':
    width = 2 * max(len(values[s]) for s in squares) + 2 
    # line is the horizontal line separating the square units 
    line = '+'.join(['-' * (width * n)] * n)
    for r in rows:
      if r in [cols[i*n] for i in range(1,n)]:
        print( line )
      for c in cols:
        if c in [cols[i*n] for i in range(1,n)]:
          print( '|', end='')
        print( '('+' '.join(values[r+c])+')'+' '*(width - 2 - len(' '.join(values[r+c]))), end='')
      print()
    print( flush=True )
    sleep(.2)

def assign(values, s, d):
  """This will remove all values in each square s but leave only d and propagate any impact which this might have on the peers of the square.
  This will return the updated values, however if a contradiction is detected, this will return False"""
  other_values = list(values[s])
  other_values.remove(d)
  if all(eliminate(values, s, other_d) for other_d in other_values):
    return values
  else:
    return False

def eliminate(values, s, d):
  """This will eliminate d from the values of square s, ie from values[s]; will also progate its impact values or places < 2.
  There are 2 cases for which propagation will occur:
    Case 1) If a square s is reduced to only one value remaining_d, then we eliminate all instances of remaining_d in its peers.
    Case 2) If a unit has only one place for value d, then we will put it there and eliminate d from the peers in its other units.
  This will return values, however, if a contradiction is detected, this will return False"""
  if d not in values[s]:
    return values # Indicating that digit d was already eliminated from the possible values of square s
  values[s].remove(d)
  # Case 1) of propagation
  if len(values[s]) == 0:
    return False # This is a contradiction as we just removed the last value
  elif len(values[s]) == 1:
    remaining_d = ''.join(values[s])
    if not all(eliminate(values, peer_s, remaining_d) for peer_s in peers[s]):
      return False
  # Case 2) of propagation
  places = []
  for u in units[s]:
    places = [s for s in u if d in values[s]]
    if len(places) == 0:
      return False # This is a contradiction as there is no available place for this value in its units
    elif len(places) == 1:
      # Digit d only has one available place in its units, we will assign it there
      if not assign(values, places[0], d):
        return False
  return values

def check_solve(values):
  """This solve will thoroughly check the grid to ensure that there no multiple solutions. 
     If multiple solutions are found, returns 'multi' """
  if values is False:
    print( "check_solve values is empty" )
    return False # This indicates that a recursive call to this function failed and its time to try another digit from values
  if all(len(values[s]) == 1 for s in squares):
    return values # All squares have only one possibility for values, in other words, SOLVED!
  else:
    solutions = {}
    if verbose:
      display(values)
    rand_squares = list(squares)
    while len(rand_squares) > 0:
      s = rand_squares[randrange(0, len(rand_squares))]
      if len(values[s]) > 1:
        break
      rand_squares.remove(s)
    rand_values = list(values[s])
    while len(rand_values) > 0:
      d = rand_values[randrange(0, len(rand_values))]
      values_copy = deepcopy(values)
      solved = rand_solve(assign(values_copy, s, d))
      if solved:
        if verbose:
          print( "Found a Solution! s = %s, d = %s" % (s, d) )
          display(solved)
        if solutions:
          if not generating:
            print( "Multiple solutions found!" )
            display(solved)
            display(solutions)
          return 'multi'
        else:
          solutions = solved
      rand_values.remove(d)
    return solutions
      

def fast_solve(values):
  """Since we are using the brute force method by trying each value, we will use depth-first search and propagation for efficiency."""
  if values is False:
    return False # This indicates that a recursive call to this function failed and its time to try another digit from values
  if all(len(values[s]) == 1 for s in squares):
    return values # All squares have only one possibility for values, in other words, SOLVED!
  else:
    if verbose:
      display(values)
    # Chosing an unfilled square s with the fewest possible values
    min_number, s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)
    for d in values[s]:
      values_copy = deepcopy(values)
      solved = fast_solve(assign(values_copy, s, d))
      if solved:
        return solved

def rand_solve(values):
  """This is a clone of search, but this will generate a random solution instead."""
  if values is False:
    return False
  if all(len(values[s]) == 1 for s in squares):
    return values
  else:
    if verbose:
      display(values)
    rand_squares = list(squares)
    while len(rand_squares) > 0:
      s = rand_squares[randrange(0, len(rand_squares))]
      if len(values[s]) > 1:
        break
      rand_squares.remove(s)
    rand_values = list(values[s])
    while len(rand_values) > 0:
      d = rand_values[randrange(0, len(rand_values))]
      values_copy = deepcopy(values)
      solved = rand_solve(assign(values_copy, s, d))
      if solved:
        return solved
      else:
        rand_values.remove(d)

def gen_values():
  """This will generate and return a list of possible values for a grid at 3 difficulty levels: Easy, Normal or Hard all with unique solutions."""
  global generating
  generating = True
  values = rand_solve(parse_grid(blank))
  rand_squares = list(squares)
  while len(rand_squares) > 0:
    s = rand_squares[randrange(0, len(rand_squares))]
    rand_index = squares.index(s)
    removed_d = values[s]
    values[s] = digits
    finished = check_solve(parse_grid(values_grid(values)))
    if finished == 'multi':
      values[s] = removed_d
      generating = False
      return values
    rand_squares.remove(s)

# This generates a blank grid
blank = '.' * (n**4)

# A list of hard difficulty Sudokus, not solvable with only constraint propagation
hard = [ '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......',
         '409060010000007908000508000000400062070000090260009000000305000305700000010020504',
         '000200030605090010000050900057800600806000401001005790008070000070030109090006000',
         '000074316000603840000008500725800034000030050000002798008940000040085900971326485'  ]

# A list of normal difficulty Sudokus, with challenge level between those of easy and hard
normal = [ '600920005005780960010005000500600082000000000860009003000400030043078500700013009',
           '5..26..1..2...75.......56......8.2348..643..5493.2......43.......91...2..6..74..3'  ]

# A list of easy difficulty Sudokus, solvable only relying on constraint propagation
easy = [ '167000000050600047000300009641057000800060005000980716700008000490006050000000671',
	 '83.....1...42.8..6..23.589...5..6.8.9..5.7..3.6.9..7...568.91..7..1.25...2.....69',
         '003020600900305001001806400008102900700000008006708200002609500800203009005010300'  ]

# A list of multi-solution Sudokus, checkable via check_solve
multi = [ '906070403000400200070023010500000100040208060003000005030700050007005000405010708',
          '.8...9743.5...8.1..1.......8....5......8.4......3....6.......7..3.5...8.9724...5.',
          '.....6....59.....82....8....45........3........6..3.54...325..6..................'  ] 

def choose_grid():
  diff = input('Choose Sudoku difficulty (ex: e1 = easy1, h2 = hard2, h = hard[random], nothing for empty Sudoku):\n'\
               'Enter q at anytime to quit\n')
  if 'q' in diff:
    return False
  if 'e' in diff:
    found_grid = ''.join([easy[i] for i in range(0, len(easy)) if str(i+1) in diff])
    if not found_grid:
      return easy[randrange(0, len(easy))]
    else:
      return found_grid
  elif 'n' in diff:
    found_grid = ''.join([normal[i] for i in range(0, len(normal)) if str(i+1) in diff])
    if not found_grid:
      return normal[randrange(0, len(normal))]
    else:
      return found_grid
  elif 'h' in diff:
    found_grid = ''.join([hard[i] for i in range(0, len(hard)) if str(i+1) in diff])
    if not found_grid:
      return hard[randrange(0, len(hard))]
    else:
      return found_grid
  elif 'm' in diff:
    found_grid = ''.join([multi[i] for i in range(0, len(multi)) if str(i+1) in diff])
    if not found_grid:
      return multi[randrange(0, len(multi))]
    else:
      return found_grid
  elif 'g' in diff:
    print( "Generated Sudoku" )
    return values_grid(gen_values())
  else:
    return blank

def interact():
  while True:
    grid = choose_grid()
    if not grid:
      break
    display(convert_grid(grid))
    choice = input('Press Enter to Solve Grid or s to select another Sudoku:\n'\
                   'Include flags? (optional)\n'\
                   'd = display steps\n'\
                   'c = check solve\n'\
                   'f = fast solve\n'\
                   'r = random solve\n')
    if 'q' in choice:
      break
    elif not 's' in choice:
      if 'd' in choice:
        global verbose
        verbose = True
      if 'c' in choice:
        solve = check_solve(parse_grid(grid))
      elif 'r' in choice:
        solve = rand_solve(parse_grid(grid))
      else:
        solve = fast_solve(parse_grid(grid))
      display(solve)
      break
    else:
      print()

interact()
