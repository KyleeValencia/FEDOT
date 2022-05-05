from abc import abstractmethod
from collections.abc import Sequence
from typing import Any, Optional, Union, Iterable, Callable

from fedot.core.dag.graph import Graph
from fedot.core.optimisers.fitness import *
from fedot.core.repository.quality_metrics_repository import MetricType, MetricsRepository

ObjectiveFunction = Callable[[Graph], Fitness]


class Objective:
    """Represents objective function for computing metric values
    on Graphs and keeps information about metrics used."""

    def __init__(self, metrics: Union[MetricType, Iterable[MetricType]], is_multi_objective: bool = False):
        self._metrics = tuple(metrics) if isinstance(metrics, Iterable) else (metrics,)
        self._is_multi_objective = is_multi_objective

    @property
    def metrics(self) -> Sequence[MetricType]:
        return self._metrics

    @property
    def is_multi_objective(self) -> bool:
        return self._is_multi_objective

    @abstractmethod
    def __call__(self, graph: Graph, **kwargs: Any) -> Fitness:
        evaluated_metrics = []
        for metric in self._metrics:
            metric_func = MetricsRepository().metric_by_id(metric, default_callable=metric)
            metric_value = metric_func(graph, **kwargs)
            evaluated_metrics.append(metric_value)
        return to_fitness(evaluated_metrics, self._is_multi_objective)

    @property
    def metric_names(self) -> Sequence[str]:
        return [str(metric) for metric in self._metrics]


def to_fitness(metric_values: Optional[Sequence[float]], multi_objective: bool = False) -> Fitness:
    if metric_values is None:
        return null_fitness()
    elif multi_objective:
        return MultiObjFitness(values=metric_values,
                               weights=[-1] * len(metric_values))
    else:
        return SingleObjFitness(*metric_values)
