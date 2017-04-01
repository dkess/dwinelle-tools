#!/usr/bin/env python3

# This file is part of dwinelle-tools.

# dwinelle-tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# dwinelle-tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with dwinelle-tools.  If not, see <http://www.gnu.org/licenses/>.

from collections import Counter, defaultdict
import pickle
from typing import Dict, FrozenSet, List, NamedTuple, Set, Tuple
from sys import argv

from sympy.matrices import GramSchmidt, Matrix, zeros

import utils

Edge = Tuple[int, int]

def flip(a: Edge) -> Edge:
    return (a[1], a[0])

edge_lengths = utils.load_edge_lengths()
edge_direction: Dict[Edge, Tuple[Edge, int]] = {}
# maps an ordered edge to the start/end points of the elevation
edge_stairpoints: Dict[Edge, Tuple[float, float]] = {}

er = utils.get_edgerooms()
roomsets = {k: {r[1] for r in v} for k, v in er.items()}
for e, rooms in roomsets.items():
    if 'u' in rooms and 'd' in rooms:
        print('Anomoly: u and d:', e)

    if 'u' in rooms and 'd' not in roomsets.get(flip(e), []):
        print(e)
    if 'd' in rooms and 'u' not in roomsets.get(flip(e), []):
        print(e)

    direction = None
    if 'u' in rooms:
        direction = 1
    elif 'd' in rooms:
        direction = -1
    else:
        continue
    
    if len(rooms) == 1:
        astart = 0
        bstart = 0
    else:
        astart = next(r[0] for r in er[e] if r[1] in 'ud')
        bstart = next(r[0] for r in er[flip(e)] if r[1] in 'ud')

    a, b = e
    if a < b:
        edge_stairpoints[e] = (astart, 1 - bstart)
    else:
        edge_stairpoints[(b, a)] = (bstart, 1 - astart)
        start, end = 1 - astart, bstart

graph = utils.get_graph().branches

loose_ends = {(0, v): k for k, v in graph[0].items()}

positions = defaultdict(list)
positions[0] = [Counter()]

loose_ends = {(None, 0)}

while loose_ends:
    prev, v = loose_ends.pop()

    for d, n in graph[v].items():
        if n != prev:
            current_pos = Counter(positions[v][0])
            e = utils.edge(v, n)
            if e in edge_stairpoints:
                magnitude = 1 if v < n else -1
                if 'd' in roomsets.get(e, []) or 'u' in roomsets.get(flip(e), []):
                    magnitude = -magnitude
                
                current_pos[e] += magnitude
            positions[n].append(current_pos)
            try:
                loose_ends.remove((n, v))
            except KeyError:
                loose_ends.add((v, n))

for eh in utils.load_equal_heights():
    v = eh[0]
    for n in eh[1:]:
        positions[v].extend(positions.pop(n))

rows: List[Counter] = []
tracked_edges: Set[Edge] = set()

for p in positions.values():
    for entry in p[1:]:
        c = Counter(p[0])
        c.subtract(entry)

        tracked_edges.update(k for k, v in c.items() if v)

        if any(c.values()):
            rows.append(c)

tracked_edges = list(tracked_edges)
edge_id = {e: n for n, e in enumerate(tracked_edges)}

def matrix_item(row, col):
    return rows[row][tracked_edges[col]]

the_matrix = Matrix(len(rows), len(tracked_edges), matrix_item)

# some convenience API functions
def get_rows(with_edge=None):
    if with_edge:
        return [r for r in rows if with_edge in r[0] or with_edge in r[1]]
    return rows

height_override = utils.load_height_override()

edge_heights = {}
measured = [None] * len(tracked_edges)
for e, (start, end) in edge_stairpoints.items():
    try:
        length = height_override.get(e, edge_lengths[e])
        measured[edge_id[e]] = length * (end - start)
    except KeyError:
        w = end - start
        if 'd' in roomsets[e] or 'u' in roomsets.get(flip(e), []):
            start, end = end, start
        edge_heights[e] = (start, end, edge_lengths[e] * w)

if None in measured:
    print('something went wrong!')

if __name__ == '__main__':
    subspace = GramSchmidt(the_matrix.nullspace(), True)

    # Do an orthogonal projection of measured onto the subspace
    measured = Matrix(measured)
    projected_vector = sum((w.dot(measured) * w for w in subspace),
                           zeros(len(tracked_edges), 1))

    for n, length in enumerate(projected_vector):
        start, end = edge_stairpoints[tracked_edges[n]]
        # flip start and end so tht we always start at the bottom of the stairs
        e = tracked_edges[n]
        if 'd' in roomsets[e] or 'u' in roomsets.get(flip(e), []):
            start, end = end, start
        edge_heights[tracked_edges[n]] = (start, end, float(length.evalf()))

    pickle.dump(edge_heights, open(argv[1], 'wb'))
