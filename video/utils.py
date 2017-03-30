from collections import defaultdict, deque, namedtuple
from enum import IntEnum
from itertools import chain
import json
from os import environ, path
from pickle import load
import re

PATH = environ.get('NODESPATH', '')

class Direction(IntEnum):
    forward = 0
    right = 1
    backward = 2
    left = 3

    def opposite(self):
        return self + Direction.backward

    def __add__(self, other: 'Direction') -> 'Direction':
        return Direction((self.value + other.value) % 4)

    def __sub__(self, other: 'Direction') -> 'Direction':
        return Direction((self.value - other.value) % 4)

    def letter(self):
        return DIRECTIONS[self.value]

def edge(a: int, b: int):
    if a < b:
        return a, b
    else:
        return b, a

def millis_to_timecode(m):
    m, millis = divmod(m, 1000)
    m, seconds = divmod(m, 60)
    hours, minutes = divmod(m, 60)
    return '{:02}:{:02}:{:02},{:03}'.format(hours, minutes, seconds, millis)

def get_doubles(it, end=None):
    '''
    Turns an iterator a b c d e... into (a, b) (b, c) (c, d) (d, e) ...
    
    If `end` is given, end with (e, end)
    '''
    it = iter(it)
    try:
        last = next(it)
        while True:
            e = next(it)
            yield (last, e)
            last = e
    except StopIteration:
        if end != None:
            yield (last, end)

LogEntry = namedtuple('LogEntry', ['id', 'startnode', 'endnode', 'starttime', 'endtime'])
Graph = namedtuple('Graph', ['branches', 'edgedata'])
GraphEdge=namedtuple('GraphEdge', ['length', 'rooms'])

def get_offset(clipid):
    return load_timefile()[clipid][0]

def get_length(clipid):
    return load_timefile()[clipid][1]

def get_logentries():
    '''
    Returns an iterator through all the LogEntries. Times are unix timestamps.
    '''
    log = load_nodes()['log']
    return (LogEntry(id=n,
                     startnode=start['node'],
                     endnode=end['node'],
                     starttime=start['time_enter'],
                     endtime=start['time_exit'])
            for n, (start, end) in enumerate(get_doubles(log)))

def get_active_times(clipid=None):
    '''
    Iterate through the LogEntries in which new nodes were discovered.  If
    clipid is None, return all LogEntries, where starttime and endtime are Unix
    millisecond timestamps.  If clipid is given, only return LogEntries that
    occurred during the given clip, and starttime and endtime will be Unix will
    be milliseconds since the start of the clip.
    '''

    offset = 0
    length = float('inf')
    if clipid:
        offset = get_offset(clipid)
        length = get_length(clipid)

    log = load_nodes()['log']
    traveled = set()
    for logentry in get_logentries():
        edge = (logentry.startnode, logentry.endnode)
        if edge not in traveled:
            traveled.add(edge)
            starttime = logentry.starttime - offset
            endtime = logentry.endtime - offset
            if starttime < 0:
                continue
            if endtime > length:
                continue
            yield logentry._replace(starttime=starttime, endtime=endtime)
    
class IntervalDict:
    '''
    A dictionary where keys are represented by intervals, and any number in
    that interval can be used to access a key.
    '''

    def __init__(self, intervals):
        '''
        Initialize with the intervals already chosen.  `intervals` should be
        a list of ((start, end), default) tuples.
        '''
        self.intervals = list(sorted(intervals))

    def get(self, number):
        '''Gets an entry, or return None if the entry does not exist.'''
        # Do a binary search of the interval tree
        bmin = 0
        bmax = len(self.intervals) - 1
        while True:
            if bmax < bmin:
                return None
            index = (bmax + bmin) // 2
            on = self.intervals[index]
            if number < on[0][0]:
                bmax = index - 1
            elif number >= on[0][1]:
                bmin = index + 1
            else:
                return on[1]

    def values(self):
        '''Return an iterator over the dict's values, sorted by key.'''
        return (v for k, v in self.intervals)

def get_walking_times(clipid):
    '''
    Just like the output from get_active_times, but start_time and end_time
    are shortened to only include times when the camera-holder is walking.
    '''
    active_times = get_active_times(clipid)
    intervals = [((i.starttime, i.endtime), i._asdict()) for i in active_times]
    int_dict = IntervalDict(intervals)

    for l in open(path.join(PATH, 'walk{}.txt'.format(clipid))):
        p, n = l.strip().split()

        # convert to milliseconds
        n = float(n) * 1000

        item = int_dict.get(n)
        if item == None:
            continue

        if p == 'y':
            item['starttime'] = int(n)
        elif p == 'i':
            item['endtime'] = int(n)
        else:
            print('bad input')

    return (LogEntry(**i) for i in int_dict.values())

def get_logentry_at_time(*args):
    '''
    If one argument is provided, get the LogEntry corresponding to the given
    unix time (in milliseconds).  If two arguments are provided, get the 
    LogEntry at clipid (first argument) and time in that clip in milliseconds
    (second argument).
    '''

    if len(args) == 1:
        unixtime = args[0]
    else:
        unixtime = timestamp_from_video(*args)

    for logentry in get_logentries():
        if logentry.starttime <= unixtime < logentry.endtime:
            return logentry

