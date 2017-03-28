#!/usr/bin/env python3

from os import path
from sys import argv

# wrote this script in python because lua is terrible to work with
filedir, name = path.split(argv[1])
clipid, ext = path.splitext(name)
entry = argv[2]

x = argv[2].strip().split()
if len(x) == 1:
    print('seek {} absolute'.format(x[0]))
else:
    import utils
    if x[0] == 'l':
        cid, seconds = utils.time_in_video(utils.load_nodes()['log'][int(x[1])]['time_enter'])
    else:
        a = int(x[0])
        b = int(x[1])

        cid, seconds = next(utils.get_entries_with_edge(a, b)).starttime

    if cid != clipid:
        print('loadfile {}{} replace start={}'.format(path.join(filedir, cid), ext, seconds))
    else:
        print('seek {} absolute'.format(seconds))
