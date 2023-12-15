import networkx as nx
from qaoa_optimizer import timed_optimizer,initialize_dev
from allocate import allocate
def negate_edge_weights(G):
  """
  Negate all edge weights in a NetworkX graph.

  Args:
    G: A NetworkX graph with edge weights.

  Returns:
    A new NetworkX graph with the same structure as G but with all edge weights negated.

  Raises:
    ValueError: If the graph has no edges or no edge weights.
  """

  if not G.edges:
    raise ValueError("Graph must have at least one edge.")

  # Check if any edge has a weight attribute defined
  if not any(G.get_edge_data(u, v).get("weight", None) for u, v in G.edges):
    raise ValueError("Graph must have edge weights defined.")

  # Create a new graph with the same structure as G
  H = nx.Graph(copy=True)
  H.add_nodes_from(G.nodes)

  # Iterate over edges and set weight to negative of original weight
  for u, v, data in G.edges(data=True):
    H.add_edge(u, v, weight=-data["weight"])

  return H

def convert_graph_to_int_nodes(graph):
    # Create a new directed graph with integer nodes
    new_graph = nx.DiGraph()
    
    # Mapping dictionary to store the correspondence between old and new nodes
    mapping_dict = {}
    
    # Iterate through the nodes of the original graph and add them to the new graph with integer nodes
    for old_node in graph.nodes:
        new_node = len(mapping_dict)  # Assign a new integer node ID
        mapping_dict[old_node] = new_node
        new_graph.add_node(new_node)
    
    # Iterate through the edges of the original graph and add them to the new graph with integer nodes
    for edge in graph.edges(data=True):
        (old_source, old_target, a) = edge
        print(old_source,old_target,a)
        #print(weight)
        new_source, new_target = mapping_dict[old_source], mapping_dict[old_target]
        new_graph.add_edge(new_source, new_target)
        for k,v in a.items():
          new_graph[new_source][new_target][k] = v
    
    return new_graph, mapping_dict


def check_graph_properties(graph, s, d):
    # Check the number of connected components
    connected_components = list(nx.weakly_connected_components(graph))
    if len(connected_components) != 1:
        return False

    # Check if there is exactly one edge starting at 's'
    f1 = 0 
    f2 = 0
    for u,v in graph.edges():
       if u == s or v == s:
          f1=1
       if u == d or v == d:
          f2=1
       if (f1 and f2):
          return True

    return False
   
def bbx(Graph,source,dest,listofpnr,MCT,updownmap):
    rem = len(listofpnr)
    print("intial REM ",rem)
    #MAP GRAPH NODES TO INTEGERS
    G_m,mapping = convert_graph_to_int_nodes(Graph)
    print("HERE")
    print(G_m.edges(data=True))
    G_mod = G_m.copy()
    print("HERE")
    print(G_mod.edges(data=True))
    print(mapping)
    source = mapping[source]
    dest = mapping[dest]
    mapping1 = {v: k for k, v in mapping.items()}
   # G_m.add_edge(2,5,weight = 30)
   # print(G_m.edges())
   # print(len(G_m.edges(data=True)))
    #G_m = negate_edge_weights(G_m)
   # print(G_m.edges())
   # print(len(G_m.edges(data=True)))
   # print("map - ",mapping)
    initialize_dev(len(G_m.edges),65)
    classes = ['FirstClass','BusinessClass','EconomyClass','PremiumEconomyClass']
    cnt = 0
    for cabin in classes:
       print(cnt)
       cnt+=1
       #G_mod = G_m.copy()
       #rpnr = 1
       lode = []
       while(rem>0):
        path = timed_optimizer(G_mod,len(G_mod.nodes),source,dest)
        print(mapping)
        print("REM ",rem )
        print(path.edges(data=True))
        if (not check_graph_properties(path,source,dest)):
           break
        G_mod,listofpnr,rem,listofdeletededges = allocate(G_mod,path,mapping1,listofpnr,mapping1[source][:3],mapping1[dest][:3],updownmap,cabin,False,MCT,rem)
        lode.extend(listofdeletededges)
       for u,v,a in lode:
         G_mod.add_edge(u,v)
         for n,m in a.items():
            G_mod[u][v][n] = m
    
    for cabin in classes:
       print(cnt)
       cnt += 1
       #G_mod = G_m.copy()
       #rpnr = 1
       lode = []
       while(rem>0):
        path = timed_optimizer(G_mod,len(G_mod.nodes),source,dest)
        print(mapping)
        print("REM ",rem )
        print(path.edges(data=True))
        if (not check_graph_properties(path,source,dest)):
           break
        G_mod,listofpnr,rem,listofdeletededges = allocate(G_mod,path,mapping1,listofpnr,mapping1[source][:3],mapping1[dest][:3],updownmap,cabin,True,MCT,rem)
        lode.extend(listofdeletededges)
       for u,v,a in lode:
         G_mod.add_edge(u,v)
         for n,m in a.items():
            G_mod[u][v][n] = m
    print("final REM ",rem)
    return listofpnr