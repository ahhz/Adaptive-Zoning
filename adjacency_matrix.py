from typing import List, Optional, Set, Tuple
from scipy.spatial import Delaunay
import numpy as np

class AdjacencyMatrix:
    """
    Keeps track of the adjacency relationships between zones.

    Initially, adjacency is determined based on Delaunay triangulation of the leaf zone centroids.
    When zones are merged, the adjacency matrix is updated to reflect the adjacency of the new
    merged zone with its neighbors.

    Attributes:
        adjacents (List[Set[int]]): A list where `adjacents[i]` is a set containing the indices
                                     of the zones adjacent to zone `i`.
    """
    def __init__(self, centroids: List[Tuple[float,float]]):
        """
        Initializes the adjacency matrix based on Delaunay triangulation of the given points.

        Args:
            centroids: A list of coordinate tuples (x, y) for each initial zone.
        """
        triangulation = Delaunay(np.array(centroids))
        adjacents = [set() for _ in centroids]
        for simplex in triangulation.simplices:
            for index in simplex:
                other = set(simplex)
                other.remove(index)
                adjacents[index] = adjacents[index].union(other)
        self._adjacents = adjacents

    def merge(self, children: Set[int]) -> Set[int]:
        """
        Updates the adjacency matrix after a merge of the given child zones into a new parent zone.

        The new parent zone becomes adjacent to all zones that were adjacent to any of its children,
        excluding the children themselves. The adjacency lists of the neighbors of the children
        are also updated to include the new parent zone and exclude the merged children.

        Args:
            children: A set of the indices of the child zones that were merged.

        Returns:
            Set[int]: A set of the indices of the zones that are now adjacent to the newly
                     created parent zone.
        """
        n = len(self._adjacents)
        child_sets = [self._adjacents[c] for c in children]
        merged = set.union(*child_sets) - children
        self._adjacents.append(merged)

        for i in merged :
            self._adjacents[i] = (self._adjacents[i] - children) | {n}

        return merged

    def get_all(self) -> List[Set[int]]:
        """
        Returns the current adjacency list for all zones.

        Returns:
            List[Set[int]]: A list where each element is a set of adjacent zone indices.
        """
        return self._adjacents
