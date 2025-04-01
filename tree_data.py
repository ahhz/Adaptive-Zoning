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

class TreeData:
    """
    Stores and manages the data associated with each zone in the hierarchical tree.

    For leaf nodes, the initial data (origins, destinations, weights, points) is provided.
    A copy of the data is made, and subsequently extended for the aggregated zones.
    When zones are merged, the data for the new parent zone is aggregated from its children.

    Attributes:
        origins (List[float]): A list where `origins[i]` stores the origin value for zone `i`.
        destinations (List[float]): A list where `destinations[i]` stores the destination value for zone `i`.
        weights (List[float]): A list where `weights[i]` stores the weight value for zone `i`.
        centroids (List[Tuple[float, float]]): A list where `points[i]` stores the coordinates (x, y)
                                             of the centroid of zone `i`.
    """
    def __init__(self, origins: List[float], destinations: List[float], weights: List[float], centroids: List[Tuple[float,float]]):
        """
        Initializes the tree data with the data for the initial leaf nodes.

        Args:
            origins: A list of origin values for each initial zone.
            destinations: A list of destination values for each initial zone.
            weights: A list of weight values for each initial zone.
            centroids: A list of coordinate tuples (x, y) for each initial zone.

        Raises:
            Exception: If the input data sources are not distinct (the same list is passed
                       for multiple arguments).
            Exception: If the input data lists do not have the same length.
        """
        n = len(origins)
        if (len(destinations) != n) or (len(weights) != n) or (len(centroids) != n):
            raise Exception("Adaptive zoning data must be have same length")

        self.origins = origins.copy()
        self.destinations = destinations.copy()
        self.weights = weights.copy()
        self.centroids = centroids.copy()

    def append_parent(self, children: Set[int]):
        """
        Appends the aggregated data for a new parent zone formed by merging the given child zones.

        The origin, destination, and weight of the parent zone are the sums of the corresponding
        values of its children. The centroid of the parent zone is calculated as the weighted
        average of the centroids of its children, using their weights.

        Args:
            children: A set of the indices of the child zones being merged.
        """
        self.origins.append(sum([self.origins[c] for c in children]))
        self.destinations.append(sum([self.destinations[c] for c in children]))
        self.weights.append(sum([self.weights[c] for c in children]))
        total_weight = self.weights[-1]
        assert(total_weight > 0)
        x = sum([ self.centroids[c][0] * self.weights[c] for c in children ]) / total_weight
        y = sum([ self.centroids[c][1] * self.weights[c] for c in children ]) / total_weight
        self.centroids.append((x,y))
