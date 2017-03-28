#!/usr/bin/env python3

import utils

edge_lengths = utils.load_edge_lengths()
print('var el = {{{}}};'.format(','.join('"{} {}":{}'.format(k[0], k[1], v) for k, v in edge_lengths.items())))
print('var coords = {{{}}};'.format(','.join('{}:{{x:{},y:{},z:{}}}'.format(k, v[0], v[1], v[2]) for k, v in utils.get_node_coords().items())))
print('var eh = {{{}}};'.format(','.join('"{} {}":{{bot:{},top:{},l:{}}}'.format(k[0], k[1], v[0], v[1], v[2]) for k, v in utils.load_edge_heights().items())))
