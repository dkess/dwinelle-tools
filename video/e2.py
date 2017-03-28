#!/usr/bin/env python3

from collections import Counter, defaultdict
from itertools import chain
import pickle
from typing import Dict, FrozenSet, List, NamedTuple, Set, Tuple
from sys import argv

from sympy.matrices import GramSchmidt, Matrix, zeros

import utils

Edge = Tuple[int, int]

def edge(a: int, b: int) -> Edge:
    if a > b:
        return (b, a)
    else:
        return (a, b)

class GraphPoint:
    x: Counter = Counter()
    y: Counter = Counter()
    
    def update(self, d: utils.Direction, e: Edge):
        e = edge(*e)
        if d == utils.Direction.forward:
            self.y[e] += 1
        elif d == utils.Direction.right:
            self.x[e] += 1
        elif d == utils.Direction.backward:
            self.y[e] -= 1
        elif d == utils.Direction.left:
            self.x[e] -= 1

    def copy(self) -> 'GraphPoint':
        r = GraphPoint()
        r.x = Counter(self.x)
        r.y = Counter(self.y)
        return r

graph = utils.get_graph().branches

positions = defaultdict(list)
positions[0] = [GraphPoint()]

loose_ends = {(None, 0)}

while loose_ends:
    prev, v = loose_ends.pop()

    for d, n in graph[v].items():
        if n != prev:
            current_pos = positions[v][0].copy()
            current_pos.update(d, (n, v))
            positions[n].append(current_pos)
            try:
                loose_ends.remove((n, v))
            except KeyError:
                loose_ends.add((v, n))

for en in utils.load_equal_nodes():
    v = en[0]
    for n in en[1:]:
        positions[v].extend(positions.pop(n))

def set_to_counter(pos, neg):
    r = Counter()
    for x in pos:
        r[x] = 1
    for x in neg:
        r[x] = -1
    return r

def present_edges(c):
    return (k for k, v in c.items() if v)

rows: List[Counter] = [set_to_counter(*x) for x in utils.load_equal_edges()]
tracked_edges: Set[Edge] = set(chain.from_iterable(present_edges(r) for r in rows))

for p in positions.values():
    if len(p) > 1:
        for entry in p[1:]:
            cx = Counter(p[0].x)
            cy = Counter(p[0].y)
            cx.subtract(entry.x)
            cy.subtract(entry.y)

            tracked_edges.update(present_edges(cx), present_edges(cy))

            # make sure there aren't any rows that are just zeroes
            if any(cx.values()):
                rows.append(cx)
            if any(cy.values()):
                rows.append(cy)

# give each edge a unique id (for indexing into the matrix)
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

if __name__ == '__main__':
    subspace = GramSchmidt(the_matrix.nullspace(), True)

    # Do an orthogonal projection of measured onto the subspace
    measured = Matrix(measured)
    projected_vector = sum((w.dot(measured) * w for w in subspace),
                           zeros(len(tracked_edges), 1))

    for n, length in enumerate(projected_vector):
        edge_lengths[tracked_edges[n]] = float(length.evalf())

    pickle.dump(edge_lengths, open(argv[1], 'wb'))
