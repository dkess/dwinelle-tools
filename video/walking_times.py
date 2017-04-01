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

# Takes a walking log (outputted from the mpv walking script) a nodes file, and
# a milliseconds offset, and outputs a space-delimited CSV with the columns:
# logid starttime endtime
# for all log entries in which there was a new edge

from sys import argv, exit

if len(argv) != 5:
    print('Usage: {} intervals offset walkinglog'.format(argv[0]))
    exit(0)

offset = int(argv[2])

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
            elif number > on[0][1]:
                bmin = index + 1
            else:
                return on[1]

    def values(self):
        '''Return an iterator through the dict's values, sorted by key.'''
        return (v for k, v in self.intervals)

'''
j = json.load(open(argv[1]))
path = [l['node'] for l in j['log']]
traveled = set()
intervals = []
for i in range(len(path) - 1):
    k = (path[i], path[i+1])
    if k not in traveled:
        traveled.add(k)

        s = j['log'][i]['time_enter'] - offset
        e = j['log'][i]['time_exit'] - offset
        intervals.append(((s, e), [i, s, e]))
'''

intervals = []
for l in open(argv[1]):
    a, b = map(int, l.rstrip().split(' '))
    intervals.append(((a - offset, b - offset), [s, e]))


int_dict = IntervalDict(intervals)
discarded = 0

for l in open(argv[3]):
    p, n = l.strip().split()

    # convert to milliseconds
    n = float(n) * 1000

    item = int_dict.get(n)
    if item == None:
        discarded += 1
        continue

    if p == 'y':
        item[0] = n
    elif p == 'i':
        item[1] = n
    else:
        print('bad input')

for v in int_dict.values():
    print(*v)
