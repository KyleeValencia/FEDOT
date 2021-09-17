import os
import time
from datetime import datetime
from typing import List

import numpy as np

from fedot.core.pipelines.pipeline import Pipeline
from fedot.core.pipelines.validation import validate
from remote.infrastructure.models_controller.computations import Client


class ComputationalSetup:
    remote_eval_params = {
        'mode': 'local',
        'dataset_name': '',  # name of the dataset for composer evaluation
        'task_type': '',  # name of the modelling task for dataset
        'train_data_idx': [],
        'max_parallel': 10
    }

    @property
    def is_remote(self):
        return ComputationalSetup.remote_eval_params['mode'] == 'remote'

    def fit(self, pipelines: List['Pipeline']) -> List['Pipeline']:
        pipelines_parts, data_id = _prepare_computation_vars(pipelines)

        final_pipelines = []
        for pipelines_part in pipelines_parts:
            remote_eval_params = ComputationalSetup.remote_eval_params

            dataset_name = remote_eval_params['dataset_name']
            task_type = remote_eval_params['task_type']
            data_idx = remote_eval_params['train_data_idx']

            client = _prepare_client()

            for pipeline in pipelines_part:
                try:
                    validate(pipeline)
                except ValueError:
                    pipeline.execution_id = None
                    continue

                pipeline_json, _ = pipeline.save()
                pipeline_json = pipeline_json.replace('\n', '')

                config = _get_config(pipeline_json, data_id, dataset_name, task_type, data_idx)

                client.create_execution(
                    container_input_path="/home/FEDOT/input_data_dir",
                    container_output_path="/home/FEDOT/output_data_dir",
                    container_config_path="/home/FEDOT/.config",
                    container_image="fedot:dm-5",
                    timeout=360,
                    config=config
                )

                pipeline.execution_id = client.get_executions()[-1]['id']

            statuses = ['']
            all_executions = client.get_executions()
            print(all_executions)
            start = datetime.now()
            while any(s not in ['Succeeded', 'Failed', 'Timeout', 'Interrupted'] for s in statuses):
                executions = client.get_executions()
                statuses = [execution['status'] for execution in executions]
                print([f"{execution['id']}={execution['status']};" for execution in executions])
                time.sleep(5)

            end = datetime.now()

            for p_id, pipeline in enumerate(pipelines_part):
                if pipeline.execution_id:
                    client.download_result(
                        execution_id=pipeline.execution_id,
                        path=f'./remote_fit_results',
                        unpack=True
                    )

                    try:
                        results_path_out = f'./remote_fit_results/execution-{pipeline.execution_id}/out'
                        results_folder = os.listdir(results_path_out)[0]
                        pipeline.load(os.path.join(results_path_out, results_folder, 'fitted_pipeline.json'))
                    except Exception as ex:
                        print(p_id, ex)
            final_pipelines.extend(pipelines_part)

            print('REMOTE EXECUTION TIME', end - start)

        return final_pipelines


def _prepare_computation_vars(pipelines):
    num_parts = np.floor(len(pipelines) / ComputationalSetup.remote_eval_params['max_parallel'])
    pipelines_parts = [x.tolist() for x in np.array_split(pipelines, num_parts)]
    data_id = int(os.environ['DATA_ID'])
    return pipelines_parts, data_id


def _prepare_client():
    pid = int(os.environ['PROJECT_ID'])

    client = Client(
        authorization_server=os.environ['AUTH_SERVER'],
        controller_server=os.environ['CONTR_SERVER']
    )

    client.login(login=os.environ['FEDOT_LOGIN'],
                 password=os.environ['FEDOT_PASSWORD'])

    client.create_execution_group(project_id=pid)
    response = client.get_execution_groups(project_id=pid)
    new_id = max([item['id'] for item in response]) + 1
    client.set_group_token(project_id=pid, group_id=new_id)
    return client


def _get_config(pipeline_json, data_id, dataset_name, task_type, dataset_idx):
    return f"""[DEFAULT]
        pipeline_description = {pipeline_json}
        train_data = input_data_dir/data/{data_id}/{dataset_name}.csv
        task = {task_type}
        output_path = output_data_dir/fitted_pipeline
        train_data_idx = {[str(int(ind)) for ind in dataset_idx]}
        [OPTIONAL]
        """.encode('utf-8')