import networkx as nx
from qaoa_optimizer import timed_optimizer,initialize_dev

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
        old_source, old_target, weight = edge
        new_source, new_target = mapping_dict[old_source], mapping_dict[old_target]
        print("s t",new_source,new_target)
        new_graph.add_edge(new_source, new_target, weight=weight['weight'])
    
    return new_graph, mapping_dict

def bbx(Graph,source,dest):
    #MAP GRAPH NODES TO INTEGERS
    G_m,mapping = convert_graph_to_int_nodes(Graph)
   # G_m.add_edge(2,5,weight = 30)
    print(G_m.edges())
    print(len(G_m.edges(data=True)))
    #G_m = negate_edge_weights(G_m)
    print(G_m.edges())
    print(len(G_m.edges(data=True)))
    print("map - ",mapping)
    #initialize_dev(len(G_m.edges),65)
    #G_f = timed_optimizer(G_m,len(G_m.nodes),source,dest)
    return G_m