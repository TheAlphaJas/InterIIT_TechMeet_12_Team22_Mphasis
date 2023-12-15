import numpy as np
import networkx as nx
import pandas as pd

# mapping in inv matlab {0 : HYD}
# updownmap['FirstClass'] = ["F", 'B', 'E']
# updownmap => {F: [F, B], B: [B], E: [B, E]}

def allocate(G, path, mapping, affected_pnrs, source, dest, updownmap, cur_cab, strict, mct, rem):
    G_mod = G.copy()
    solution = False
    edge_ls = list(path.edges(data=True))
    for i in affected_pnrs:
        if 'proposed' in i:
            continue
        if (cur_cab not in updownmap[i['pnr_cabin']]) or (strict and cur_cab != i['pnr_cabin']):
            continue
        check = True
        for u, v, a in edge_ls:
            if mapping[u][:3] != mapping[v][:3]:
                if a[cur_cab] < i['pax_cnt']:
                    check = False
                    break
                if (mapping[u][:3] == source and i['min_time'] > pd.to_datetime(mapping[u][3:])) or (mapping[v][:3] == dest and i['max_time'] < pd.to_datetime(mapping[v][3:])):
                    check = False
                    break
        if check:
            solution = True
            i['proposed'] = []
            rem -= 1
            for u, v, a in edge_ls:
                if mapping[u][:3] != mapping[v][:3]:
                    if mapping[v][:3] == dest:
                        i['proposed'].append((mapping[u], mapping[v], cur_cab))
                    else:
                        i['proposed'].append((mapping[u], mapping[v][:3]+str(pd.to_datetime(mapping[v][3:]) - pd.Timedelta(hours=mct)), cur_cab))
                    a[cur_cab] -= i['pax_cnt']
    mn_cap = np.inf
    for u, v, a in edge_ls:
        if mapping[u][:3] != mapping[v][:3]:
            mn_cap = min(mn_cap, a[cur_cab])
    del_list = []
    for u, v, a in edge_ls:
        if mapping[u][:3] != mapping[v][:3]:
            if a[cur_cab] == mn_cap:
                del_list.append((u, v, a))
                G_mod.remove_edge(u, v)
    for u, v, a in edge_ls:
        if mapping[u][:3] != mapping[v][:3]:
            if G_mod.has_edge(u, v):
                G_mod[u][v][cur_cab] = a[cur_cab]
    return G_mod, affected_pnrs, rem, del_list