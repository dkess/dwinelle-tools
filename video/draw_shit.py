from itertools import chain
import turtle

import utils

def edge(a: int, b: int):
    if a > b:
        return (b, a)
    else:
        return (a, b)

SHRINK = 70
X_OFFSET = 800
Y_OFFSET = 0

graph = utils.get_graph().branches
full_floors = [(r, e) for r, e in utils.get_floors() if len(r) > 0]
edge_lengths = utils.load_edge_lengths()

empty_edges = set(chain.from_iterable(e for r, e in utils.get_floors() if len(e) == 0))

directions = {utils.Direction.forward: 90,
              utils.Direction.right: 0,
              utils.Direction.backward: 270,
              utils.Direction.left: 180}

current_floor = None
def draw_floor(floornum):
    global current_floor
    current_floor = floornum

    node_coords = utils.get_node_coords(utils.Direction.left) 

    if floornum == len(full_floors):
        rooms = []
        # All edges with rooms
        edges = chain.from_iterable(edges for _, edges in full_floors)
        # Edges with elevation changes
        #edges = set(chain.from_iterable((edge(v, n) for n in b.values() if set(['u', 'd']) & set(utils.get_graph().edgedata[edge(v, n)]['rooms'])) for v, b in enumerate(utils.get_graph().branches)))
        # All edges
        #...
    elif floornum >= 0 and floornum < len(full_floors):
        rooms, edges = full_floors[floornum]
        print(rooms)
    else:
        return

    turtle.showturtle()
    turtle.speed(0)
    turtle.clear()

    written_nodes = set()

    for a, b in edges:
        turtle.penup()
        x, y = node_coords[a]
        turtle.goto(x / SHRINK + X_OFFSET, y / SHRINK + Y_OFFSET)
        if a not in written_nodes:
            turtle.write(a)
            written_nodes.add(a)

        turtle.pendown()

        if edge_lengths[edge(a, b)] <= 0:
            turtle.pencolor('red')
        else:
            turtle.pencolor('black')

        x, y = node_coords[b]
        turtle.goto(x / SHRINK + X_OFFSET, y / SHRINK + Y_OFFSET)
        turtle.pencolor('black')
        if b not in written_nodes:
            turtle.write(b)
            written_nodes.add(b)

    turtle.hideturtle()
    turtle.done()

def next_floor(x, y):
    print('got click event')
    draw_floor((current_floor + 1) % (len(full_floors) + 1))

def prev_floor(x, y):
    print('right click')
    draw_floor((current_floor - 1) % (len(full_floors) + 1))

turtle.Screen().onclick(next_floor, 1)
turtle.Screen().onclick(prev_floor, 3)

draw_floor(0)
