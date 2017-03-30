import json

import utils

print('var EDGEROOMS = {{{}}};'.format(','.join(
    '"{} {}":[{}]'.format(k[0], k[1], ','.join(
        '{{t:{:.4f},n:{}}}'.format(r[0], json.dumps(r[1])) for r in v))
    for k, v in utils.get_edgerooms().items())))

print ('var GRAPH = [{}];'.format(','.join('[{}]'.format(','.join(str(n) for n in branches.values())) for branches in utils.get_graph().branches)))
print('var DIRECTIONS = {{{}}};'.format(','.join('"{} {}":{}'.format(v, n, d) for v, g in enumerate(utils.get_graph().branches) for d, n in g.items() if v < n)));
print('var GROUPS = {};'.format(json.dumps(utils.load_groups())))