def get_entries_with_edge(*args):
    '''
    Iterate through a list of log entries in which the given path was taken.

    If one argument is given, choose the edge associated with the LogEntry of
    the given id (or the given LogEntry).  If two arguments are given, choose
    the edge whose starting node has id of the first argument and ending node
    has id of the second argument.

    `starttime` and `endtime` in the returned LogEntries will be a
    (clipid, millis) tuple where clipid is the clip in which the log entry took
    place in, and millis is the time during that video when that log entry
    happened.
    '''

    log = load_nodes()['log']

    if len(args) == 1:
        if type(args[0]) == LogEntry:
            startnode = args[0].startnode
            endnode = args[0].endnode
        else:
            entry = log[args[0]]
            startnode = log[args[0]]['node']
            endnode = log[args[0]+1]['node']
    else:
        startnode, endnode = args

    return (logentry._replace(starttime=time_in_video(logentry.starttime),
                              endtime=time_in_video(logentry.endtime))
            for logentry in get_logentries()
            if logentry.startnode == startnode and logentry.endnode == endnode)

def time_in_video(timestamp):
    '''
    Takes a unix timestamp in millis and returns a (clipid, seconds) couple
    where seconds is the time of that timestamp in the given clipid.
    '''
    timefile = load_timefile()
    clipid = timestamps_tree.get(timestamp)
    return (clipid, (timestamp - get_offset(clipid)) / 1000)

def timestamp_from_video(clipid, millis):
    '''
    Inverse of time_in_video.  Returns the unix timestamp in millis of a point
    in time of a clip.
    '''
    return get_offset(clipid) + millis

def get_graph(rotate_dir=Direction.forward):
    j = load_nodes()
    
    neighbors = [{Direction[k] + rotate_dir: v for k, v in node['branches'].items()} for node in j['nodes']]
    
    # only contains keys (a,b) where a < b
    edgedata = defaultdict(lambda: {'rooms': [], 'distance': 0})
    tree = IntervalDict(((e.starttime, e.endtime),
                         (e.startnode, e.endnode))
                        for e in get_logentries())

    for clipid, rooms in load_roomsfiles().items():
        for ts, name in rooms:
            unixts = timestamp_from_video(clipid, ts)
            startnode, endnode = tree.get(unixts)
            if startnode < endnode:
                k = (startnode, endnode)
            else:
                k = (endnode, startnode)

            edgedata[k]['rooms'].append(name)

        for e in get_walking_times(clipid):
            if e.startnode < e.endnode:
                k = (e.startnode, e.endnode)
            else:
                k = (e.endnode, e.startnode)

            edgedata[k]['distance'] += (e.endtime - e.starttime) / 2

    return Graph(branches=neighbors, edgedata=edgedata)

def get_edgerooms():
    edgerooms = defaultdict(list)
    tree = IntervalDict(((e.starttime, e.endtime), e)
                        for e in get_logentries())

    for clipid, rooms in load_roomsfiles().items():
        for ts, name in rooms:
            unixts = timestamp_from_video(clipid, ts)
            entry = tree.get(unixts)
            e = (entry.startnode, entry.endnode)
            normalized_time = ((unixts - entry.starttime)
                               / (entry.endtime - entry.starttime))
            edgerooms[e].append((normalized_time, name, clipid, ts))

    return edgerooms

def get_node_coords(rotate_dir=Direction.forward):
    g = get_graph().branches
    node_lengths = load_edge_lengths()
    edge_heights = load_edge_heights()

    hflip = False
    hflip = -1 if hflip else 1

    node_coords = {}
    def dfs(v, x, y, z):
        node_coords[v] = (x, y, z)
        for d, n in g[v].items():
            if n not in node_coords:
                length = float(node_lengths[edge(v, n)])
                if edge(v, n) in edge_heights:
                    if v < n:
                        s, e, h = edge_heights[(v, n)]
                    else:
                        s, e, h = edge_heights[(n, v)]
                        h = -h
                    if s > e:
                        h = -h
                else:
                    h = 0
                d = d + rotate_dir
                if d == Direction.forward:
                    dfs(n, x, y + length, z + h)
                elif d == Direction.right:
                    dfs(n, x + hflip * length, y, z + h)
                elif d == Direction.backward:
                    dfs(n, x, y - length, z + h)
                elif d == Direction.left:
                    dfs(n, x - hflip * length, y, z + h)
    
    dfs(0, 0, 0, 0)
    
    return node_coords

