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

def display(values):
  """This will display the values and the grid on the console in the traditional 2-D box formats"""
  if values == False:
    print ( "Contradiction reached! Please check grid." ) # values was returned as false from other functions
  else:
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

def check_solve(grid):
  """This solve will thoroughly check the grid to ensure that there no multiple solutions. 
     If multiple solutions are found, returns 'multi'"""
  return fast_solve(parse_grid(grid))

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
        rand_values = list(values[s])
        while len(rand_values) > 0:
          d = rand_values[randrange(0, len(rand_values))]	  
          values_copy = deepcopy(values)
          solved = rand_solve(assign(values_copy, s, d))
          if solved:
            return solved
          else:
            rand_values.remove(d)
      else:
        rand_squares.remove(s)

# This generates a blank grid
blank = '.' * (n**4)

# A list of hard difficulty Sudokus, not solvable with only constraint propagation
hard = [ '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......', 
         '.....6....59.....82....8....45........3........6..3.54...325..6..................' ]

# A list of easy difficulty Sudokus, solvable only relying on constraint propagation
easy = [ '167000000050600047000300009641057000800060005000980716700008000490006050000000671',
         '..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..',
	 '003020600900305001001806400008102900700000008006708200002609500800203009005010300' ]

def choose_grid():
  diff = input('Choose Sudoku difficulty (Sudoku number optional) (ex: e1 = easy1, h2 = hard2, h = hard[random], nothing for empty Sudoku): ')
  if 'e' in diff:
    found_grid = ''.join([easy[i] for i in range(0, len(easy)) if str(i+1) in diff])
    if not found_grid:
      return easy[randrange(0, len(easy))]
    else:
      return found_grid
  elif 'h' in diff:
    found_grid = ''.join([hard[i] for i in range(0, len(hard)) if str(i+1) in diff])
    if not found_grid:
      return hard[randrange(0, len(hard))]
    else:
      return found_grid
  else:
    return blank

def interact():
  while True:
    grid = choose_grid()
    display(convert_grid(grid))
    choice = input('Press Enter to Solve Grid, Type r to select another Sudoku, or q to Quit: ')
    if choice == 'q':
      break
    elif not choice:
      flags = input('Include optional flags?\n'\
                    'd = display steps\n'\
                    'c = check solve\n'\
                    'f = fast solve\n'\
                    'r = random solve\n')
      if 'd' in flags:
        global verbose
        verbose = True
      if 'c' in flags:
        solve = check_solve(parse_grid(grid))
      elif 'r' in flags:
        solve = rand_solve(parse_grid(grid))
      else:
        solve = fast_solve(parse_grid(grid))
      display(solve)
      break
    else:
      print()
interact()
