# Copyright (c) 2025 Alex Hagen-Zanker
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import List, Optional, Set, Tuple

import matplotlib.axes
import matplotlib.figure
import matplotlib.pyplot as plt

from plot_adaptive_zoning import plot_agg_voronoi
from tree import Tree
from tree_data import TreeData
from cluster_maker import ClusterMaker
from neighbourhood_maker import NeighbourhoodMaker


class AdaptiveZoneSystem:
    """
    Implements the adaptive zoning method as published by Hagen-Zanker and 
    Jin (2012).

    This class performs hierarchical clustering of zones and then 
    determines a neighborhood of interacting zones for each initial (leaf) 
    zone.
 
    """
    def __init__(self, 
                 origins: List[float], 
                 destinations: List[float], 
                 weights: List[float],
                 centroids: List[Tuple[float, float]], 
                 beta: float, nbh_size: int):
        """
        Initializes the adative_zone_system.

        Args:
            origins (List[float]): A list of origin values for each initial 
                zone.
            destinations (List[float]): A list of destination values for 
                each initial zone.
            weights (List[float]): A list of weight values for each initial 
                zone.
            centroids (List[Tuple[float, float]]): A list of coordinate 
                tuples (x, y) for each initial zone, representing their 
                locations.
            beta (float): A parameter influencing the clustering and 
                neighborhood formation.
            nbh_size (int): The desired number of (leaf and aggregated) 
                zones that each leaf zone's neighborhood will include.
        """
        self._beta = beta
        self._nbh_size = nbh_size
        self._data = TreeData(origins, destinations, weights, centroids)
        clusterer = ClusterMaker(self._data, beta)
        self._zone_tree = clusterer.create()
        self._distance_matrix = clusterer.get_distance_matrix()
        neighbourhooder = NeighbourhoodMaker(self._data, beta, nbh_size, 
                                             self._zone_tree, 
                                             self._distance_matrix)
        self._neighbourhoods = neighbourhooder.create()
        self._transposed_neighbourhoods = None

    def get_tree(self) -> Tree:
        """
        Returns the hierarchical tree structure.

        Returns:
            The hierarchical tree structure (`tree` object).
        """
        return self._zone_tree

    def get_neighbourhoods(self) -> List[Set[int]]:
        """
        Returns the list of neighborhoods for each initial leaf zone.

        Returns:
            A list of neighborhoods, where each neighborhood is a set of 
            integer indices representing the zones (both leaf and aggregated) 
            that the corresponding initial leaf zone will interact with.
        """
        return self._neighbourhoods

    def get_beta(self) -> float:
        """
        Returns the beta parameter used for clustering and neighborhood 
        formation.

        Returns:
            The beta parameter (float).
        """
        return self._beta

    def get_neighbourhood_size(self) -> int:
        """
        Returns the neighborhood size.

        Returns:
            The desired number of zones in each leaf zone's neighborhood 
            (int).
        """
        return self._nbh_size

    def num_atomic_zones(self) -> int:
        """
        Returns the number of initial (leaf) zones.

        Returns:
            The number of initial leaf zones (int).
        """
        return self._zone_tree.get_num_leafs()

    def num_zones(self) -> int:
        """
        Returns the total number of zones in the hierarchical tree 
        (including aggregated zones).

        Returns:
            The total number of zones (int).
        """
        return self._zone_tree.get_size()

    def get_transposed_neighbourhoods(self) -> List[List[int]]:
        """
        Returns the transposed neighborhood list.

        This list indicates for each zone (by its index in the hierarchical
        tree), which initial leaf zones have it in their neighborhood.

        Returns:
            A list where each inner list contains the indices of the 
            initial leaf zones that include the current zone in their 
            neighborhood.
        """
        if self._transposed_neighbourhoods is not None:
            return self._transposed_neighbourhoods

        num_total_zones = self.num_zones()
        self._transposed_neighbourhoods = [
            [] for _ in range(num_total_zones)]
        for i, row in enumerate(self._neighbourhoods):
            for j in row:
                self._transposed_neighbourhoods[j].append(i)
        return self._transposed_neighbourhoods
    
    def map_leaf_zones_to_neighbourhood(self, center: int, 
                                        renumber: bool = False)->List[int]:
        out = [0 for _ in range(self._zone_tree.get_num_leafs())]
        for index, neighbour in enumerate(self._neighbourhoods[center]):
            leafs = self._zone_tree.get_leafs(neighbour)
            for leaf in leafs:
                out[leaf] = index if renumber else neighbour
        return out
    
    def map_leaf_zones_to_n_clusters(self, n: int, 
                                     renumber: bool = False)->List[int]:
        return self._zone_tree.map_leafs_to_n_groups(n, renumber)
   
    def plot_n_clusters_voronoi(self, n : int, 
                                ax: Optional[matplotlib.axes.Axes] = None
                                ) -> matplotlib.axes.Axes:
        if ax is None:
            fig, ax = plt.subplots()
        agg = self.map_leaf_zones_to_n_clusters(n, True)
        num_leafs = self._zone_tree.get_num_leafs()
        leaf_centroids = self._data.centroids[:num_leafs]
        plot_agg_voronoi(leaf_centroids, agg, ax)
        return ax

    def plot_neighbourhood_voronoi(self, center : int, 
                                   ax: Optional[matplotlib.axes.Axes] = 
                                   None) -> matplotlib.axes.Axes:
        if ax is None:
            fig, ax = plt.subplots()
        agg = self.map_leaf_zones_to_neighbourhood(center, True)
        num_leafs = self._zone_tree.get_num_leafs()
        leaf_centroids = self._data.centroids[:num_leafs]
        plot_agg_voronoi(leaf_centroids, agg, ax)
        return ax 

