from typing import Any, Optional, Union, Iterable, Callable, Sequence

from fedot.core.dag.graph import Graph
from fedot.core.log import Log, default_log
from fedot.core.optimisers.fitness import *
from fedot.core.repository.quality_metrics_repository import MetricType, MetricsRepository

ObjectiveFunction = Callable[[Graph], Fitness]


class Objective:
    """Represents objective function for computing metric values
    on Graphs and keeps information about metrics used."""

    def __init__(self, metrics: Union[MetricType, Iterable[MetricType]],
                 is_multi_objective: bool = False,
                 log: Optional[Log] = None):
        self.metrics = tuple(metrics) if isinstance(metrics, Iterable) else (metrics,)
        self.is_multi_objective = is_multi_objective
        self._log = log or default_log(str(self.__class__))

    def __call__(self, graph: Graph, **kwargs: Any) -> Fitness:
        evaluated_metrics = []
        for metric in self.metrics:
            metric_func = MetricsRepository().metric_by_id(metric, default_callable=metric)
            try:
                metric_value = metric_func(graph, **kwargs)
                evaluated_metrics.append(metric_value)
            except Exception as ex:
                self._log.error(f'Objective evaluation error for graph {graph} on metric {metric}: {ex}')
                return null_fitness()  # fail right away
        return to_fitness(evaluated_metrics, self.is_multi_objective)

    @property
    def metric_names(self) -> Sequence[str]:
        return [str(metric) for metric in self.metrics]


def to_fitness(metric_values: Optional[Sequence[float]], multi_objective: bool = False) -> Fitness:
    if metric_values is None:
        return null_fitness()
    elif multi_objective:
        return MultiObjFitness(values=metric_values,
                               weights=[-1] * len(metric_values))
    else:
        return SingleObjFitness(*metric_values)