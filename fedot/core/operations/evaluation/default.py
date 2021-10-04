import warnings
from typing import Optional
from typing import Callable
from fedot.core.data.data import InputData, OutputData
from fedot.core.operations.evaluation.evaluation_interfaces import EvaluationStrategy
from fedot.core.operations.evaluation.operation_implementations.models.default_model import DefaultModelImplementation

warnings.filterwarnings("ignore", category=UserWarning)


class CustomDefaultModelStrategy(EvaluationStrategy):
    """
    This class defines the default model container for custom of domain-specific implementations

    :param str operation_type: rudimentary of parent - type of the operation defined in operation or
           data operation repositories
    :param dict params: hyperparameters to fit the model with
    """

    def __init__(self, operation_type: Optional[str], params: dict = None, wrappers: dict = None):
        super().__init__(operation_type, params)

        self.wrappers = wrappers
        self.operation_impl = DefaultModelImplementation(self.wrappers, **params)

    def fit(self, train_data: InputData):
        """ This strategy does not support fitting the operation"""
        return self.operation_impl

    def predict(self, trained_operation, predict_data: InputData,
                is_fit_pipeline_stage: bool) -> OutputData:

        prediction = self.operation_impl.predict(predict_data, is_fit_pipeline_stage)
        # Convert prediction to output (if it is required)
        converted = self._convert_to_output(prediction, predict_data)
        return converted

    def _convert_to_operation(self, operation_type: str):
        raise NotImplementedError('For this strategy there is only one available operation')