"""Terminology and Definitions:
size n - Dimensions for the Sudoku, typically n=3 but can be resized 
Square - Individual block occupied by each value 
Unit - a collection of n^2 squares either in the same box, column or row as a particular Square, that are filled with permutations of values 0 to 2^n - 1  
Peer -  The squares belonging to the same unit as the Square, there are 2*(n^2 -1) + 2^(n-1) peers for each Square
"""

import string

n = int(input('Enter the desired size n: '))

def cross(A, B):
  # Returning the Cross Product of elements in A and of elements in B as a list
  return [a+b for a in A for b in B]

values = [ str(i) for i in range(n**2) ]
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

print( values )
print( rows )
print( squares )
print( squares[0] )
print( units[squares[0]] )
print( set(sum(units[squares[0]], []))-set([squares[0]]) )
