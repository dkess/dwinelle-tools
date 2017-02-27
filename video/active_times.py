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
