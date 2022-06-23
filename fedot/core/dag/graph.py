from abc import ABC, abstractmethod
from typing import Dict, Sequence, Union, TypeVar, List

from fedot.core.visualisation.graph_viz import GraphVisualiser

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

    @abstractmethod
    def __eq__(self, other) -> bool:
        # return self.operator.is_graph_equal(other)
        raise NotImplementedError()

    @property
    @abstractmethod
    def root_node(self) -> Union[GraphNode, Sequence[GraphNode]]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def nodes(self) -> List['GraphNode']:
        raise NotImplementedError()

    @nodes.setter
    @abstractmethod
    def nodes(self, new_nodes: List['GraphNode']):
        raise NotImplementedError()

    @property
    @abstractmethod
    def depth(self) -> int:
        raise NotImplementedError()

    @property
    def length(self) -> int:
        return len(self.nodes)

    def show(self, path: str = None):
        GraphVisualiser().visualise(self, path)

    @property
    def graph_description(self) -> Dict:
        return {
            'depth': self.depth,
            'length': self.length,
            'nodes': self.nodes,
        }

    @property
    def descriptive_id(self) -> str:
        return self.root_node.descriptive_id

    def __str__(self):
        return str(self.graph_description)

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return self.length
