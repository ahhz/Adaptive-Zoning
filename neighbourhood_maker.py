from heapq import heappush, heappop
from math import exp,log
from typing import List, Optional, Set, Tuple

from lazy_distance import lazy_distance
from tree import Tree
from tree_data import tree_data

# criterion = Oi * Dj* (exp(beta *(dii + djj - dij)-exp(-beta *(dii + djj + dij))
# log criterion = log(Oi) + log(Dj) + beta(dii+djj-dij) +log(1-exp(-2 beta(dii+djj))
# negate the criterion: - (log(Oi) + log(Dj) + beta(dii+djj-dij) +log(1-exp(-2 beta(dii+djj)))
# because the heap sorts from small to large.

class neighbourhood_maker:
    """
    Creates a set of neighborhoods for each leaf node in the zone tree.

    Each neighborhood aims to include a mix of aggregated and leaf nodes that are
    considered relevant to the corresponding leaf node based on a priority function.
    The neighborhood is built by starting with the root of the tree and iteratively
    expanding it by considering child nodes based on the priority. The size of the
    neighborhood (in terms of the number of nodes, not necessarily just leaves) is
    influenced by `nbh_size`.

    Attributes:
        distance_matrix (lazy_distance): The lazy distance matrix for calculating distances between zones.
        zone_tree (tree): The hierarchical tree structure of the zones.
        data (tree_data): The data associated with the zones (origins, destinations, etc.).
        beta (float): A parameter influencing the priority function.
        nbh_size (int): The desired size (number of nodes) for each neighborhood.
    """
    def __init__(self, data: tree_data, beta: float, nbh_size: int, zone_tree: Tree, distance_matrix: lazy_distance):
        """
        Initializes the neighbourhood maker.

        Args:
            data: The data associated with the zones.
            beta: A parameter influencing the priority function.
            nbh_size: The desired size (number of nodes) for each neighborhood.
            zone_tree: The hierarchical tree structure of the zones.
            distance_matrix: The lazy distance matrix for calculating distances between zones.
        """
        self.distance_matrix = distance_matrix
        self.zone_tree = zone_tree
        self.data = data
        self.beta = beta
        self.nbh_size = nbh_size

    def priority(self, i: int, j: int) -> float:
        """
        Calculates the priority for including zone `j` (or its descendants) in the neighborhood of leaf node `i`.

        The priority is based on a negated log-likelihood criterion that considers the origins
        of zone `i`, the destinations of zone `j`, and the internal and external distances
        between them, weighted by the `beta` parameter. The negation is used because the
        priority queue (min-heap) sorts from smallest to largest, and we want to prioritize
        zones with a higher (non-negated) criterion.

        Args:
            i: The index of the leaf node for which the neighborhood is being created.
            j: The index of a zone (could be a leaf or a merged zone) being considered for inclusion.

        Returns:
            float: The negated log-likelihood priority value. Lower values indicate higher priority.
        """
        dii = self.distance_matrix.get(i, i)
        djj = self.distance_matrix.get(j, j)
        dij = self.distance_matrix.get(i, j)

        return -(log(self.data.origins[i]) + log(self.data.destinations[j]) + self.beta * (dii + djj - dij) + log(1 - exp(-2 * self.beta * (dii + djj))))

    def create(self) -> List[Set[int]]:
        """
        Creates a list of neighborhoods, one for each leaf node in the zone tree.

        Each neighborhood is a set of zone indices (which can be a mix of leaf and
        aggregated nodes) that are considered relevant to the corresponding leaf node
        based on the priority function and the hierarchical tree structure. The
        neighborhood is expanded from the root of the tree until the desired `nbh_size`
        (number of nodes in the neighborhood) is reached.

        Returns:
            List[Set[int]]: A list where each element is a set of integer indices representing
                             the nodes in the neighborhood of the corresponding initial leaf node.
        """
        neighbourhoods = []
        for i in range(self.zone_tree.get_num_leafs()):
            q = []
            root = self.zone_tree.get_last_added()
            nbh_i = {root}
            heappush(q, (self.priority(i, root), root))
            while len(nbh_i) < self.nbh_size:
                if not q:
                    break
                j = heappop(q)[1]
                children = self.zone_tree.get_children(j)
                if children:
                    nbh_i = (nbh_i | children) - {j}
                    for c in children:
                        if self.zone_tree.has_children(c):
                            heappush(q, (self.priority(i, c), c))
            neighbourhoods.append(nbh_i)
        return neighbourhoods
