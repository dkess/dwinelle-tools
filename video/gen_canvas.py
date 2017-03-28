#!/usr/bin/env python3

import utils

SHRINK = 85
X_OFFSET = 1500
Y_OFFSET = 300

edge_lengths = utils.load_edge_lengths()
print('var el = {{{}}};'.format(','.join('"{} {}":{}'.format(k[0], k[1], v) for k, v in edge_lengths.items())))
print('var coords = {{{}}};'.format(','.join('{}:{{x:{},y:{}}}'.format(k, v[0] / SHRINK + X_OFFSET, -v[1] / SHRINK + Y_OFFSET) for k, v in utils.get_node_coords(utils.Direction.left).items())))
