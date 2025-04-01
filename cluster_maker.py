from heapq import heappush, heappop
from math import exp,log
from typing import List, Optional, Set, Tuple

from tree import Tree
from tree_data import TreeData
from lazy_distance import LazyDistance
from adjacency_matrix import adjacency_matrix


# take log of criterion to avoid overflow, order will remain the same, and criterios cannot be <=0 by definition, xc > xa,xb, wc = wa+wb :

# criterion = wc * exp(xc) - wa * exp(xa) - wb * exp(xb)

# using: (1) w * exp(x) = exp(x+log(w))

#        (2) exp(a) + exp(b) = exp(c)(exp(a-c) + exp(b-c))

#        (3) log(a * b) = log(a) + log(b)

# Hence:

# log_criterion = xm + log(exp(xc+log(wc) - xm) - log(exp(xa+log(wa) - xm)- log(exp(xb+log(wb) - xm))

# where xm can be any contant, we use x_max = max(xc+log(wc), xa +log(wa), xb+log(wb))

# could have considered the min or the average, this seems good as you cannot get overflow, and "underflow" just rounds to 0
class cluster_maker:
    """
    Performs hierarchical clustering of zones based on a defined criterion.

    Initially, it identifies adjacent zones and adds them as merge candidates to a priority queue.
    The zone pairs with the highest priority (lowest log-criterion) are merged iteratively.
    The merging process continues until the priority queue is empty, resulting in a hierarchical
    tree structure of the zones.

    Attributes:
        data (tree_data): The data associated with the zones.
        beta (float): A parameter influencing the merging criterion.
        queue (List[Tuple[float, Set[int]]]): A priority queue storing merge candidates
                                                (sets of adjacent zone indices) and their priorities.
        adjacency (adjacency_matrix): The adjacency matrix of the zones.
        zone_tree (tree): The hierarchical tree structure being built.
        distance_matrix (lazy_distance): The lazy distance matrix for calculating distances
                                         between zones.
    """
    def __init__(self, data: TreeData, beta: float):
        """
        Initializes the cluster maker.

        Args:
            data: The data associated with the zones.
            beta: A parameter influencing the merging criterion.
        """
        self.data = data
        self.beta = beta
        self.queue = []
        self.adjacency = adjacency_matrix(data.centroids)
        self.zone_tree = Tree(len(data.origins))
        self.distance_matrix = LazyDistance(data.centroids, self.zone_tree, data.weights)
    
    # Note, this code is generalised to work with any number of zones in a merge candidate, however there are always exactly two. 
    def priority(self, candidate: Set[int]) -> float:
        """
        Calculates the priority (log-criterion) for merging a given set of zones.

        The priority is based on the change in a criterion function that considers the
        internal distances and weights of the zones being merged. A lower priority value
        (more negative log-criterion) indicates a more favorable merge. The log of the
        criterion is used to avoid potential overflow and underflow issues.

        The criterion being (implicitly) maximized is:
        `w_combi * exp(beta * dii_combi) - sum([w[c] * exp(beta * d.get(c, c)) for c in candidate])`
        where:
        - `w_combi` is the combined weight of the candidate zones.
        - `dii_combi` is the internal distance of the merged zone.
        - `w[c]` and `d.get(c, c)` are the weight and internal distance of individual candidate zones.

        The logarithmic transformation is applied for numerical stability.

        Args:
            candidate: A set of indices of the zones to be considered for merging.

        Returns:
            float: The log of the criterion for merging the candidate zones.
        """
        # for shorthand
        d = self.distance_matrix
        w = self.data.weights

        # combined weights of merge candidate zones
        w_combi = sum([w[c] for c in candidate])

        # internal distance of merge candidate zones when merged
        dii_combi = sum([d.get(a, b) * w[a] * w[b] for a in candidate for b in candidate]) / w_combi**2

        # log(weight * exp(beta * internal_distance) for all merge candidate zones
        x_dash = [self.beta * d.get(c, c) + log(w[c]) for c in candidate]

        # log(weight * exp(beta * internal_distance) for merge candidate zones when merged
        x_dash_combi = self.beta * dii_combi + log(w_combi)

        x_max = max(max(x_dash), x_dash_combi)
        log_criterion = x_max + log(exp(x_dash_combi - x_max) - sum([exp(x_dash_i - x_max) for x_dash_i in x_dash]))

        return log_criterion

    def add_candidate_to_queue(self, candidate: Set[int]):
        """
        Adds a merge candidate (a set of zone indices) and its priority to the priority queue.

        Args:
            candidate: A set of indices of the zones to be considered for merging.
        """
        elem = (self.priority(candidate), candidate)
        heappush(self.queue, elem)

    def merge_zones(self, children: Set[int]):
        """
        Merges a set of child zones into a new parent zone and updates the tree structure,
        data, distance matrix, and adjacency matrix. It also adds new merge candidates
        involving the newly created parent zone to the priority queue.

        Args:
            children: A set of the indices of the child zones to be merged.
        """
        new_parent = self.zone_tree.append_parent(children)
        self.data.append_parent(children)
        self.distance_matrix.add_zone()
        combined_adjacency = self.adjacency.merge(children)
        for adjacent in combined_adjacency:
            self.add_candidate_to_queue({adjacent, new_parent})

    def create(self) -> Tree:
        """
        Creates the hierarchical clustering of zones by iteratively merging the most
        favorable adjacent zones until no more merges are possible (priority queue is empty).

        Returns:
            tree: The resulting hierarchical tree structure representing the clustering.
        """
        # First create candidates for all adjacent zones
        for i, nbh_i in enumerate(self.adjacency.get_all()):
            for j in nbh_i:
                if i < j:
                    self.add_candidate_to_queue({i, j})

        # Continue to merge zones; merged zones are added to the queue
        while self.queue:
            priority, children = heappop(self.queue)
            # Check if any of the children have already been merged into a parent
            if not any(self.zone_tree.has_parent(c) for c in children):
                self.merge_zones(children)

        return self.zone_tree

    def get_distance_matrix(self) -> LazyDistance:
        """
        Returns the lazy distance matrix used by the cluster maker.

        Returns:
            lazy_distance: The lazy distance matrix object.
        """
        return self.distance_matrix
