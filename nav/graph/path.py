# -*- coding: utf-8 -*-
"""graph_path.py

Description

Todo:
    * Add todo
"""
from nav.utility.classes import Location

from typing import List

import networkx as nx
import numpy as np
import numpy.linalg as linalg
from math import floor, ceil


def plan_graph_path(waypoints: List[Location], graph: nx.Graph,
         origin, params) -> np.ndarray:
    """Builds a path to the next waypoint(s)
    Args:
        graph: inside flight boundaries and outside obstacles
        waypoints: location waypoints to fly
    Returns:
        path: a list of locations corresponding to nodes in the graph path
    """
    # waypoints to nodes
    nodes = [point.to_grid(origin, params["granularity"]) for point in waypoints]

    # nodes to graph path
    paths = [nx.bidirectional_dijkstra(graph, source, target, weight='weight')[1]
             for source, target in zip(nodes[0:-1], nodes[1:])]

    path = []
    for p in paths:
        path += p[:-1]
    path += [paths[-1][-1]]

    return path

def quantize_graph_path(path: list, origin, params) -> np.ndarray:
    """Quantizes a given graph path -> a path in Rn. Guaranteed that endpoints are included
    Args:
        path: Contains a list of vertex names in order of the path.
        rn_path: A numpy array of points in r3 of each vertex in path, where the columns are each point.
        params: the algorithm parameters
    """
    path_coords = [list(Location.from_grid(node, origin, params["granularity"]))
                   for node in path]
    rn_path = np.array(path_coords).T

    if rn_path.shape[1] <= 1:
        raise ValueError('A path must have at least two points')
    
    dist_mat = linalg.norm(rn_path[:,:-1] - rn_path[:,1:], axis=0)
    total_norm = sum(dist_mat)
    
    quantization_distance = params["quantization_distance"]
    if total_norm <= quantization_distance:
        raise ValueError('A path\'s total distance must be larger than the quantization distance')

    curr_path_len = 0 # ∆(dist) between current quantization path and last node explored

    full_path = np.zeros((rn_path.shape[0], int(ceil(total_norm/quantization_distance))))
    curr_idx = 0

    for v_idx, edge_len in enumerate(dist_mat):
        curr_vertex, next_vertex = rn_path[:,v_idx], rn_path[:,v_idx+1]
        conv_comb = curr_path_len / edge_len
        n_iter = int(ceil((edge_len - curr_path_len)/quantization_distance))

        for _ in range(n_iter):
            assert conv_comb <= 1
            full_path[:,curr_idx] = (1-conv_comb)*curr_vertex + conv_comb*next_vertex
            conv_comb += quantization_distance/edge_len
            curr_idx += 1
        
        curr_path_len += n_iter*quantization_distance - edge_len
        assert curr_path_len >= 0.0

    return full_path
