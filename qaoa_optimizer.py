import pennylane as qml
from pennylane import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import streamlit as st
#Some Imp graph functions
def find_shortest_path(graph, start, end):
	shortest_path = nx.shortest_path(graph, source=start, target=end, weight='weight')
	total_weight = nx.shortest_path_length(graph, source=start, target=end, weight='weight')
	return shortest_path, total_weight

def make_random_directed_graph(nodes, seed=20):
    np.random.seed(seed)
    G = nx.DiGraph()
    for i in range(nodes // 2):
        for j in range(nodes // 2):
            x = np.random.randint(nodes)
            y = np.random.randint(nodes)
            while x == y:
                y = np.random.randint(nodes)
            weight = int(100*(1 + np.random.randint(nodes) / nodes))/100
            G.add_edge(str(x), str(y), weight=weight)
    return G

def draw_graph(graph):
    plt.clf()
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, font_weight='bold', node_size=700, node_color='skyblue', font_color='black', font_size=8, edge_color='gray')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels={(u, v): graph[u][v]['weight'] for u, v in graph.edges()})
    # plt.show()
    return None

def graph_from_list(input_list):
  G = nx.DiGraph()
  for edge in input_list:
    G.add_edge(str(edge[0]),str(edge[1]),weight = edge[2])
  return G

def count_paths(graph, start_node, end_node):
    try:
        paths = list(nx.all_simple_paths(graph, source=start_node, target=end_node))
        print(f"All paths from {start_node} to {end_node}: {paths}")
        return len(paths)
    except nx.NetworkXNoPath:
        print(f"No path found from {start_node} to {end_node}")
        return 0

def remove_unconnected_components(G):
  """
  Removes all unconnected components from a directed weighted networkx graph.

  Args:
    G: A directed weighted networkx graph.

  Returns:
    A new directed weighted networkx graph without unconnected components.
  """
  # Get all connected components
  connected_components = nx.weakly_connected_components(G)

  # Create a new graph
  H = nx.DiGraph()

  # Add nodes and edges from the largest connected component
  largest_component = max(connected_components, key=len)
  for node in largest_component:
    H.add_node(node)

  for u, v, data in G.edges(data=True):
    if u in largest_component and v in largest_component:
      H.add_edge(u,v)
      for k,v1 in data.items():
          H[u][v][k] = v1

  return H

# Example usage
def remove_edges_by_indices(G, indices):
  """
  Removes edges from a weighted networkx graph G based on their indices.

  Args:
      G: A NetworkX graph with edge weights.
      indices: A list of string or integer indices of the edges to remove.

  Returns:
      A new NetworkX graph with the specified edges removed.
  """
  # Create a copy of the graph to avoid modifying the original
  G_copy = nx.DiGraph(G)

  # Get the edges to remove based on their indices
  edges_to_remove = [list(G_copy.edges)[i] for i in indices]
  # Remove the specified edges
  G_copy.remove_edges_from(edges_to_remove)
  #print(G_copy.edges)
  # Update the graph with weights after removing edges
  
  for edge in G_copy.edges():
    # Get the weight of the edge from the original graph
    d = G.get_edge_data(edge[0],edge[1])
    for k,v in d.items():
          G_copy[edge[0]][edge[1]][k] = v
    # Add the weight back to the copied graph
    #G_copy.edges[edge[0], edge[1]]["weight"] = weight

  return G_copy
