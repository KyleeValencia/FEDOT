from abc import ABC, abstractmethod
from enum import Enum
from typing import (
    List,
    Callable,
    Optional
)

import numpy as np

from core.composer.chain import Chain
from core.composer.node import NodeGenerator
from core.models.data import Data
from core.models.model import Model


# TODO: specify ComposerRequirements class
class ComposerRequirements:
    def __init__(self, primary_requirements, secondary_requirements, max_depth, max_models_num):
        self.primary_requirements= primary_requirements
        self.secondary_requirements =secondary_requirements
        self.max_depth= max_depth
        self.max_models_num=max_models_num

class Composer(ABC):
    @abstractmethod
    def compose_chain(self, initial_chain: Optional[Chain],
                      primary_requirements: List[Model],
                      secondary_requirements: List[Model],
                      metrics: Callable) -> Chain:
        raise NotImplementedError()


class DummyChainTypeEnum(Enum):
    flat = 1,
    hierarchical = 2


class DummyComposer(Composer):
    def __init__(self, dummy_chain_type):
        self.dummy_chain_type = dummy_chain_type

    def compose_chain(self, initial_chain: Optional[Chain],
                      primary_requirements: List[Model],
                      secondary_requirements: List[Model],
                      metrics: Optional[Callable]) -> Chain:
        new_chain = Chain()
        empty_data = Data(np.zeros(1), np.zeros(1), np.zeros(1))

        if self.dummy_chain_type == DummyChainTypeEnum.hierarchical:
            # (y1, y2) -> y
            last_node = NodeGenerator.get_secondary_node(secondary_requirements[0])
            last_node.nodes_from = []

            for requirement_model in primary_requirements:
                new_node = NodeGenerator.get_primary_node(requirement_model, empty_data)
                new_chain.add_node(new_node)
                last_node.nodes_from.append(new_node)
            new_chain.add_node(last_node)
        elif self.dummy_chain_type == DummyChainTypeEnum.flat:
            # (y1) -> (y2) -> y
            first_node = NodeGenerator.get_primary_node(primary_requirements[0], empty_data)
            new_chain.add_node(first_node)
            prev_node = first_node
            for requirement_model in secondary_requirements:
                new_node = NodeGenerator.get_secondary_node(requirement_model)
                new_node.nodes_from = [prev_node]
                prev_node = new_node
                new_chain.add_node(new_node)
        else:
            raise NotImplemented
        return new_chain
