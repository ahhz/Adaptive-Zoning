from typing import List, Optional, Set, Tuple

from tree_data import tree_data
from cluster_maker import cluster_maker
from neighbourhood_maker import neighbourhood_maker

def adaptive_zoning(origins: List[float], destinations: List[float], weight: List[float], 
                    points: List[Tuple[float, float]], beta: float, nbh_size: int):
    """
    Implements the adaptive zoning method as published by Hagen-Zanker and Jin (2012).

    This function performs hierarchical clustering of zones and then determines a
    neighborhood of interacting zones for each initial (leaf) zone.

    Note: The input lists `origins`, `destinations`, and `weight` will be modified
    in-place during the clustering process. If you need to preserve the original
    data, pass copies of these lists to the function.

    Args:
        origins: A list of origin values for each initial zone.
        destinations: A list of destination values for each initial zone.
        weight: A list of weight values for each initial zone.
        points: A list of coordinate tuples (x, y) for each initial zone, representing their locations.
        beta: A float parameter influencing the clustering and neighborhood formation.
        nbh_size: The desired number of (leaf and aggregated) zones that each leaf zone's
                  neighborhood will aim to include.

    Returns:
        Tuple[List[Set[int]], tree]: A tuple containing:
            - A list of neighborhoods, where each neighborhood is a set of integer indices
              representing the zones (both leaf and aggregated) that the corresponding
              initial leaf zone will interact with. The order of neighborhoods in the list
              corresponds to the order of the initial leaf zones.
            - The hierarchical tree structure (`tree` object) resulting from the clustering process.
    """
    data = tree_data(origins, destinations, weight, points)
    clusterer = cluster_maker(data, beta)
    zone_tree = clusterer.create()
    distance_matrix = clusterer.get_distance_matrix()
    neighbourhooder = neighbourhood_maker(data, beta, nbh_size, zone_tree, distance_matrix)
    neighbourhoods = neighbourhooder.create()
    return neighbourhoods, zone_tree