def solve2(edges, s, d, n):
    m = len(edges)

    c_k = [0] * (m)
    c_ij = [[0] * (m) for _ in range(m)]
    adj_from = [[] for _ in range(n)]
    adj_to = [[] for _ in range(n)]

    beg_at_s, end_at_d = [], []

    for i in range(m):
        c_k[i] += edges[i][2] / 2
        if edges[i][0] == s:
            beg_at_s.append(i)
        if edges[i][1] == d:
            end_at_d.append(i)
        adj_from[edges[i][0]].append(i)
        adj_to[edges[i][1]].append(i)

    n_s = len(beg_at_s)
    n_d = len(end_at_d)

    for i in beg_at_s:
        c_k[i] += globals()['M'] - (globals()['M'] * n_s) / 2
        for j in beg_at_s:
            c_ij[i][j] += globals()['M'] / 4

    for i in end_at_d:
        c_k[i] += globals()['M'] - (globals()['M'] * n_d) / 2
        for j in end_at_d:
            c_ij[i][j] += globals()['M'] / 4

    for k in range(0, n):
        if k == s or k == d:
            continue

        k1 = len(adj_to[k])
        k2 = len(adj_from[k])

        for i in adj_to[k]:
            c_k[i] += (globals()['M'] * (k2-k1)) / 2
            for j in adj_to[k]:
                c_ij[i][j] += globals()['M'] / 4

        for i in adj_from[k]:
            c_k[i] += (globals()['M'] * (k1-k2)) / 2
            for j in adj_from[k]:
                c_ij[i][j] += globals()['M'] / 4

        for i in adj_to[k]:
            for j in adj_from[k]:
                c_ij[i][j] -= globals()['M'] / 4
                c_ij[j][i] -= globals()['M'] / 4

    return np.array(c_k), np.array(c_ij)
import pennylane as qml
from pennylane import numpy as np
def cost_hamiltonian(n_qubits, beta, cx,c_ij):
    globals()['n_qubits'] = len(cx)
    for i in range(globals()['n_qubits']):
        qml.RZ(cx[i]*beta, wires=i)

    for i in range(globals()['n_qubits']):
        for j in range(globals()['n_qubits']):
            if (c_ij[i][j] == 0):
                continue
            if (i==j):
                continue
            qml.CNOT(wires=[i, j])
            qml.RZ(c_ij[i][j]*beta,wires=j)
            qml.CNOT(wires=[i, j])

def mixer_hamiltonian(n_qubits, gamma):
    for i in range(globals()['n_qubits']):
        qml.RX(gamma, wires=i)

def initialize_dev(n_qubits,m):
    globals()['M'] = m
    globals()['dev'] = qml.device("default.qubit",wires = n_qubits) 
    #globals()['dev'] = qml.device('qiskit.ibmq', wires=n_qubits, backend='ibmq_qasm_simulator', ibmqx_token="570584f081c13799d99654308f965658da9398c8b802cf4af4f2c1b2b115db94a60c583f116f821c9f69a4f4a0b4d6f25219b6cd94a9efc4517700f0c122caab")

    global objective
    @qml.qnode(globals()['dev'])
    def objective(betas,gammas,depth,c_k,c_ij):
        globals()['n_qubits'] = len(c_k)
        for i in range(globals()['n_qubits']):
            qml.Hadamard(wires=i)
        results = []
        for i in range(depth):
            cost_hamiltonian(globals()['n_qubits'],betas[i],c_k,c_ij)
            mixer_hamiltonian(globals()['n_qubits'],gammas[i])
        results = []
        for i in range(globals()['n_qubits']):
            results.append(qml.expval(qml.PauliZ(i)))
        return tuple(results)


def cost(betas,gammas,depth):
    globals()['n_qubits'] = len(globals()['c_k'])
    y = objective(betas,gammas,depth,globals()['c_k'],globals()['c_ij'])
    c_k = globals()['c_k']
    c_ij = globals()['c_ij']
    final = 0
    for i in range(globals()['n_qubits']):
        final += (c_k[i]*y[i])
    for i in range(globals()['n_qubits']):
        for j in range(globals()['n_qubits']):
            final += (y[i]*y[j]*c_ij[i][j])
    return final
def find_indices_greater_than_0_5(array):
  """
  Finds the indices of elements in an array that are greater than 0.5.

  Args:
      array: A NumPy array of values.

  Returns:
      A list of indices where the elements are greater than 0.5.
  """
  # Create an empty list to store the indices
  indices = []

  # Loop through each element in the array
  for i, element in enumerate(array):
    # Check if the element is greater than 0.5
    if element >= 0.4:
      # Add the index to the list
      indices.append(i)

  return indices
