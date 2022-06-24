from typing import List, Optional, Union, Iterable
from uuid import uuid4

from fedot.core.utilities.data_structures import UniqueList
from fedot.core.utils import DEFAULT_PARAMS_STUB


MAX_DEPTH = 1000


class GraphNode:
    """
    Class for node definition in the DAG-based structure

    :param nodes_from: parent nodes which information comes from
    :param content: dict for the content in node
        The possible parameters are:
            'name' - name (str) or object that performs actions in this node
            'params' - dictionary with additional information that is used by
            the object in the 'name' field (e.g. hyperparameters values).
    """

    def __init__(self, content: Union[dict, str],
                 nodes_from: Optional[List['GraphNode']] = None):
        # Wrap string into dict if it is necessary
        if isinstance(content, str):
            content = {'name': content}

        self.content = content
        self._nodes_from = UniqueList(nodes_from or ())
        self.uid = str(uuid4())

    def __str__(self):
        return str(self.content['name'])

    def __repr__(self):
        return self.__str__()

    @property
    def nodes_from(self) -> List:
        return self._nodes_from

    @nodes_from.setter
    def nodes_from(self, nodes: Optional[Iterable['GraphNode']]):
        self._nodes_from = UniqueList(nodes)

    @property
    def descriptive_id(self):
        return _descriptive_id_recursive(self)

    # TODO: implement normal topological sort
    def ordered_subnodes_hierarchy(self, visited=None) -> List['GraphNode']:
        if visited is None:
            visited = []

        if len(visited) > MAX_DEPTH:
            raise ValueError('Graph has cycle')
        nodes = [self]
        for parent in self.nodes_from:
            if parent not in visited:
                visited.append(parent)
                nodes.extend(parent.ordered_subnodes_hierarchy(visited))

        return nodes

    @property
    def distance_to_primary_level(self):
        if not self.nodes_from:
            return 0
        else:
            return 1 + max([next_node.distance_to_primary_level for next_node in self.nodes_from])


def _descriptive_id_recursive(current_node, visited_nodes=None) -> str:
    """
    Method returns verbal description of the content in the node
    and its parameters
    """
    if visited_nodes is None:
        visited_nodes = []

    node_operation = current_node.content['name']
    params = current_node.content.get('params')
    if isinstance(node_operation, str):
        # If there is a string: name of operation (as in json repository)
        node_label = str(node_operation)
        if params and params != DEFAULT_PARAMS_STUB:
            node_label = f'n_{node_label}_{params}'
    else:
        # If instance of Operation is placed in 'name'
        node_label = node_operation.description(params)

    full_path_items = []
    if current_node in visited_nodes:
        return 'ID_CYCLED'
    visited_nodes.append(current_node)
    if current_node.nodes_from:
        previous_items = []
        for parent_node in current_node.nodes_from:
            previous_items.append(_descriptive_id_recursive(parent_node, visited_nodes))
        previous_items.sort()
        previous_items_str = ';'.join(previous_items)

        full_path_items.append(f'({previous_items_str})')
    full_path_items.append(f'/{node_label}')
    full_path = ''.join(full_path_items)
    return full_path
