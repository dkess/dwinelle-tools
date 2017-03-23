#!/usr/bin/env python3

import utils

j = utils.load_nodes()

for n in j['nodes']:
    print(' '.join(map(str, n['branches'].values())))
