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

from sys import exit, argv

import utils

if len(argv) != 3 or argv[2] not in {'active', 'walking'}:
    print('Usage: {} clipid [active|walking]')

clipid = argv[1]

length = utils.get_length(clipid)

if argv[2] == 'active':
    intervals = utils.get_active_times(clipid=clipid)
else:
    intervals = utils.get_walking_times(clipid)
#intervals = [(i.starttime, i.endtime) for i in intervals]
intervals = list(intervals)

counter = 0
def insert_subtitle(start, duration, txt, color):
    if duration <= 0:
        return

    global counter
    counter += 1
    print(counter)
    print('{} --> {}'.format(utils.millis_to_timecode(start),
                             utils.millis_to_timecode(start + duration)))
    print('<font color="{}">{}</font>'.format(color, txt))
    print()

def insert_countdown(start, edge, duration, color):
    seconds, offset = divmod(duration, 1000)
    insert_subtitle(start, offset, '{} {}'.format(edge, seconds + 1), color)
    for n in range(seconds, 0, -1):
        insert_subtitle(start + duration - n * 1000,
                        1000,
                        '{} {}'.format(edge, n),
                        color)

for i in range(len(intervals)):
    s = intervals[i].starttime
    e = intervals[i].endtime
    if s > 0 and e < length:
        edge = (intervals[i].startnode, intervals[i].endnode)
        insert_countdown(s, edge, e - s, 'green')
        
        if i + 1 < len(intervals):
            insert_countdown(e, edge, intervals[i+1].starttime - e, 'red')
