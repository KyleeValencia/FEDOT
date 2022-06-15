from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, Sequence, Union, TypeVar, Generic

from fedot.core.visualisation.graph_viz import GraphVisualiser

if TYPE_CHECKING:
    from fedot.core.dag.graph_node import GraphNode


NodeType = TypeVar('NodeType', bound=GraphNode, covariant=False, contravariant=False)


class Graph(ABC):
    """
    Defines abstract graph interface that's required by graph optimisation process.
    """

    @abstractmethod
    def add_node(self, new_node: 'GraphNode'):
        """
        Add new node to the Pipeline

        :param new_node: new GraphNode object
        """
        raise NotImplementedError()

    @abstractmethod
    def update_node(self, old_node: 'GraphNode', new_node: 'GraphNode'):
        """
        Replace old_node with new one.

        :param old_node: 'GraphNode' object to replace
        :param new_node: 'GraphNode' new object
        """
        raise NotImplementedError()

    @abstractmethod
    def update_subtree(self, old_subroot: 'GraphNode', new_subroot: 'GraphNode'):
        """
        Replace the subtrees with old and new nodes as subroots

        :param old_subroot: 'GraphNode' object to replace
        :param new_subroot: 'GraphNode' new object
        """
        raise NotImplementedError()

    @abstractmethod
    def delete_node(self, node: 'GraphNode'):
        """
        Delete chosen node redirecting all its parents to the child.

        :param node: 'GraphNode' object to delete
        """
        raise NotImplementedError()

    @abstractmethod
    def delete_subtree(self, subroot: 'GraphNode'):
        """
        Delete the subtree with node as subroot.

        :param subroot:
        """
        raise NotImplementedError()

    def __eq__(self, other) -> bool:
        # return self.operator.is_graph_equal(other)
        raise NotImplementedError()

    def __str__(self):
        return str(self.graph_description)

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return self.length

    @property
    def root_node(self) -> Union[GraphNode, Sequence[GraphNode]]:
        raise NotImplementedError()

    @property
    def nodes(self) -> Sequence['GraphNode']:
        raise NotImplementedError()

    @property
    def length(self) -> int:
        return len(self.nodes)

    @property
    def depth(self) -> int:
        raise NotImplementedError()

    def show(self, path: str = None):
        GraphVisualiser().visualise(self, path)

    @property
    def graph_description(self) -> Dict:
        return {
            'depth': self.depth,
            'length': self.length,
            'nodes': self.nodes,
        }


class GraphDelegate(Graph):
    """
    Graph that delegates calls to another Graph implementation.

    The class purpose is for cleaner code organisation:
    - avoid inheriting from specific Graph implementations
    - hide Graph implementation details from inheritors.

    :param delegate: Graph implementation to delegate to.
    """

    def __init__(self, delegate: Graph):
        self.operator = delegate

    def add_node(self, new_node: 'GraphNode'):
        self.operator.add_node(new_node)

    def update_node(self, old_node: 'GraphNode', new_node: 'GraphNode'):
        self.operator.update_node(old_node, new_node)

    def update_subtree(self, old_subroot: 'GraphNode', new_subroot: 'GraphNode'):
        self.operator.update_subtree(old_subroot, new_subroot)

    def delete_node(self, node: 'GraphNode'):
        self.operator.delete_node(node)

    def delete_subtree(self, subroot: 'GraphNode'):
        self.operator.delete_subtree(subroot)

    def __eq__(self, other) -> bool:
        return self.operator.__eq__(other)

    def __str__(self):
        return self.operator.__str__()

    def __repr__(self):
        return self.operator.__repr__()

    @property
    def root_node(self) -> Union['GraphNode', Sequence['GraphNode']]:
        return self.operator.root_node

    @property
    def nodes(self) -> Sequence['GraphNode']:
        return self.operator.nodes

    @property
    def length(self) -> int:
        return self.operator.length

    @property
    def depth(self) -> int:
        return self.operator.depth
