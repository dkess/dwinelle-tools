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
        except (IndexError, KeyError) as e:
            print('err')

