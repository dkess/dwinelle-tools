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

from enum import Enum
from itertools import chain
from sys import argv
import turtle

import utils

def edge(a: int, b: int):
    if a > b:
        return (b, a)
    else:
        return (a, b)

SHRINK = 85
X_OFFSET = 800
Y_OFFSET = 100

graph = utils.get_graph().branches

class Mode(Enum):
    floors = 0
    equals = 1

mode: Mode = Mode.floors
current_floor: int = 0
if len(argv) >= 2:
    mode = Mode[argv[1]]
    if len(argv) >= 3:
        current_floor = int(argv[2])
    
if mode == Mode.floors:
    full_floors = [(r, (e, [])) for r, e in utils.get_floors() if len(r) > 0]
elif mode == Mode.equals:
    import equations
    full_floors = list(enumerate(equations.get_rows()))

edge_lengths = utils.load_edge_lengths()

empty_edges = set(chain.from_iterable(e for r, e in utils.get_floors() if len(e) == 0))

directions = {utils.Direction.forward: 90,
              utils.Direction.right: 0,
              utils.Direction.backward: 270,
              utils.Direction.left: 180}

def draw_floor(floornum: int):
    global current_floor
    current_floor = floornum

    node_coords = utils.get_node_coords(utils.Direction.left) 

    if floornum == len(full_floors):
        rooms = []
        # All edges with rooms
        print('Showing everything')
        edges = chain.from_iterable(chain(((True, e) for e in edges[0]), ((False, e) for e in edges[1])) for _, edges in full_floors)
        # Edges with elevation changes
        #edges = set(chain.from_iterable((edge(v, n) for n in b.values() if set(['u', 'd']) & set(utils.get_graph().edgedata[edge(v, n)]['rooms'])) for v, b in enumerate(utils.get_graph().branches)))
        # All edges
        #...
    elif floornum >= 0 and floornum < len(full_floors):
        rooms, edges = full_floors[floornum]
        print(edges)
        edges = chain(((True, e) for e in edges[0]), ((False, e) for e in edges[1]))
        print(rooms)
    else:
        return

    turtle.showturtle()
    turtle.speed(0)
    turtle.clear()

    written_nodes = set()

    for edge_dir, (a, b) in edges:
        turtle.penup()
        x, y, _ = node_coords[a]
        turtle.goto(x / SHRINK + X_OFFSET, y / SHRINK + Y_OFFSET)
        if a not in written_nodes:
            turtle.write(a)
            written_nodes.add(a)

        turtle.pendown()

        if edge_dir:
            if edge_lengths[edge(a, b)] <= 0:
                turtle.pencolor('red')
            else:
                turtle.pencolor('black')
        else:
            if edge_lengths[edge(a, b)] <= 0:
                turtle.pencolor('blue')
            else:
                turtle.pencolor('green')

        x, y, _ = node_coords[b]
        turtle.goto(x / SHRINK + X_OFFSET, y / SHRINK + Y_OFFSET)
        turtle.pencolor('black')
        if b not in written_nodes:
            turtle.write(b)
            written_nodes.add(b)

    turtle.hideturtle()
    turtle.done()

def next_floor(x, y):
    draw_floor((current_floor + 1) % (len(full_floors) + 1))

def prev_floor(x, y):
    draw_floor((current_floor - 1) % (len(full_floors) + 1))

turtle.Screen().onclick(next_floor, 1)
turtle.Screen().onclick(prev_floor, 3)

draw_floor(current_floor)
