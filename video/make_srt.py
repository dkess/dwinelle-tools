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
intervals = [(i.starttime, i.endtime) for i in intervals]

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

def insert_countdown(start, duration, color):
    seconds, offset = divmod(duration, 1000)
    insert_subtitle(start, offset, seconds + 1, color)
    for n in range(seconds, 0, -1):
        insert_subtitle(start + duration - n * 1000, 1000, n, color)

for i in range(len(intervals)):
    s, e = intervals[i]
    if s > 0 and e < length:
        insert_countdown(s, e - s, 'green')
        
        if i + 1 < len(intervals):
            insert_countdown(e, intervals[i+1][0] - e, 'red')
