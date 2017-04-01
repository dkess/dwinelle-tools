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

# This can be used to generate data3d.js for the web frontend.

import utils

edge_lengths = utils.load_edge_lengths()
print('var el = {{{}}};'.format(','.join('"{} {}":{}'.format(k[0], k[1], v) for k, v in edge_lengths.items())))
print('var coords = {{{}}};'.format(','.join('{}:{{x:{},y:{},z:{}}}'.format(k, v[0], v[1], v[2]) for k, v in utils.get_node_coords().items())))
print('var eh = {{{}}};'.format(','.join('"{} {}":{{bot:{},top:{},l:{}}}'.format(k[0], k[1], v[0], v[1], v[2]) for k, v in utils.load_edge_heights().items())))
