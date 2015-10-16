"""Terminology and Definitions:
size n - Dimensions for the Sudoku, typically n=3 but can be resized 
Square - Individual block occupied by each value 
Unit - a collection of n^2 squares either in the same box, column or row as a particular Square, that are filled with permutations of values 0 to 2^n - 1  
Peer -  The squares belonging to the same unit as the Square, there are 2*(n^2 -1) + 2^(n-1) peers for each Square
Grid - Synonomous with the Sudoku board, grid represent the current Sudoku board"""

import string

from random import randrange
from copy import deepcopy
from time import sleep

# Verbose flag
verbose = False

# Flag used for the generation of Sudokus
generating = False
multiple = False 

# Declare the necessary global variables
n = 3
digits = []
rows = []
cols = []
squares = []
unitList = []
units = {}
peers = {}

# Template for blank/empty grid
blank = ''

# A list of hard difficulty Sudokus, not solvable with only constraint propagation
hard = [ '4 . . . . . 8 . 5 . 3 . . . . . . . . . . 7 . . . . . . 2 . . . . . 6 . . . . . 8 . 4 . . . . . . 1 . . . . . . . 6 . 3 . 7 . 5 . . 2 . . . . . 1 . 4 . . . . . .',
         '4 0 9 0 6 0 0 1 0 0 0 0 0 0 7 9 0 8 0 0 0 5 0 8 0 0 0 0 0 0 4 0 0 0 6 2 0 7 0 0 0 0 0 9 0 2 6 0 0 0 9 0 0 0 0 0 0 3 0 5 0 0 0 3 0 5 7 0 0 0 0 0 0 1 0 0 2 0 5 0 4',
         '0 0 0 2 0 0 0 3 0 6 0 5 0 9 0 0 1 0 0 0 0 0 5 0 9 0 0 0 5 7 8 0 0 6 0 0 8 0 6 0 0 0 4 0 1 0 0 1 0 0 5 7 9 0 0 0 8 0 7 0 0 0 0 0 7 0 0 3 0 1 0 9 0 9 0 0 0 6 0 0 0',
         '0 0 0 0 7 4 3 1 6 0 0 0 6 0 3 8 4 0 0 0 0 0 0 8 5 0 0 7 2 5 8 0 0 0 3 4 0 0 0 0 3 0 0 5 0 0 0 0 0 0 2 7 9 8 0 0 8 9 4 0 0 0 0 0 4 0 0 8 5 9 0 0 9 7 1 3 2 6 4 8 5'  ]

# A list of easy difficulty Sudokus, solvable only relying on constraint propagation
easy = [ '1 6 7 0 0 0 0 0 0 0 5 0 6 0 0 0 4 7 0 0 0 3 0 0 0 0 9 6 4 1 0 5 7 0 0 0 8 0 0 0 6 0 0 0 5 0 0 0 9 8 0 7 1 6 7 0 0 0 0 8 0 0 0 4 9 0 0 0 6 0 5 0 0 0 0 0 0 0 6 7 1',
         '8 3 . . . . . 1 . . . 4 2 . 8 . . 6 . . 2 3 . 5 8 9 . . . 5 . . 6 . 8 . 9 . . 5 . 7 . . 3 . 6 . 9 . . 7 . . . 5 6 8 . 9 1 . . 7 . . 1 . 2 5 . . . 2 . . . . . 6 9',
         '0 0 3 0 2 0 6 0 0 9 0 0 3 0 5 0 0 1 0 0 1 8 0 6 4 0 0 0 0 8 1 0 2 9 0 0 7 0 0 0 0 0 0 0 8 0 0 6 7 0 8 2 0 0 0 0 2 6 0 9 5 0 0 8 0 0 2 0 3 0 0 9 0 0 5 0 1 0 3 0 0',
         '6 0 0 9 2 0 0 0 5 0 0 5 7 8 0 9 6 0 0 1 0 0 0 5 0 0 0 5 0 0 6 0 0 0 8 2 0 0 0 0 0 0 0 0 0 8 6 0 0 0 9 0 0 3 0 0 0 4 0 0 0 3 0 0 4 3 0 7 8 5 0 0 7 0 0 0 1 3 0 0 9',
         '5 . . 2 6 . . 1 . . 2 . . . 7 5 . . . . . . . 5 6 . . . . . . 8 . 2 3 4 8 . . 6 4 3 . . 5 4 9 3 . 2 . . . . . . 4 3 . . . . . . . 9 1 . . . 2 . . 6 . . 7 4 . . 3'  ]

