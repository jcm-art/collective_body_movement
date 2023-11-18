# Collective Body Movement Application
# Director: Sarah Silverblatt-Buser (https://www.sarahsilverblatt.com/)
# Author: Justin Martin (jcm-art)

from typing import Dict, List
import numpy as np
import pandas as pd
from ..utils import CollectiveBodyBolt


# TODO - make generic class with inheritance
class MetricCalculator:

    def __init__(
            self,algorithm_name: str = None):
        self.algorithm_name = algorithm_name

        self.jump_dict_pd = {
            'mean': pd.Series.mean,
            'max': pd.Series.max,
            'min': pd.Series.min,
            'sum': pd.Series.sum,
            'std': pd.Series.std,
        }

        self.jump_dict_np = {
            'mean': np.mean,
            'max': np.max,
            'min': np.min,
            'sum': np.sum,
            'std': np.std,
        }

        self.metric_dict = {
            'dataset_id': [],
            'mean': [],
            'max': [],
            'min': [],
            'sum': [],
            'std': [],
        }

        self.meta_metric_dict = {
            'mean': None,
            'max': None,
            'min': None,
            'sum': None,
            'std': None,
        }

    def calculate_metrics(
            self,
            dataset_id: int,
            series: pd.Series,
            command_list: List[str] = [
                'mean','max','min','sum','std']
    ):
        self.metric_dict['dataset_id'].append(dataset_id)
        for command in command_list:
            metric_result = self.jump_dict_pd[command](series)
            self.metric_dict[command].append(metric_result)
        return self.metric_dict

    def calculate_meta_metrics(
            self,
            np_array: np.array,
            command_list: List[str] = [
                'mean','max','min','sum','std']
    ):
        for command in command_list:
            metric_result = self.jump_dict_np[command](np_array)
            self.meta_metric_dict[command]=metric_result
        return self.meta_metric_dict

    def get_metric_dict(self):
        return self.metric_dict
    
    def get_meta_metric_dict(self):
        return self.meta_metric_dict
    
    def get_algorithm_name(self):
        return self.algorithm_name
    

class MetricsBolt(CollectiveBodyBolt):

    def __init__(self, output_directory_path: str, save_intermediate_output: bool=False) -> None:
        super().__init__(output_directory_path, save_intermediate_output)

    # TODO - port to parent class as optional method
    def process(
        self, 
        input_dataframe_list: List[pd.DataFrame], 
        aggregate_metadata: Dict,
        input_metadata_list: List[Dict]
     ) -> (List[pd.DataFrame], List[Dict]):
        
        self.output_df_list = input_dataframe_list
        self.aggregate_metadata_output = aggregate_metadata
        self.output_metadata_list = input_metadata_list

        self.output_df_list, self.output_metadata_list = self._process_all_datasets(
            self.output_df_list, self.output_metadata_list)

        if self.save_intermediate_output:
            self.save_output()
            
        return self.output_df_list, self.aggregate_metadata_output, self.output_metadata_list

    # TODO - port to parent class as optional method
    def _process_all_datasets(self, output_df_list, output_metadata_list):

        assert len(output_df_list) == len(output_metadata_list), "Missing matching df and metadata pairs"
        for i in range(len(output_df_list)):
            output_df = output_df_list[i]

            # Prepare metadata for parsing and addifions
            output_metadata = output_metadata_list[i]
            output_dataset_id = list(output_metadata.keys())[0]
            output_metadata = output_metadata[output_dataset_id]
            output_metadata["derived_kinematics_metadata"] = {}

            if output_metadata["cleaned_metadata"]["is_valid"]:
                output_df, output_metadata = self._calculate_metrics(output_dataset_id, output_df, output_metadata)

            else: 
                output_metadata["metrics_metadata"] = {
                    "error_flag": "invalid dataset, kinematics pipeline not run"
                }

            # Restore structure of output metdata
            output_metadata = {
                output_dataset_id: output_metadata
            }

            # Update the metadata list entries
            output_df_list[i] = output_df
            output_metadata_list[i] = output_metadata
        return output_df_list, output_metadata_list
    
    def _calculate_metrics(self, output_dataset_id: int, output_df: pd.DataFrame, output_metadata: Dict):
        # TODO - build list of algorithms to use for final metrics per dataset
        output_metadata["metrics_metadata"] = {}
        output_metadata["metrics"] = {}
        output_metadata["basic_data_metrics"] = {}
        
        # Generate metrics for basic data
        # TODO - replace by aggregated metadata with column list to prevent variation and recalling
        # TODO - remove hardcoded column names
        algorithm_names = ["total_cartesian_distance","total_rotational_distance","linear_kinetic_energy","linear_power","rotational_inertia","rotational_kinetic_energy"]
        algo_set = set(algorithm_names)
        all_cols_set = set(output_df.columns)
        basic_columns = list(all_cols_set-algo_set)

        output_metadata = self._basic_data_metrics(output_dataset_id, output_df, output_metadata, basic_columns)

        # Divide algorithms by chapter (if required)
        output_df, output_metadata = self._divide_algorithm_by_chapter(output_df, output_metadata, "total_cartesian_distance")
        
        # Calculate Metrics from algorithms
        # TODO - move to process all datasets
        # TODO - rework for autogeneration
        
        for algorithm in algorithm_names:
            total_dist_metric = MetricCalculator(algorithm)
            total_dist_metric.calculate_metrics(output_dataset_id, output_df[algorithm])        
            output_metadata["metrics"][total_dist_metric.get_algorithm_name()] = total_dist_metric.get_metric_dict()

            # TODO - add a metrics by chapter function and separate out in metadata structure

        return output_df, output_metadata

    def _basic_data_metrics(
            self, 
            output_dataset_id: int,
            output_df: pd.DataFrame, 
            output_metadata: Dict, 
            basic_columns: List[str]
     ) -> Dict:

        for column in basic_columns:

            # TODO - remove hardcoded fix to skip time (check for numeric)
            if column!="time":
                total_dist_metric = MetricCalculator(column)
                total_dist_metric.calculate_metrics(output_dataset_id, output_df[column])

                # TODO - rework for autogeneration
                output_metadata["basic_data_metrics"][total_dist_metric.get_algorithm_name()] = total_dist_metric.get_metric_dict()

        return output_metadata

    def _divide_algorithm_by_chapter(self, output_df: pd.DataFrame, output_metadata: Dict, algorithm_name: str):
            new_algorithm_name = f"{algorithm_name}_by_chapter"

            # Modify cumsum to track by chapter
            chapter1_max = output_df[output_df["chapitre"]==1][algorithm_name].max()
            chapter2_max = output_df[output_df["chapitre"]==2][algorithm_name].max()
            chapter3_max = output_df[output_df["chapitre"]==3][algorithm_name].max()

            # Normalize by chapter
            output_df[new_algorithm_name] = output_df['total_cartesian_distance']
            output_df[new_algorithm_name] = output_df[output_df['chapitre']==2][algorithm_name]-chapter1_max
            output_df[new_algorithm_name] = output_df[output_df['chapitre']==3][algorithm_name]-chapter2_max
            output_df[new_algorithm_name] = output_df[output_df['chapitre']==4][algorithm_name]-chapter3_max

            return output_df, output_metadata