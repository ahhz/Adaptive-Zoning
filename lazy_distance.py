from math import sqrt
from typing import List, Optional, Set, Tuple

from tree import tree

class lazy_distance:
    """
    Calculates and caches the distances between zones in the hierarchical tree.

    For leaf nodes, the distance is the Euclidean distance between their centroids.
    For non-leaf nodes (merged zones), the distance to another zone is the weighted
    average of the distances from its children to that zone, using the children's weights.
    Distances are calculated on demand and stored in a cache (`matrix`) to avoid
    redundant computations.

    Attributes:
        matrix (List[Dict[int, float]]): A list where each element is a dictionary.
                                          `matrix[i]` stores the distances from zone `i`
                                          to other zones `j` (where `j > i`). The keys of
                                          the inner dictionary are the indices `j`, and the
                                          values are the calculated distances.
        points (List[Tuple[float, float]]): A list of coordinate tuples (x, y) for each zone.
        zone_tree (tree): The hierarchical tree structure of the zones.
        weights (List[float]): A list of weight values for each zone.
    """
    def __init__(self, points: List[Tuple[float,float]], zone_tree: tree, weights: List[float]):
        """
        Initializes the lazy distance calculator.

        Args:
            points: A list of coordinate tuples (x, y) for each initial zone.
            zone_tree: The hierarchical tree structure of the zones.
            weights: A list of weight values for each initial zone.
        """
        self.matrix = [dict() for _ in range(len(points))]
        self.points = points
        self.zone_tree = zone_tree
        self.weights = weights

    def get(self, i: int, j: int) -> float:
        """
        Returns the distance between zone `i` and zone `j`.

        If the distance has already been calculated, it is retrieved from the cache (`self.matrix`).
        Otherwise, it is calculated based on whether `j` is a leaf or a merged zone.
        Leverages the symmetry of distance (distance between i and j is the same as j and i)
        to store only one of the pairs (where the first index is smaller).

        Args:
            i: The index of the first zone.
            j: The index of the second zone.

        Returns:
            float: The distance between zone `i` and zone `j`.
        """
        if i > j:
            i,j = j,i

        if j in self.matrix[i]:
            return self.matrix[i][j]

        # assuming that the index of leafs is always lower than non-leafs
        children = self.zone_tree.get_children(j)
        if children:
            dij = sum([self.weights[c] * self.get(i,c) for c in children]) / self.weights[j]
        else:
            dx = self.points[i][0]-self.points[j][0]
            dy = self.points[i][1]-self.points[j][1]
            dij = sqrt(dx**2+dy**2)

        self.matrix[i][j] = dij
        return dij

    def add_zone(self):
        """
        Adds a new empty dictionary to the `matrix` when a new merged zone is created,
        to hold distances from this new zone to others.
        """
        self.matrix.append(dict())
