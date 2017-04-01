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

# This script can be used to generate data.js for the web frontend.

import json

import utils

print('var EDGEROOMS = {{{}}};'.format(','.join(
    '"{} {}":[{}]'.format(k[0], k[1], ','.join(
        '{{t:{:.4f},n:{}}}'.format(r[0], json.dumps(r[1])) for r in v))
    for k, v in utils.get_edgerooms().items())))

print ('var GRAPH = [{}];'.format(','.join('[{}]'.format(','.join(str(n) for n in branches.values())) for branches in utils.get_graph().branches)))
print('var DIRECTIONS = {{{}}};'.format(','.join('"{} {}":{}'.format(v, n, d) for v, g in enumerate(utils.get_graph().branches) for d, n in g.items() if v < n)));
print('var GROUPS = {};'.format(json.dumps(utils.load_groups())))
