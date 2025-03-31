from typing import List, Optional, Set, Tuple

from tree_data import tree_data
from cluster_maker import cluster_maker
from neighbourhood_maker import neighbourhood_maker


class adaptive_zone_system:
    """
    Implements the adaptive zoning method as published by Hagen-Zanker and Jin (2012).

    This class performs hierarchical clustering of zones and then determines a
    neighborhood of interacting zones for each initial (leaf) zone.

    Attributes:
        beta (float): A parameter influencing the clustering and neighborhood formation.
        nbh_size (int): The desired number of (leaf and aggregated) zones that each leaf zone's
                          neighborhood will aim to include.
        zone_tree: The hierarchical tree structure resulting from the clustering process.
        distance_matrix: The distance matrix calculated during the clustering process.
        neighbourhoods (List[Set[int]]): A list of neighborhoods, where each neighborhood is a
                                          set of integer indices representing the zones (both leaf
                                          and aggregated) that the corresponding initial leaf zone
                                          will interact with. The order of neighborhoods in the
                                          list corresponds to the order of the initial leaf zones.
        transposed_neighbourhoods (Optional[List[List[int]]]): A list where each inner list contains
                                                               the indices of the initial leaf zones
                                                               that consider the current zone (by
                                                               index) as part of their neighborhood.
                                                               This is computed lazily.

    Args:
        origins (List[float]): A list of origin values for each initial zone.
        destinations (List[float]): A list of destination values for each initial zone.
        weight (List[float]): A list of weight values for each initial zone.
        points (List[Tuple[float, float]]): A list of coordinate tuples (x, y) for each initial zone,
                                            representing their locations.
        beta (float): A parameter influencing the clustering and neighborhood formation.
        nbh_size (int): The desired number of (leaf and aggregated) zones that each leaf zone's
                          neighborhood will aim to include.
    """
    def __init__(self, origins: List[float], destinations: List[float], weight: List[float],
                 points: List[Tuple[float, float]], beta: float, nbh_size: int):
        """
        Initializes the adative_zone_system.

        Args:
            origins (List[float]): A list of origin values for each initial zone.
            destinations (List[float]): A list of destination values for each initial zone.
            weight (List[float]): A list of weight values for each initial zone.
            points (List[Tuple[float, float]]): A list of coordinate tuples (x, y) for each initial zone,
                                                representing their locations.
            beta (float): A parameter influencing the clustering and neighborhood formation.
            nbh_size (int): The desired number of (leaf and aggregated) zones that each leaf zone's
                              neighborhood will aim to include.
        """
        self.beta = beta
        self.nbh_size = nbh_size
        data = tree_data(origins, destinations, weight, points)
        clusterer = cluster_maker(data, beta)
        self.zone_tree = clusterer.create()
        self.distance_matrix = clusterer.get_distance_matrix()
        neighbourhooder = neighbourhood_maker(data, beta, nbh_size, self.zone_tree, self.distance_matrix)
        self.neighbourhoods = neighbourhooder.create()
        self.transposed_neighbourhoods = None

    def get_tree(self):
        """
        Returns the hierarchical tree structure.

        Returns:
            The hierarchical tree structure (`tree` object).
        """
        return self.zone_tree

    def get_neighbourhoods(self) -> List[Set[int]]:
        """
        Returns the list of neighborhoods for each initial leaf zone.

        Returns:
            A list of neighborhoods, where each neighborhood is a set of integer indices
            representing the zones (both leaf and aggregated) that the corresponding
            initial leaf zone will interact with.
        """
        return self.neighbourhoods

    def get_beta(self) -> float:
        """
        Returns the beta parameter used for clustering and neighborhood formation.

        Returns:
            The beta parameter (float).
        """
        return self.beta

    def get_neighbourhood_size(self) -> int:
        """
        Returns the neighborhood size.

        Returns:
            The desired number of zones in each leaf zone's neighborhood (int).
        """
        return self.nbh_size

    def num_atomic_zones(self) -> int:
        """
        Returns the number of initial (leaf) zones.

        Returns:
            The number of initial leaf zones (int).
        """
        return self.zone_tree.get_num_leafs()

    def num_zones(self) -> int:
        """
        Returns the total number of zones in the hierarchical tree (including aggregated zones).

        Returns:
            The total number of zones (int).
        """
        return self.zone_tree.get_size()

    def get_transposed_neighbourhoods(self) -> List[List[int]]:
        """
        Returns the transposed neighborhood list.

        This list indicates for each zone (by its index in the hierarchical tree),
        which initial leaf zones consider it part of their neighborhood.

        Returns:
            A list where each inner list contains the indices of the initial leaf zones
            that include the current zone in their neighborhood.
        """
        if self.transposed_neighbourhoods is not None:
            return self.transposed_neighbourhoods

        num_total_zones = self.num_zones()
        self.transposed_neighbourhoods = [[] for _ in range(num_total_zones)]
        for i, row in enumerate(self.neighbourhoods):
            for j in row:
                self.transposed_neighbourhoods[j].append(i)
        return self.transposed_neighbourhoods

# to be removed:it is better to use the class interface.
def adaptive_zoning(origins: List[float], destinations: List[float], weight: List[float], 
                    points: List[Tuple[float, float]], beta: float, nbh_size: int):
        zone_system = adaptive_zone_system(origins, destinations, weight, points, beta, nbh_size)
        return zone_system.get_neighbourhoods(),zone_system.get_tree()
