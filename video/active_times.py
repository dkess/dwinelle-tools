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

import json
from sys import argv, exit

if len(argv) != 2:
    print('Usage: {} nodesfile'.format(argv[0]))
    exit(0)

j = json.load(open(argv[1]))

path = [l['node'] for l in j['log']]
traveled = set()
for i in range(len(path) - 1):
    k = (path[i], path[i+1])
    if k not in traveled:
        traveled.add(k)
        print(j['log'][i]['time_enter'], j['log'][i]['time_exit'])
