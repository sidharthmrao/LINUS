from typing import Dict, List, Tuple, Set
import pygame
import heapq
import time


class Graph:
    def __init__(self, coords: List[Tuple[int, int]]):
        self.edges = {}
        self.coords = coords

        for i in range(len(coords)):
            self.add_node(i)

    def add_node(self, index: int):
        self.edges[index] = set()

    def add_edge(self, index1: int, index2: int):
        self.edges[index1].add(index2)
        self.edges[index2].add(index1)

    def get_neighbors(self, index: int) -> Set[int]:
        return self.edges[index]

    def get_coord(self, index: int) -> Tuple[int, int]:
        return self.coords[index]


class Subgraph:
    def __init__(self, coords: List[Tuple[int, int]]):
        self.edges: Dict[int, Dict[int, float]] = {}
        self.paths: Dict[int, Dict[int, List[int]]] = {}
        self.coords = coords

    def add_node(self, index: int):
        self.edges[index] = {}
        self.paths[index] = {}

    def add_edge(self, index1: int, index2: int, path: List[int]):
        if index1 not in self.edges:
            self.add_node(index1)
        if index2 not in self.edges:
            self.add_node(index2)

        self.edges[index1][index2] = len(path)
        self.edges[index2][index1] = len(path)
        self.paths[index1][index2] = path
        self.paths[index2][index1] = path[::-1]

    def remove_edge(self, index1: int, index2: int):
        del self.edges[index1][index2]
        del self.edges[index2][index1]
        del self.paths[index1][index2]
        del self.paths[index2][index1]

    def remove_node(self, index):
        del self.edges[index]
        del self.paths[index]

    def get_neighbors(
        self, index: int
    ) -> Tuple[Dict[int, float], Dict[int, List[int]]]:
        return (self.edges[index], self.paths[index])

    def get_coord(self, index: int) -> Tuple[int, int]:
        return self.coords[index]


def intersection_subgraph(
    graph: Graph,
    subgraph: Subgraph,
    inter_node: int,
    start_node: int,
    visited: Set[int],
) -> Subgraph:
    """
    Constructs a subgraph from a given graph, starting from a specified node and
    traversing through its neighbors. The function identifies intersections and
    dead ends as subgraph nodes, adding paths between these points as edges.
    """

    # Path from start_node to next intersection
    path = []

    if start_node != 0:
        path.append(start_node)

    curr_node = start_node
    current_options = graph.get_neighbors(curr_node)

    for i in list(current_options):
        if i in visited:
            current_options.remove(i)

    visited.add(curr_node)

    while current_options:
        if len(current_options) == 1:  # Regular point, not an intersection
            changed = False

            for option in current_options:
                if option not in visited:
                    curr_node = option
                    changed = True

            # Dead end
            if not changed:
                break

            visited.add(curr_node)
            path.append(curr_node)

            current_options: Set[int] = graph.get_neighbors(curr_node)
            for option in list(current_options):
                if option in visited:
                    current_options.remove(option)

        else:  # Intersection point
            for option in list(current_options):
                if option not in visited:
                    intersection_subgraph(graph, subgraph, curr_node, option, visited)
                current_options.remove(option)

            if (
                curr_node in subgraph.edges and len(subgraph.edges[curr_node]) > 1
            ):  # More than one path added to intersection
                # Add the path to subgraph

                if len(path) > 10 or inter_node == curr_node:
                    subgraph.add_edge(inter_node, curr_node, path)
                else:
                    for other in list(subgraph.edges[curr_node].keys()):
                        subgraph.add_edge(
                            inter_node, other, path + subgraph.paths[curr_node][other]
                        )
                        subgraph.remove_edge(curr_node, other)

            elif curr_node in subgraph.edges and len(subgraph.edges[curr_node]) == 1:
                # One path added, consolidate with current path
                other = list(subgraph.edges[curr_node].keys())[0]

                if inter_node != curr_node:
                    subgraph.add_edge(
                        inter_node, other, path + subgraph.paths[curr_node][other]
                    )
                    subgraph.remove_edge(curr_node, other)
            else:
                subgraph.add_edge(inter_node, curr_node, path)

    # Reached a dead end, gen a new intersection here and terminate
    if path:
        endpoint = path.pop(-1)

        if len(path) > 10:  # Keep only dead ends that are large enough to see
            subgraph.add_edge(inter_node, endpoint, path)

    return subgraph


