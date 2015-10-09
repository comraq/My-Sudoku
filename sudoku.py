"""Terminology and Definitions:
size n - Dimensions for the Sudoku, typically n=3 but can be resized 
Square - Individual block occupied by each value 
Unit - a collection of n^2 squares either in the same box, column or row as a particular Square, that are filled with permutations of values 0 to 2^n - 1  
Peer -  The squares belonging to the same unit as the Square, there are 2*(n^2 -1) + 2^(n-1) peers for each Square
Grid - Synonomous with the Sudoku board, grid represent the current Sudoku board
"""

import string

n = int(input('Enter the desired size n: '))

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
  values = dict((s, digits) for s in squares)
  for s,d in grid_values(grid).items():
    if d in digits and not assign(values, s, d):
      print( "parse_grid returning False" )
      return False #This is an indication that we cannot assign digit d into square s
  return values

def grid_values(grid):
  """This converts grid into a dict of {square: char} with '.' for empty squares and returns it"""
  chars = [c for c in grid if c in digits or c == '.']
  assert len(chars) == (n**4)
  return dict(zip(squares, chars))

def display(values):
  """This will display the values and the grid on the console in the traditional 2-D box formats"""
  width = 1 + max(len(values[s]) for s in squares)  
  # line is the horizontal line separating the square units 
  line = '+'.join(['-' * (width * n)] * n)
  for r in rows:
    print( ''.join(values[r+c].center(width)+('|' if c in [cols[i*n] for i in range(1,n)] else '') for c in cols) )
    if r in [cols[i*n] for i in range(1,n)]:
      print( line )

def assign(values, s, d):
  """This will remove all values in each square s but leave only d and propagate any impact which this might have on the peers of the square.
  This will return the updated values, however if a contradiction is detected, this will return False"""
  values[s].remove(d)
  other_values = values[s]
  if all(eliminate(values, s, other_d) for other_d in other_values):
    return values
  else:
    print( "assign returning False" )
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
    print( "eliminate returning False" )
    return False # This is a contradiction as we just removed the last value
  elif len(values[s]) == 1:
    remaining_d = values[s]
    if not all(eliminate(values, peer_s, remaining_d) for peer_s in peers[s]):
      print( "eliminate returning False" )
      return False
  # Case 2) of propagation
  for u in units[s]:
    places = [s for s in u if d in values[s]]
    if len(places) == 0:
      print( "eliminate returning False" )
      return False # This is a contradiction as there is no available place for this value in its units
    elif len(places) == 1:
      # Digit d only has one available place in its units, we will assign it there
      if not assign(values, places[0], d):
        print( "eliminate returning False" )
        return False
  return values

print( digits )
print( rows )
print( squares )
print( squares[0] )
print( units[squares[0]] )
print( set(sum(units[squares[0]], []))-set([squares[0]]) )

grid1 = '..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..'
display(parse_grid(grid1))
