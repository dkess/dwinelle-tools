from sys import argv, exit

def millis_to_timecode(m):
    m, millis = divmod(m, 1000)
    m, seconds = divmod(m, 60)
    hours, minutes = divmod(m, 60)
    return '{:02}:{:02}:{:02},{:03}'.format(hours, minutes, seconds, millis)

if len(argv) != 4:
    print('Usage: {} intervals offset length'.format(argv[0]))
    exit(0)

time_offset = int(argv[2])
length = int(argv[3])

intervals = []
for l in open(argv[1]):
    a, b = map(int, l.rstrip().split(' '))
    intervals.append((a - time_offset, b - time_offset))

counter = 0
def insert_subtitle(start, duration, txt, color):
    if duration <= 0:
        return

    global counter
    counter += 1
    print(counter)
    print('{} --> {}'.format(millis_to_timecode(start),
                             millis_to_timecode(start + duration)))
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