def reduce_subgraph(subgraph: Subgraph, root: int) -> Subgraph:
    """
    Consolidate all nodes within some cartesian distance of each other into a single node.
    """

    new_subgraph = Subgraph(subgraph.coords)

    curr = root
    new_subgraph.add_node(curr)
    visited = set()
    visited.add(curr)
    queue = [curr]

    cluster_parent = {curr: curr}

    while queue:
        current = queue.pop(0)

        current_coord = subgraph.get_coord(current)

        neighbors = subgraph.get_neighbors(current)[0]

        for i in neighbors:
            other_coord = subgraph.get_coord(i)
            dist = (
                (current_coord[0] - other_coord[0]) ** 2
                + (current_coord[1] - other_coord[1]) ** 2
            ) ** 0.5

            if dist < 5:
                cluster_parent[i] = cluster_parent[current]
            else:
                cluster_parent[i] = i

            if i not in visited:
                visited.add(i)
                queue.append(i)

    for i in cluster_parent:
        neighbors = subgraph.get_neighbors(i)[0]

        for j in neighbors:
            if cluster_parent[i] != cluster_parent[j]:
                new_subgraph.add_edge(
                    cluster_parent[i], cluster_parent[j], subgraph.paths[i][j]
                )

    return new_subgraph


def shortest_path(graph: Subgraph, index_a: int, index_b: int) -> List[int] | None:
    prev = {index_a: (None, 0)}
    visited = set()
    queue = [index_a]

    while queue:
        current = queue.pop(0)
        neighbors = graph.get_neighbors(current)[0]

        for i in neighbors:
            if i in graph.edges[current]:
                dist = graph.edges[current][i]
                if i not in prev or prev[i][1] > dist + prev[current][1]:
                    prev[i] = (current, dist + prev[current][1])

            if i not in visited:
                visited.add(i)
                queue.append(i)

    if index_b not in prev:
        return None

    path = []
    current = index_b
    while current is not None:
        path.append(current)
        current = prev[current][0]
    path.reverse()
    return path


def shortest_graph_path(
    graph: Graph, index_a: int, index_b: int, screen
) -> List[int] | None:
    prev = {index_a: (None, 0)}
    visited = set()
    queue = [index_a]
    while queue:
        current = queue.pop(0)
        # print(current)
        neighbors = graph.get_neighbors(current)

        for i in neighbors:
            if i in graph.edges[current]:
                if i not in prev or prev[i][1] > 1 + prev[current][1]:
                    prev[i] = (current, 1 + prev[current][1])

            if i not in visited:
                visited.add(i)
                queue.append(i)

    if index_b not in prev:
        return None

    path = []
    current = index_b
    while current is not None:
        path.append((int(graph.coords[current][0]), int(graph.coords[current][1])))
        current = prev[current][0]
    path.reverse()

    if path is None:
        return None

    return path


def shortest_graph_path_coords(
    graph: Graph, coord_a: Tuple[int, int], coord_b: Tuple[int, int], screen
) -> List[int] | None:
    """
    Returns the shortest path between two coordinates in a graph. Returns None if no path found.
    """

    index_a = None
    index_b = None

    for i in range(len(graph.coords)):
        if graph.coords[i][0] == int(coord_a[0]) and graph.coords[i][1] == int(
            coord_a[1]
        ):
            index_a = i
        if graph.coords[i][0] == int(coord_b[0]) and graph.coords[i][1] == int(
            coord_b[1]
        ):
            index_b = i

    if index_a is None or index_b is None:
        return None

    return shortest_graph_path(graph, index_a, index_b, screen)


