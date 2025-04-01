from typing import List, Optional, Set, Tuple
from collections import deque

class Tree:
    """
    Represents a hierarchical tree structure for zones, defining parent-child relationships.
    The tree structure is simple, but sufficient to support the Adaptive Zone System computations.
    
    The initial `num_leafs` indices represent the leaf nodes. As zones are merged, new parent
    nodes are created with indices greater than the leaf nodes. The last merged zone becomes
    the root of the tree. Parent zones always have a higher index than their children.

    """
    def __init__(self, num_leafs: int = 0):
        """
        Initializes a tree structure with a given number of leaf nodes.

        Args:
            num_leafs: The initial number of leaf nodes in the tree. Defaults to 0.
        """
        self._num_leafs = num_leafs
        self._parent = [None for _ in range(num_leafs)]
        self._children = [None for _ in range(num_leafs)]

    def get_last_added(self) -> int:
        """
        Returns the index of the last added node of the tree.

        Returns:
            int: The index of the last added node.
        """
        return len(self._parent)-1

    def has_parent(self, index: int) -> bool:
        """
        Checks if a given zone index has a parent.

        Args:
            index: The index of the zone to check.

        Returns:
            bool: True if the zone has a parent, False otherwise.
        """
        return self._parent[index] is not None

    def get_parent(self, index: int) -> Optional[int]:
        """
        Returns the index of the parent zone for a given zone index.

        Args:
            index: The index of the zone.

        Returns:
            Optional[int]: The index of the parent zone, or None if the zone has no parent (is the root).
        """
        return self._parent[index]

    def has_children(self, index: int) -> bool:
        """
        Checks if a given zone index has children.

        Args:
            index: The index of the zone to check.

        Returns:
            bool: True if the zone has children, False otherwise.
        """
        return self._children[index] is not None

    def get_children(self, index: int) -> Optional[Set[int]]:
        """
        Returns the children of a given zone index.

        Args:
            index: The index of the zone.

        Returns:
            Optional[Set[int]]: A set of the indices of the child zones, or None if the zone has no children.
        """
        return self._children[index]

    def get_num_leafs(self) -> int:
        """
        Returns the initial number of leaf nodes in the tree.

        Returns:
            int: The initial number of leaf nodes.
        """
        return self._num_leafs

    def append_parent(self, children: Set[int]) -> int:
        """
        Appends a new parent node to the tree, representing the merging of the given child zones.

        The `parent` attribute of each child is updated to point to the new parent.

        Args:
            children: A set of the indices of the child zones being merged.

        Returns:
            int: The index of the newly created parent zone 
        """
        index_of_last_added = len(self._parent)
        self._children.append(children)
        self._parent.append(None)
        for c in children:
            self._parent[c] = index_of_last_added
        return index_of_last_added

    def get_size(self) -> int:
        """
        Returns the total number of nodes (leafs and merged zones) currently in the tree.

        Returns:
            int: The total number of nodes in the tree.
        """
        return len(self._parent)
     
    def get_leafs(self,node) -> List[int]:
        """
        Returns the list of leaf indices belonging to a given node in the tree
        
        Returns:
            List[int]: The list of nodes that are the leafs under the given node
        """
        queue = deque([node])
        leafs = []
        while queue:
            next_node = queue.popleft() 
            if next_node < self._num_leafs:
                leafs.append(next_node)
            else:
                queue.extend(self._children[next_node])
        return leafs

    def map_leafs_to_n_groups(self, n : int, renumber : bool = False)->List[int]:
        """
        Returns a list the for each leaf node specifies which group it belongs for a given number of groups. 
        
         Args:
            n: The number of groups
            renumber: if this is set to True the groups are renumbered consecutively from zero, 
            otherwise the index of the group node is returned. 
           
        Returns: 
            List[int]: List of size num_leafs with the associate group index for each leaf in order
        """
        max_index = 2 * self._num_leafs - n 
        group_indices = [i for i in range(max_index) if self._parent[i] >= max_index]
        out = [0 for _ in range(self._num_leafs)]
        for index, group in enumerate(group_indices):
            leafs = self.get_leafs(group)
            for leaf in leafs:
                out[leaf] = index if renumber else group
        return out
        