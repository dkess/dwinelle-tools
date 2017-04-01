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

import utils

SHRINK = 85
X_OFFSET = 1500
Y_OFFSET = 300

edge_lengths = utils.load_edge_lengths()
print('var el = {{{}}};'.format(','.join('"{} {}":{}'.format(k[0], k[1], v) for k, v in edge_lengths.items())))
print('var coords = {{{}}};'.format(','.join('{}:{{x:{},y:{}}}'.format(k, v[0] / SHRINK + X_OFFSET, -v[1] / SHRINK + Y_OFFSET) for k, v in utils.get_node_coords(utils.Direction.left).items())))
