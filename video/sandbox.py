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

from itertools import chain

import utils
el = utils.load_edge_lengths()
g = utils.get_graph(utils.Direction.left).branches
ed = utils.get_graph().edgedata

if __name__ == '__main__':
    while True:
        s = input('-> ')
        try:
            try:
                n = int(s.strip())
                print(g[n])
            except ValueError:
                a, b = map(int, s.strip().split())
                e = utils.edge(a, b)
                print(el[e])
                '''
                for le in chain(utils.get_entries_with_edge(a, b),
                                utils.get_entries_with_edge(b, a)):
                    print(le)
                '''
                print(ed[e])
                print(next(k for k, v in g[a].items() if v == b))
        except (IndexError, KeyError) as e:
            print('err')

