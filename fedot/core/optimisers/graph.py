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
