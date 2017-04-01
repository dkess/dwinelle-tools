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

# NOTE: this code is broken.  You should use e2.py instead.

from collections import defaultdict
from itertools import chain
import pickle
from typing import Dict, FrozenSet, List, NamedTuple, Set, Tuple
from sys import argv

from sympy.matrices import GramSchmidt, Matrix, zeros

import utils

graph = utils.get_graph().branches

Edge = Tuple[int, int]

class FrozenGraphPoint(NamedTuple):
    y_pos: FrozenSet[Edge]
    x_pos: FrozenSet[Edge]
    y_neg: FrozenSet[Edge]
    x_neg: FrozenSet[Edge]
    
class GraphPoint:
    y_pos: Set[Edge] = set()
    x_pos: Set[Edge] = set()
    y_neg: Set[Edge] = set()
    x_neg: Set[Edge] = set()

    def update(self, d: utils.Direction, e: Edge):
        if d == utils.Direction.forward:
            try:
                self.y_neg.remove(e)
            except KeyError:
                self.y_pos.add(e)
        elif d == utils.Direction.right:
            try:
                self.x_neg.remove(e)
            except KeyError:
                self.x_pos.add(e)
        elif d == utils.Direction.backward:
            try:
                self.y_pos.remove(e)
            except KeyError:
                self.y_neg.add(e)
        elif d == utils.Direction.left:
            try:
                self.x_pos.remove(e)
            except KeyError:
                self.x_neg.add(e)

    def freeze(self):
        return FrozenGraphPoint(
            y_pos=frozenset(self.y_pos),
            x_pos=frozenset(self.x_pos),
            y_neg=frozenset(self.y_neg),
            x_neg=frozenset(self.x_neg))
            

cur_y_pos = set() # forward
cur_x_pos = set() # right
cur_y_neg = set() # backward
cur_x_neg = set() # left

def edge(a: int, b: int) -> Edge:
    if a > b:
        return (b, a)
    else:
        return (a, b)

def update_pos(d, e):
    if d == utils.Direction.forward:
        try:
            cur_y_neg.remove(e)
        except KeyError:
            cur_y_pos.add(e)
    elif d == utils.Direction.right:
        try:
            cur_x_neg.remove(e)
        except KeyError:
            cur_x_pos.add(e)
    elif d == utils.Direction.backward:
        try:
            cur_y_pos.remove(e)
        except KeyError:
            cur_y_neg.add(e)
    elif d == utils.Direction.left:
        try:
            cur_x_pos.remove(e)
        except KeyError:
            cur_x_neg.add(e)

positions: Dict[Edge, FrozenGraphPoint] = {}
current_position = GraphPoint()
def dfs(before: int, v: int):
    frozen = current_position.freeze()
    for n in graph[v].values():
        if n != before:
            if (n, v) in positions:
                positions[(n, v)] = frozen
            else:
                positions[(v, n)] = None
        elif len(graph[v]) > 2:
            positions[(v, n)] = frozen

    for d, n in graph[v].items():
        if n != before and (v, n) in positions and positions[(v, n)] == None:
            del positions[(v, n)]

            # cross this edge
            e = edge(v, n)
            current_position.update(d, e)
            dfs(v, n)
            current_position.update(d.opposite(), e)

dfs(None, 0)

equal_pos = defaultdict(list)
for (n, _), p in positions.items():
    equal_pos[n].append(p)

#equal_pos = [v for v in equal_pos.values() if len(v) > 1]
rows: List[Tuple[FrozenSet[Edge], FrozenSet[Edge]]] = utils.load_equal_edges()[:]

tracked_edges: Set[Edge] = set(chain.from_iterable(chain(pos, neg) for pos, neg in rows))

rowdata = []
for v in equal_pos.values():
    if len(v) > 1:
        start = v[0]
        for entry in v[1:]:
            # start - entry
            y_pos = (start.y_pos - entry.y_pos) | (entry.y_neg - start.y_neg)
            y_neg = (start.y_neg - entry.y_neg) | (entry.y_pos - start.y_pos)

            x_pos = (start.x_pos - entry.x_pos) | (entry.x_neg - start.x_neg)
            x_neg = (start.x_neg - entry.x_neg) | (entry.x_pos - start.x_pos)

            if y_pos & y_neg or x_pos & x_neg:
                print('something is wrong!!!')

            tracked_edges.update(y_pos, y_neg, x_pos, x_neg)

            rowdata.append(((x_pos, x_neg), (y_pos, y_neg), (start, entry)))

            rows.append((y_pos, y_neg))
            rows.append((x_pos, x_neg))

# give each edge a unique id (for indexing into the matrix)
tracked_edges = list(tracked_edges)
edge_id = {e: n for n, e in enumerate(tracked_edges)}

def matrix_item(row, col):
    if tracked_edges[col] in rows[row][0]:
        return 1
    elif tracked_edges[col] in rows[row][1]:
        return -1
    else:
        return 0

the_matrix = Matrix(len(rows), len(tracked_edges), matrix_item)

# some convenience API functions
def get_rows(with_edge=None):
    if with_edge:
        return [r for r in rows if with_edge in r[0] or with_edge in r[1]]
    return rows

if __name__ == '__main__':
    subspace = GramSchmidt(the_matrix.nullspace(), True)

    # Get the measured edge lengths
    edge_lengths = {}
    measured = [None] * len(tracked_edges)
    for e, data in utils.get_graph().edgedata.items():
        try:
            if measured[edge_id[e]] == None:
                measured[edge_id[e]] = data['distance']
        except KeyError:
            if e not in edge_lengths:
                edge_lengths[e] = data['distance']

    if None in measured:
        print('something went wrong!')

    # Do an orthogonal projection of measured onto the subspace
    measured = Matrix(measured)
    projected_vector = sum((w.dot(measured) * w for w in subspace),
                           #zeros(len(tracked_edges), 1)).evalf()
                           zeros(len(tracked_edges), 1))

    for n, length in enumerate(projected_vector):
        edge_lengths[tracked_edges[n]] = float(length.evalf())

    pickle.dump(edge_lengths, open(argv[1], 'wb'))
