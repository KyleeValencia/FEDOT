from core.composer.node import Node
from core.models.data import Data


class Chain:
    def __init__(self):
        self.nodes = []

    def evaluate(self) -> Data:
        raise NotImplementedError()

    def add_node(self, new_node: Node):
        # Append new node to chain
        self.nodes.append(new_node)

    def update_node(self, new_node: Node):
        raise NotImplementedError()





