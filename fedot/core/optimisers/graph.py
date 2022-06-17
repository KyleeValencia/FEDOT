from copy import deepcopy
from typing import Any, List, Optional, Union

from fedot.core.dag.graph_delegate import GraphDelegate
from fedot.core.dag.graph_node import GraphNode
from fedot.core.dag.graph_operator import GraphOperator
from fedot.core.log import Log, default_log


OptNode = GraphNode


class OptGraph(GraphDelegate):
    """
    Base class used for optimized structure

    :param nodes: OptNode object(s)
    :param log: Log object to record messages
    """

    def __init__(self, nodes: Union[OptNode, List[OptNode]] = (),
                 log: Optional[Log] = None):
        self.log = log or default_log(__name__)
        super().__init__(GraphOperator(nodes))

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo=None):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result
