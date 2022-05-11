from fedot.core.optimisers.generation_keeper import ImprovementWatcher
from fedot.core.optimisers.gp_comp.operators.operator import PopulationT
from fedot.core.optimisers.gp_comp.parameters.parameter import AdaptiveParameter


class GraphDepth(AdaptiveParameter[int]):

    def __init__(self, improvements: ImprovementWatcher,
                 start_depth: int = 1, max_depth: int = 10, max_stagnated_generations: int = 1,
                 adaptive: bool = True):
        self._improvements = improvements
        self._start_depth = start_depth
        self._max_depth = max_depth
        self._current_depth = start_depth
        self._max_stagnated_gens = max_stagnated_generations
        self._adaptive = adaptive

    @property
    def initial(self) -> int:
        return self._start_depth

    def next(self, population: PopulationT = None) -> int:
        if not self._adaptive:
            return self._max_depth
        if self._current_depth >= self._max_depth:
            return self._current_depth
        if self._improvements.stagnation_duration >= self._max_stagnated_gens:
            self._current_depth += 1
        return self._current_depth