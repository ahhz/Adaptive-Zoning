from typing import List, Optional, Set, Tuple
class tree:
    """
    Represents a hierarchical tree structure for zones, defining parent-child relationships.
    The tree structure is simple, but sufficient to support the Adaptive Zoning computations.
    
    The initial `num_leafs` indices represent the leaf nodes. As zones are merged, new parent
    nodes are created with indices greater than the leaf nodes. The last merged zone becomes
    the root of the tree. Parent zones always have a higher index than their children.

    Attributes:
        root (int): The index of the root node (the last merged zone).
        num_leafs (int): The initial number of leaf nodes.
        parent (List[Optional[int]]): A list where `parent[i]` stores the index of the parent
                                       zone of zone `i`, or None if it's the root.
        children (List[Optional[Set[int]]]): A list where `children[i]` stores a set
                                                of the indices of the child zones of zone `i`,
                                                or None if it's a leaf node.
    """
    def __init__(self, num_leafs: int = 0):
        """
        Initializes a tree structure with a given number of leaf nodes.

        Args:
            num_leafs: The initial number of leaf nodes in the tree. Defaults to 0.
        """
        self.root = num_leafs
        self.num_leafs = num_leafs
        self.parent = [None for _ in range(num_leafs)]
        self.children = [None for _ in range(num_leafs)]

    def get_root(self) -> int:
        """
        Returns the index of the root node of the tree.

        Returns:
            int: The index of the root node.
        """
        return self.root

    def has_parent(self, index: int) -> bool:
        """
        Checks if a given zone index has a parent.

        Args:
            index: The index of the zone to check.

        Returns:
            bool: True if the zone has a parent, False otherwise.
        """
        return self.parent[index] is not None

    def get_parent(self, index: int) -> Optional[int]:
        """
        Returns the index of the parent zone for a given zone index.

        Args:
            index: The index of the zone.

        Returns:
            Optional[int]: The index of the parent zone, or None if the zone has no parent (is the root).
        """
        return self.parent[index]

    def has_children(self, index: int) -> bool:
        """
        Checks if a given zone index has children.

        Args:
            index: The index of the zone to check.

        Returns:
            bool: True if the zone has children, False otherwise.
        """
        return self.children[index] is not None

    def get_children(self, index: int) -> Optional[Set[int]]:
        """
        Returns the children of a given zone index.

        Args:
            index: The index of the zone.

        Returns:
            Optional[Set[int]]: A set of the indices of the child zones, or None if the zone has no children.
        """
        return self.children[index]

    def get_num_leafs(self) -> int:
        """
        Returns the initial number of leaf nodes in the tree.

        Returns:
            int: The initial number of leaf nodes.
        """
        return self.num_leafs

    def append_parent(self, children: Set[int]) -> int:
        """
        Appends a new parent node to the tree, representing the merging of the given child zones.

        The new parent node becomes the new root of the subtree formed by the merged children.
        The `parent` attribute of each child is updated to point to the new parent.

        Args:
            children: A set of the indices of the child zones being merged.

        Returns:
            int: The index of the newly created parent zone (which is the new root of the merged subtree).
        """
        self.root = len(self.children)
        self.children.append(children)
        self.parent.append(None)
        for c in children:
            self.parent[c] = self.root
        return self.root

    def get_size(self) -> int:
        """
        Returns the total number of nodes (leafs and merged zones) currently in the tree.

        Returns:
            int: The total number of nodes in the tree.
        """
        return len(self.parent)
