import copy
import numpy as np
from skimage.morphology import skeletonize, thin, medial_axis
from scipy.spatial.distance import cdist
from sklearn.cluster import DBSCAN

from lib.graph import *
from lib.render import *


def path_dist(a, b):
    """
    Calculate the smallest distance between two points in path a and b
    """

    A = np.array(a)
    B = np.array(b)

    # Compute full pairwise distance matrix
    dist_matrix = cdist(A, B)

    # Find index of the smallest distance
    min_idx_flat = np.argmin(dist_matrix)
    min_distance = dist_matrix.flat[min_idx_flat]

    # Convert flat index to 2D index (i, j)
    i, j = np.unravel_index(min_idx_flat, dist_matrix.shape)

    nearest_point_in_A = A[i]
    nearest_point_in_B = B[j]

    return min_distance, nearest_point_in_A, nearest_point_in_B


def prim_mst(matrix):
    num_nodes = matrix.shape[0]
    selected = [False] * num_nodes
    parent = [-1] * num_nodes
    key = [float("inf")] * num_nodes

    key[0] = 0  # Start from node 0

    for _ in range(num_nodes):
        # Pick the minimum key vertex not yet included
        u = min((i for i in range(num_nodes) if not selected[i]), key=lambda x: key[x])
        selected[u] = True

        # Update key and parent for adjacent vertices
        for v in range(num_nodes):
            if matrix[u][v] != 0 and not selected[v] and matrix[u][v] < key[v]:
                key[v] = matrix[u][v]
                parent[v] = u

    # Build list of MST edges
    mst_edges = []
    for v in range(1, num_nodes):
        mst_edges.append((parent[v], v))
    return mst_edges


def build_adjacency_list(edges, num_nodes):
    adj = [[] for _ in range(num_nodes)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj


def dfs_traversal(adj, start=0, visited=None, path=None):
    if visited is None:
        visited = [False] * len(adj)
    if path is None:
        path = []

    visited[start] = True
    path.append(start)

    for neighbor in adj[start]:
        if not visited[neighbor]:
            dfs_traversal(adj, neighbor, visited, path)
            # Optional: include backtracking step if you want explicit path
            path.append(start)

    return path


def slice(skeleton, screen):
    # Get all skeleton coordinates
    coords = np.column_stack(np.where(skeleton))

    # DBSCAN clustering on coordinates
    dbscan = DBSCAN(eps=5, min_samples=1)
    dbscan.fit(coords)
    labels = dbscan.labels_
    unique_labels = np.unique(labels)
    clusters = []
    for label in unique_labels:
        cluster_coords = coords[labels == label]
        clusters.append(cluster_coords)
    # Sort clusters by size
    clusters.sort(key=len, reverse=True)

    graphs = []

    paths = []

    traversal = []

    for cluster in clusters:
        dists = cdist(cluster, cluster)

        graphs.append(Graph(cluster))

        for i in range(len(cluster)):
            # Get all indices less than 2
            indices = np.where(dists[i] <= 2**0.5)[0]

            for j in indices:
                if j != i and (int(j), float(dists[i][j])) not in graphs[
                    -1
                ].get_neighbors(i):
                    graphs[-1].add_edge(int(i), int(j))

        root = 0

        graph = copy.deepcopy(graphs[-1])

        try:
            subgraph: Subgraph = reduce_subgraph(
                intersection_subgraph(graphs[-1], Subgraph(cluster), root, root, set()),
                root,
            )

            # draw_subgraph(screen, subgraph)

            path = path_constructor(graph, subgraph, root, screen)
            graphs[-1] = graph

            if path:
                paths.append(path)
        except:
            pass

    path_dist_matrix = np.zeros((len(paths), len(paths)))
    nearest_points = {}

    for i in range(len(paths)):
        for j in range(len(paths)):
            if i <= j:
                continue

            path_dist_matrix[i][j], nearest_a, nearest_b = path_dist(paths[i], paths[j])
            path_dist_matrix[j][i] = path_dist_matrix[i][j]

            nearest_points[(i, j)] = (nearest_a, nearest_b)
            nearest_points[(j, i)] = (nearest_b, nearest_a)

    mst = prim_mst(path_dist_matrix)
    adj_matrix = build_adjacency_list(mst, len(paths))
    opt_order = dfs_traversal(adj_matrix)

    visited = set()

    for i in range(len(opt_order) - 2):

        a = opt_order[i]
        b = opt_order[i + 1]

        if a not in visited:
            visited.add(a)

            traversal.extend(paths[a])

            if len(visited) == len(paths):
                break

            sp = shortest_graph_path_coords(
                graphs[a], paths[a][-1], nearest_points[(a, b)][0], screen
            )
            if sp:
                traversal.extend(sp)
        else:
            if i != 0:
                sp = shortest_graph_path_coords(
                    graphs[a],
                    nearest_points[(opt_order[i - 1], a)][1],
                    nearest_points[(a, b)][0],
                    screen,
                )
                if sp:
                    traversal.extend(sp)

        traversal.append(nearest_points[(a, b)][1])

    return traversal
