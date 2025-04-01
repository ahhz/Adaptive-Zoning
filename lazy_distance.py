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

from math import sqrt
from typing import List, Optional, Set, Tuple

from tree import Tree

class LazyDistance:
    """
    Calculates and caches the distances between zones in the hierarchical tree.

    For leaf nodes, the distance is the Euclidean distance between their centroids.
    For non-leaf nodes (merged zones), the distance to another zone is the weighted
    average of the distances from its children to that zone, using the children's weights.
    Distances are calculated on demand and stored in a cache (`matrix`) to avoid
    redundant computations.

    """
    def __init__(self, centroids: List[Tuple[float,float]], zone_tree: Tree, weights: List[float]):
        """
        Initializes the lazy distance calculator.

        Args:
            points: A list of coordinate tuples (x, y) for each initial zone.
            zone_tree: The hierarchical tree structure of the zones.
            weights: A list of weight values for each initial zone.
        """
        self._matrix = [dict() for _ in range(len(centroids))]
        self._centroids = centroids
        self._zone_tree = zone_tree
        self._weights = weights

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

        if j in self._matrix[i]:
            return self._matrix[i][j]

        # assuming that the index of leafs is always lower than non-leafs
        children = self._zone_tree.get_children(j)
        if children:
            dij = sum([self._weights[c] * self.get(i,c) for c in children]) / self._weights[j]
        else:
            dx = self._centroids[i][0]-self._centroids[j][0]
            dy = self._centroids[i][1]-self._centroids[j][1]
            dij = sqrt(dx**2+dy**2)

        self._matrix[i][j] = dij
        return dij

    def add_zone(self):
        """
        Adds a new empty dictionary to the `matrix` when a new merged zone is created,
        to hold distances from this new zone to others.
        """
        self._matrix.append(dict())
