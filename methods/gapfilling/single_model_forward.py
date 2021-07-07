import os
import pandas as pd
import numpy as np
from fedot.core.chains.node import PrimaryNode
from fedot.core.chains.ts_chain import TsForecastingChain
from methods.validation_and_metrics import *

from pylab import rcParams
rcParams['figure.figsize'] = 18, 7

from fedot.utilities.ts_gapfilling import ModelGapFiller


def run_fedot_ridge(folder_to_save, files_list,
                    columns_with_gap, file_with_results,
                    vis = False):
    """
    The function starts the algorithm of gap-filling

    :param folder_to_save: where to save csv files with filled gaps
    :param files_list: list with file name, which will be processed
    :param columns_with_gap: list with names of columns with gaps
    :param file_with_results: file with final report with metrics
    :param vis: is there a need to make visualisations
    """

    # Create folder if it doesnt exists
    if os.path.isdir(folder_to_save) == False:
        os.makedirs(folder_to_save)

    mapes = []
    for file_id, file in enumerate(files_list):
        data = pd.read_csv(os.path.join('..', 'data', file))
        data['Date'] = pd.to_datetime(data['Date'])
        dataframe = data.copy()

        # Creating the dataframe
        mini_dataframe = pd.DataFrame({'File': [file]*6,
                                       'Metric': ['MAE', 'RMSE', 'MedAE',
                                                  'MAPE', 'Min gap value',
                                                  'Max gap value']})

        # For every gap series
        for column_with_gap in columns_with_gap:
            print(f'File - {file}, column with gaps - {column_with_gap}')
            array_with_gaps = np.array(data[column_with_gap])

            # Gap-filling algorithm
            ridge_chain = TsForecastingChain(PrimaryNode('ridge'))
            gapfiller = ModelGapFiller(gap_value=-100.0,
                                       chain=ridge_chain,
                                       max_window_size=30)
            withoutgap_arr = gapfiller.forward_filling(array_with_gaps)

            # Impute time series with new one
            dataframe[column_with_gap] = withoutgap_arr
            min_val, max_val, mae, rmse, medianae, mape = validate(parameter='Height',
                                                                   mask=column_with_gap,
                                                                   data=data,
                                                                   withoutgap_arr=withoutgap_arr,
                                                                   vis=vis)

            mini_dataframe[column_with_gap] = [mae, rmse, medianae, mape, min_val, max_val]
            mapes.append(mape)

            # Save resulting file
            save_path = os.path.join(folder_to_save, file)
            dataframe.to_csv(save_path)

        print(mini_dataframe)
        print('\n')

        if file_id == 0:
            main_dataframe = mini_dataframe
        else:
            frames = [main_dataframe, mini_dataframe]
            main_dataframe = pd.concat(frames)

    mapes = np.array(mapes)
    print(f'Mean MAPE value - {np.mean(mapes):.4f}')

    path_to_save = os.path.dirname(os.path.abspath(file_with_results))
    if os.path.isdir(path_to_save) == False:
        os.makedirs(path_to_save)
    main_dataframe.to_csv(file_with_results, index=False)

# Run the single-model chain example
folder_to_save = '../data/fedot_ridge'
files_list = ['Synthetic.csv', 'Sea_hour.csv', 'Sea_10_240.csv', 'Temperature.csv', 'Traffic.csv', 'microsoft_stock.csv']
columns_with_gap = ['gap', 'gap_center']
file_with_results = '../data/reports/fedot_ridge_report.csv'

if __name__ == '__main__':
    run_fedot_ridge(folder_to_save, files_list,
                    columns_with_gap, file_with_results, vis=False)