# A list of multi-solution Sudokus, checkable via check_solve
multi = [ '9 0 6 0 7 0 4 0 3 0 0 0 4 0 0 2 0 0 0 7 0 0 2 3 0 1 0 5 0 0 0 0 0 1 0 0 0 4 0 2 0 8 0 6 0 0 0 3 0 0 0 0 0 5 0 3 0 7 0 0 0 5 0 0 0 7 0 0 5 0 0 0 4 0 5 0 1 0 7 0 8',
          '. 8 . . . 9 7 4 3 . 5 . . . 8 . 1 . . 1 . . . . . . . 8 . . . . 5 . . . . . . 8 . 4 . . . . . . 3 . . . . 6 . . . . . . . 7 . . 3 . 5 . . . 8 . 9 7 2 4 . . . 5 .',
          '. . . . . 6 . . . . 5 9 . . . . . 8 2 . . . . 8 . . . . 4 5 . . . . . . . . 3 . . . . . . . . 6 . . 3 . 5 4 . . . 3 2 5 . . 6 . . . . . . . . . . . . . . . . . .'  ] 

def initialize():
  """This initializes the necessary global variables accordingly"""
  global n
  global digits
  global rows
  global cols
  global squares
  global unitList
  global units
  global peers
  global blank
  # Dimensions of Sudoku specificed by size n
  n = int(input('Enter the desired size n: '))
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
  # Generate the blank grid according to specified dimensions
  blank = '. ' * (n**4 - 1) + '.'


def cross(A, B):
  # Returning the Cross Product of elements in A and of elements in B as a list
  return [a+b for a in A for b in B]

def parse_values(values):
  """This parses the dict values and assign all of its possible values in the format of {square: values}. Otherwise, this will return false"""
  new_values = dict((s, list(digits)) for s in squares)
  for s,d in values.items():
    d = ''.join(d) #This is necessary as values[s] may be a list with len == 1, but we need the string inside it
    if d in digits and not assign(new_values, s, d):
      return False #This is an indication that we cannot assign digit d into square s
  return new_values

def grid_values(grid):
  """This converts grid into a dict of {square: char} with '.' or '0' for empty squares and returns it"""
  sudoku_grid = []
  s_val = ''
  for c in grid:
    if c in digits:
      s_val += c
    elif c in '.0':
      s_val += ' '
    elif c == ' ':
      sudoku_grid.append(s_val)
      s_val = ''
  sudoku_grid.append(s_val) # Need to append last value in string to grid/list
  assert len(sudoku_grid) == (n**4)
  return dict(zip(squares, sudoku_grid))

#TODO: values_grid necessary? Currently not being called/used
def values_grid(values):
  """Reverse of grid_values + parse_values, taking a dict of values as parameter and returns the sudoku board (grid) as a string"""
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
      
def gen_values():
  """This will generate and return a list of possible values for a grid with a unique solution."""
  # TODO: Implement more sophisticated generator algorithms, allowing for faster performance as well as varying difficulty
  # The absolute mininmum of initial numbers in a Sudoku before reaching multiple solutions is 17
  global generating
  global multiple
  generating = True
  values = rand_solve(parse_values(grid_values(blank)))
  rand_squares = list(squares)
  while len(rand_squares) > 0:
    s = rand_squares[randrange(0, len(rand_squares))]
    removed_d = values[s]
    values[s] = ' '
    finished = check_solve(parse_values(values))
    if finished == 'multi':
      if not multiple:
        values[s] = removed_d
      generating = False
      multiple = False
      return values
    rand_squares.remove(s)

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
    min_vals, s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)
    for d in values[s]:
      values_copy = deepcopy(values)
      solved = fast_solve(assign(values_copy, s, d))
      if solved:
        return solved

def rand_solve(values):
  """A clone of fast_solve utilizing brute force on random squares instead of min_vals squares."""
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

def choose_grid():
  global multiple
  diff = input('Choose Sudoku difficulty (ex: e1 = easy1, h2 = hard2, h = hard[random], nothing for empty Sudoku):\n'\
               'Enter q at anytime to quit\n')
  if 'q' in diff:
    return False
  if 'e' in diff:
    for i in range(0, len(easy)):
      if str(i+1) in diff:
        return grid_values(easy[i])
    return grid_values(easy[randrange(0, len(easy))])
  elif 'h' in diff:
    for i in range(0, len(hard)):
      if str(i+1) in diff:
        return grid_values(hard[i])
    return grid_values(hard[randrange(0, len(hard))])
  elif 'm' in diff:
    for i in range(0, len(multi)):
      if str(i+1) in diff:
        return grid_values(multi[i])
    multiple = True
    return gen_values()
  elif 'g' in diff:
    print( "Generated Sudoku" )
    return gen_values()
  else:
    return grid_values(blank)

def interact():
  while True:
    initialize()
    grid = choose_grid()
    if not grid:
      break
    display(grid)
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
        solve = check_solve(parse_values(grid))
      elif 'r' in choice:
        solve = rand_solve(parse_values(grid))
      else:
        solve = fast_solve(parse_values(grid))
      display(solve)
      break
    else:
      print()

interact()
