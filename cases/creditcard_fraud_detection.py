import pandas as pd
import numpy as np
from sklearn.utils import shuffle
from imblearn.under_sampling import RandomUnderSampler

import random
import datetime
from datetime import timedelta


from core.composer.gp_composer.gp_composer import \
    GPComposer, GPComposerRequirements
from core.composer.visualisation import ComposerVisualiser
from core.repository.model_types_repository import ModelTypesRepository
from core.repository.quality_metrics_repository import \
    ClassificationMetricsEnum, MetricsRepository
from core.repository.tasks import Task, TaskTypesEnum

from examples.utils import create_multi_clf_examples_from_excel

from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score, roc_auc_score
from core.composer.chain import Chain
from core.models.data import InputData

random.seed(1)
np.random.seed(1)

#Kaggle competition: https://www.kaggle.com/mlg-ulb/creditcardfraud

def get_model(train_file_path: str, cur_lead_time: datetime.timedelta = timedelta(minutes=180), depth: int=5, width: int=4, population: int=35, num_gen: int=320):
    """
    train_file_path: train file path.
    cur_lead_time: max time to search best model.
    num_gen: how much steps of generations will be(check cur_lead_time). 
    
    Attention! The following params use a lot of RAM. Use small values, depending on the amount of your RAM.
    depth: max depth of searching model.
    width: max width of searching model.
    population: number of population/
    """
    task = Task(task_type=TaskTypesEnum.classification)
    dataset_to_compose = InputData.from_csv(train_file_path, task=task)

    # the search of the models provided by the framework
    # that can be used as nodes in a chain for the selected task
    models_repo = ModelTypesRepository()
    available_model_types, _ = models_repo.suitable_model(task_type=task.task_type)

    metric_function = MetricsRepository(). \
        metric_by_id(ClassificationMetricsEnum.ROCAUC_penalty)

    composer_requirements = GPComposerRequirements(
        primary=available_model_types, secondary=available_model_types,
        max_lead_time=cur_lead_time, max_arity=width,
        max_depth=depth, pop_size=population, num_of_generations=num_gen, 
        crossover_prob = 0.8, mutation_prob = 0.8, 
        add_single_model_chains = True)

    # Create the genetic programming-based composer, that allow to find
    # the optimal structure of the composite model
    composer = GPComposer()

    # run the search of best suitable model
    chain_evo_composed = composer.compose_chain(data=dataset_to_compose,
                                                initial_chain=None,
                                                composer_requirements=composer_requirements,
                                                metrics=metric_function, is_visualise=False)
    
    chain_evo_composed.fit(input_data=dataset_to_compose)

    return chain_evo_composed


def apply_model_to_data(model: Chain, data_path: str):
    """
    Applying model to data and check metrics.
    """
    dataset_to_validate = InputData.from_csv(data_path)
    
    predicted_labels = model.predict(dataset_to_validate).predict

    
    roc_auc_st = round(roc_auc_score(y_true=dataset_to_validate.target,y_score=predicted_labels.round()), 4)
                              
    p = round(precision_score(y_true=dataset_to_validate.target,y_pred=predicted_labels.round()), 4)
    r = round(recall_score(y_true=dataset_to_validate.target,y_pred=predicted_labels.round()), 4)
    a = round(accuracy_score(y_true=dataset_to_validate.target,y_pred=predicted_labels.round()),4 )
    f = round(f1_score(y_true=dataset_to_validate.target,y_pred=predicted_labels.round()), 4)
    
    return roc_auc_st, p, r, a, f


def balance_class(file_path):
    """
    Function to balace our dataset to minority class.
    """
    df = pd.read_csv(file_path)
    
    X = df.drop(columns=['Class'])
    y = df.iloc[:,[-1]]

    rus = RandomUnderSampler(sampling_strategy = 'all', random_state=42)
    
    X_res, y_res = rus.fit_resample(X, y)
    X_res['Class'] = y_res
    
    df_balanced = shuffle(X_res, random_state = 42).reset_index().drop(columns='index')
    
    df_balanced.to_csv(r'./creditcard_overSample.csv', index=False)
    
    return r'./creditcard_overSample.csv'

if __name__ == "__main__":
    file_path = r'./creditcard.csv'
    
    file_path_first = balance_class(file_path)
    
    train_file_path, test_file_path = create_multi_clf_examples_from_excel(file_path_first)
    
    fitted_model = get_model(train_file_path)
    
    ComposerVisualiser.visualise(fitted_model, save_path = f'./model.png')
    
    roc_auc, p, r, a, f = apply_model_to_data(fitted_model, test_file_path)
    print(f'TEST/TRAIN SCORE \nROC AUC metric is {roc_auc} \nPRECISION is {p} \nRECALL is {r} \nACCURACY is {a} \nF1_score is {f}')
    
    print('\n')
    roc_auc, p, r, a, f = apply_model_to_data(fitted_model, file_path)
    print(f'Applying model to all data \nROC AUC metric is {roc_auc} \nPRECISION is {p} \nRECALL is {r} \nACCURACY is {a} \nF1_score is {f}')