def get_floors():
    g = get_graph()

    unexplored = set(range(len(g.branches)))
    floors = []

    while unexplored:
        rooms = []
        edges = set()

        start = unexplored.pop()
        unexplored.add(start)

        frontier = [(-1, start)]
        while frontier:
            prev, v = frontier.pop()

            if v in unexplored:
                unexplored.remove(v)
                if prev >= 0:
                    if prev < v:
                        k = (prev, v)
                    else:
                        k = (v, prev)
                    
                    edges.add(k)
                    r = g.edgedata[k]['rooms']
                    rooms.extend(r for r in r if r != 'u' and r != 'd')
                    if 'u' in r or 'd' in r:
                        continue

                for n in g.branches[v].values():
                    frontier.append((v, n))
        floors.append((rooms, edges))

    return floors

def edge_length_accuracy():
    ed = get_graph().edgedata
    el = load_edge_lengths()

    return sorted((abs(v - ed[k]['distance'])/ed[k]['distance'], k, v, ed[k]['distance']) for k, v in el.items())

times = None
timestamps_tree = None
def load_timefile():
    global times
    global timestamps_tree

    if times:
        return times

    times = {}
    for l in open(path.join(PATH, 'times')):
        clipid, offset, length = l.strip().split()
        offset = int(offset)
        length = int(length)

        times[clipid] = (offset, length)
    
    timestamps_tree = IntervalDict(((starttime, endtime), clipid)
                                   for (starttime, clipid), (endtime, _)
                                   in get_doubles(sorted((offset, clipid)
                                                         for clipid, (offset, _)
                                                         in times.items()),
                                                  end=(float('inf'), None)))

    return times

def load_roomsfiles():
    times = load_timefile()
    rooms = {}

    for clipid in times.keys():
        entries = []

        for l in open(path.join(PATH, 'rooms{}.txt'.format(clipid))):
            ts, name = l.strip().split(' ', 1)
            ts = float(ts) * 1000
            entries.append((ts, name))

        rooms[clipid] = entries

    return rooms

nodes = None
def load_nodes():
    global nodes

    if nodes:
        return nodes

    nodes = json.load(open(path.join(PATH, 'nodes.json')))
    return nodes

edge_lengths = None
def load_edge_lengths():
    global edge_lengths

    if edge_lengths:
        return edge_lengths

    edge_lengths = load(open(path.join(PATH, 'edge_lengths'), 'rb'))
    return edge_lengths

edge_heights = None
def load_edge_heights():
    global edge_heights

    if edge_heights:
        return edge_heights

    try:
        edge_heights = load(open(path.join(PATH, 'edge_heights'), 'rb'))
    except FileNotFoundError:
        edge_heights = {}
    return edge_heights

equal_edges = None
def load_equal_edges():
    global equal_edges

    if equal_edges:
        return equal_edges

    equal_edges = []
    edge_re = re.compile(r'(\-?)\(([0-9]+)[^0-9\)]+([0-9]+)\)')
    for l in open(path.join(PATH, 'equal_edges')):
        # strip comments
        l = l.strip().split('#', 1)[0]

        pos = []
        neg = []
        for m in edge_re.finditer(l):
            sign, a, b = m.groups()
            e = edge(int(a), int(b))
            if sign == '-':
                neg.append(e)
            else:
                pos.append(e)

        if pos or neg:
            equal_edges.append((frozenset(pos), frozenset(neg)))

    return equal_edges

equal_nodes = None
def load_equal_nodes():
    global equal_nodes

    if equal_nodes:
        return equal_nodes

    equal_nodes = []
    node_re = re.compile(r'[0-9]+')
    equal_nodes = (
        [int(s) for s in node_re.findall(l.strip().split('#', 1)[0])]
        for l in open(path.join(PATH, 'equal_nodes')))
    
    equal_nodes = [e for e in equal_nodes if e]

    return equal_nodes

equal_heights = None
def load_equal_heights():
    global equal_heights

    if equal_heights:
        return equal_heights

    equal_heights = []
    node_re = re.compile(r'[0-9]+')
    equal_heights = (
        [int(s) for s in node_re.findall(l.strip().split('#', 1)[0])]
        for l in open(path.join(PATH, 'equal_heights')))
    
    equal_heights = [e for e in equal_heights if e]

    return equal_heights

height_override = None
def load_height_override():
    global height_override

    if height_override:
        return height_override

    height_override = {}
    line_re = re.compile(r'\(([0-9]+)[^0-9\)]+([0-9]+)\)\s*([+-]?(?:[0-9]*[.])?[0-9]+)')
    for l in open(path.join(PATH, 'height_override')):
        # strip comments
        l = l.strip().split('#', 1)[0]

        m = line_re.match(l)
        if m:
            a, b, length = m.groups()
            e = edge(int(a), int(b))

            height_override[e] = float(length)

    return height_override

groups = None
def load_groups():
    global groups

    if groups:
        return groups

    groups = []

    state = 0;
    for l in chain(open(path.join(PATH, 'groups')), ['']):
        l = l.strip()
        if not l:
            state = 0
            if current_group:
                groups.append(current_group)
        elif state == 0:
            current_group = {}
            current_group['nodes'] = [int(x) for x in l.split()]
            state += 1
        elif state == 1:
            current_group['name'] = l
            state += 1
            current_group['exits'] = {}
        else:
            n, name = l.split(' ', 1)
            current_group['exits'][int(n)] = name

    return groups