def shortest_subgraph_path(
    graph: Subgraph, index_a: int, index_b: int, screen
) -> List[int] | None:
    """
    Returns the shortest path between two nodes in a subgraph. Returns None if no path found.
    """

    if screen is not None:
        screen.fill((0, 0, 0))

        for i in graph.edges:
            pygame.draw.circle(screen, (255, 255, 255), graph.coords[i], 1)
        pygame.draw.circle(screen, (0, 255, 0), graph.coords[index_a], 1)
        pygame.draw.circle(screen, (0, 255, 0), graph.coords[index_b], 1)
        pygame.display.flip()

    path = shortest_path(graph, index_a, index_b)
    if path is None:
        return None

    full_path = []
    for i in range(len(path) - 1):
        full_path.extend(graph.paths[path[i]][path[i + 1]])
    for i in range(len(full_path)):
        full_path[i] = (
            int(graph.coords[full_path[i]][0]),
            int(graph.coords[full_path[i]][1]),
        )

        if screen is not None:
            pygame.draw.circle(screen, (255, 0, 0), full_path[i], 1)
            pygame.display.flip()
            time.sleep(0.01)

    return full_path


class CostTreeNode:
    """
    Node in a cost tree.
    """

    def __init__(self, node: int, prev):
        self.node = node
        self.prev = prev

        self.children = {}

    def add_child(self, node, cost: float):

        self.children[node.node] = [node, 0]

        self.backprop_cost(cost, node.node)

    def backprop_cost(self, cost: float, node: int):
        self.children[node][1] += cost

        if self.prev:
            self.prev.backprop_cost(cost, self.node)


def construct_tree(subgraph: Subgraph) -> CostTreeNode:
    """
    Construct a cost tree from a subgraph where each node represents a point in the subgraph
    and its cost is the sum of the costs of its children. This cost effectively
    represents the total area covered by a branch of a tree and all its children (including edge lengths).
    """

    root = CostTreeNode(0, None)
    curr = root

    stack = [root]
    visited = set()
    visited.add(root.node)

    while stack:
        curr = stack.pop(-1)

        neighbors, neighbor_paths = subgraph.get_neighbors(curr.node)

        for i in neighbors:
            if i not in visited:
                visited.add(i)

                new_node = CostTreeNode(i, curr)
                stack.append(new_node)

                curr.add_child(new_node, len(neighbor_paths[i]))

    return root


def dfs_priority_order(subgraph: Subgraph, curr: CostTreeNode) -> List[int]:
    children = list(curr.children.keys())
    children.sort(key=lambda k: curr.children[k][1])

    path = [curr.node]

    for i in children:
        subgraph_path_curr_to_child = subgraph.paths[curr.node][i]
        point_a = len(subgraph_path_curr_to_child) // 3
        point_b = len(subgraph_path_curr_to_child) // 2
        point_c = int(len(subgraph_path_curr_to_child) // 1.3)
        path.append(subgraph_path_curr_to_child[point_a])
        path.append(subgraph_path_curr_to_child[point_b])
        path.append(subgraph_path_curr_to_child[point_c])

        path.extend(dfs_priority_order(subgraph, curr.children[i][0]))

    return path


def path_constructor(
    graph: Graph, subgraph: Subgraph, root: int, screen
) -> List[Tuple[int, int]] | None:
    """
    Constructs a path from a list of nodes in a subgraph, returning the coordinates of each node in the path.
    """

    ordering = dfs_priority_order(subgraph, construct_tree(subgraph))
    visited = set()
    visited.add(root)

    curr = root

    path = []

    for i in ordering:
        if i not in visited:
            visited.add(i)
            shortest = shortest_graph_path(graph, curr, i, screen)
            if shortest:
                path.extend(shortest)
                for j in shortest:
                    visited.add(j)
            else:
                return None

            curr = i

    return path