import time
def objective_to_understand(betas,gammas,depth,c_k,c_ij):
  globals()['n_qubits'] = len(c_k)
  for i in range(globals()['n_qubits']):
    qml.Hadamard(wires=i)
  results = []
  for i in range(depth):
    cost_hamiltonian(globals()['n_qubits'],betas[i],c_k,c_ij)
    mixer_hamiltonian(globals()['n_qubits'],gammas[i])
  for j in range(globals()['n_qubits']):
      #print(qml.expval(qml.PauliX(0)))
      results.append(qml.expval(qml.PauliZ(wires=[j])))
  return results
def cost2(betas,gammas,depth,c_k,c_ij,qnode):
    y = qnode(betas,gammas,depth,c_k,c_ij)
    return y
def suboptimizer(G,nodes,source,dest,opt,steps,depth,params):
    np.random.seed(69)
   # print("Current graph:")
   #
   # 
   # 
   # 
   # 
   #  draw_graph(G)
    edges_list = [[int(u), int(v), data['weight']] for u, v, data in G.edges(data=True)]
    s, d = int(source), int(dest)
  #  print("source: ", s,"dest: ",d)
    weights = np.array(edges_list)[:,2]
    globals()['c_k'], globals()['c_ij'] = solve2(edges_list, s, d, nodes)
    globals()['n_qubits'] = len(globals()['c_k'])
    #dev = qml.device("default.qubit", wires=globals()['n_qubits'])
    qnode = qml.QNode(objective, globals()['dev'])
    globals()['objective_list'] = [cost(params[0],params[1],depth)]
    print("Initial Objective =",globals()['objective_list'][-1])
    #y = cost(params[0],params[1],depth,c_k,c_ij)
    #print(type(y))
    #print(opt.step(cost,params[0],params[1],depth,c_k,c_ij))
    for i in range(steps):
        params, coste = opt.step_and_cost(cost,params[0],params[1],depth)
        if (i+1) %20 == 0:
            qnode = qml.QNode(objective_to_understand, globals()['dev'])
            results1 = cost2(params[0],params[1],depth,globals()['c_k'],globals()['c_ij'],qnode)
            qnode = qml.QNode(objective, globals()['dev'])
            if (np.max(results1)>=0.4):
                print("Removing edge!")
                return (params,results1,1,G)
            elif (np.max(results1)<=-0.75):
                print("Path Found!")
                return (params,results1,0,G)
            globals()['objective_list'] += [cost(params[0],params[1],depth)]
            print("Objective after step",i+1,"=",globals()['objective_list'][-1])
            print("Cost at step",i+1,"=",coste)
            globals()['params'] = params
    # st.pyplot(draw_graph(G))
    return (params,results1,0,G)
globals()['M'] = 65
G_final = nx.DiGraph()
def optimize_now(G,nodes,source,dest):
    np.random.seed(69)
    globals()['opt'] = qml.AdamOptimizer(stepsize = 1e-3)
    globals()['steps'] = 500
    globals()['depth'] = 25
    globals()['params'] = np.random.random((2,globals()['depth']),requires_grad = True)
    globals()['params'] , results, y1, G = suboptimizer(G,nodes,source,dest,globals()['opt'],globals()['steps'],globals()['depth'],globals()['params'])
    while(y1!=0):
        l = find_indices_greater_than_0_5(np.array(results))
      #  print("List - ",l)
        G = remove_edges_by_indices(G, l)
        if (len(G.edges()) == 1 and int(list(G.edges())[0][0]) == source and int(list(G.edges())[0][1]) == dest):
          y1=0
        else:
          globals()['params'] , results, y1, G = suboptimizer(G,nodes,source,dest,globals()['opt'],globals()['steps'],globals()['depth'],globals()['params'])
    return G
def timed_optimizer(G,nodes,source,dest):
    n_qubits = len(G.edges())
    #globals()['dev'] = qml.device("default.qubit",wires = n_qubits)
    #qnode = qml.QNode(objective, globals()['dev'])
    start_time = time.time()
    g = optimize_now(G,nodes,source,dest)
    end_time = time.time()
    g = remove_unconnected_components(g)
    globals()['optimization_time'] = end_time - start_time
    return g



